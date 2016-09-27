#!/usr/bin/env python

import json
import os
import re
import shutil
import time
from distutils.version import LooseVersion

from django.contrib import messages
from django.contrib.auth import authenticate
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseForbidden)
from django.shortcuts import render
from django.views.generic import View

from webgemdeps.forms import NewStatusForm, SignInForm
from webgemdeps.models import Job, User
from webgemdeps.utils import get_available_apps, get_resource_path, get_status


class StatusCreate(View):
    """
    Handle creation of new status bar.
    """

    def post(self, request):
        if not request.user.is_authenticated():
            return HttpResponseForbidden('User not authenticated')
        form = NewStatusForm(request.POST, request.FILES)
        try:
            if form.is_valid():
                input_appname = form.cleaned_data['appname']
                input_version = form.cleaned_data['version']
                input_gemfile = request.FILES['gemfile']
                input_gemfile_lock = request.FILES['gemfilelock']
                gemfile_content = input_gemfile.read()
                gemfile_lock_content = input_gemfile_lock.read()
                RESOURCE_PATH = get_resource_path()
                clean_name = input_appname.replace("-", "_")
                folder_name = "%s-%s" % (clean_name, input_version)
                folder_name = folder_name.replace(" ", "_")
                folder = os.path.join(RESOURCE_PATH, folder_name)
                os.mkdir(folder)
                gemfile_path = os.path.join(folder, 'Gemfile')
                gemfile_lock_path = os.path.join(folder, 'Gemfile.lock')
                with open(gemfile_path, 'w') as gemfile:
                    gemfile.write(gemfile_content)
                with open(gemfile_lock_path, 'w') as gemfilelock:
                    gemfilelock.write(gemfile_lock_content)
                result = get_status.delay(folder, clean_name, input_version)
                job = Job(appname=folder_name)
                job.save()
                job.job_id = result.id
                job.save()
            else:
                raise Exception
        except Exception as e:
            print Exception, e
            messages.error(request, "Something went wrong.")
            return HttpResponseRedirect('/')
        messages.success(request, "Added successfully.")
        return HttpResponseRedirect('/')


def get_operator(requirement):
    '''
    Splits the operator and version from a requirement string.
    '''
    if requirement == '':
        return '>=', '0'
    m = re.search("\d", requirement)
    pos = m.start()
    if pos == 0:
        return '=', requirement
    check = requirement[:pos].strip()
    ver = requirement[pos:]
    return check, ver


def statusbase(appname):
    print "Appname is ", appname
    RESOURCE_PATH = get_resource_path()
    app_folder = os.path.join(RESOURCE_PATH, appname)
    ignore_list = ['fog-google', 'mini_portile2', 'newrelic_rpm',
                   'newrelic-grape', 'rb-fsevent', 'eco', 'eco-source',
                   'gitlab_meta', 'cause', 'rdoc', 'yard']
    try:

        listed_gems = []
        l = []
        filepath = os.path.join(app_folder, 'Gemfile.lock')
        gemfile_lock = open(filepath).readlines()
        for line in gemfile_lock:
            listed_gems.append(filter(None, line).strip().split(' ')[0])
        l = [gem for gem in listed_gems if not gem.isupper()]
        l = set(l)
    except Exception as e:
        print e
        pass

    filepath = os.path.join(app_folder, 'debian_status.json')
    inputfile = open(filepath)
    filecontent = inputfile.read()
    inputfile.close()
    updated_time = time.strftime(
        "%d/%m/%Y %H:%M:%S %Z", time.gmtime(os.path.getmtime(filepath)))
    deps = json.loads(filecontent)
    packaged_count = 0
    unpackaged_count = 0
    itp_count = 0
    total = 0
    mismatch = 0
    final_list = []
    for x, i in deps.items():
        if i['name'] in ignore_list:
            continue
        elif i['name'] not in l:
            print "Ignored ", i['name']
            continue
        else:
            final_list.append(i)
            if i['status'] == 'Packaged' or i['status'] == 'NEW':
                packaged_count += 1
            elif i['status'] == 'ITP':
                itp_count += 1
            else:
                unpackaged_count += 1
            if i['satisfied'] is False:
                mismatch += 1
    total = len(final_list)
    percent_complete = (packaged_count * 100) / total
    percent_incomplete = (packaged_count * 100) / total
    percent_itp = (itp_count * 100) / total
    return appname, final_list, packaged_count, unpackaged_count,\
        itp_count, mismatch, total, percent_complete, percent_incomplete,\
        percent_itp, updated_time


class StatusShow(View):
    """
    View packaging status of an app.
    """

    def get(self, request, appname):
        appname, final_list, packaged_count, unpackaged_count, itp_count, \
            mismatch, total, percent_complete, percent_incomplete,\
            percent_itp, updated_time = statusbase(appname)
        return render(request, 'status.html', {
            'appname': appname.title(),
            'deps': final_list,
            'packaged_count': packaged_count,
            'unpackaged_count': unpackaged_count,
            'itp_count': itp_count,
            'mismatch_count': mismatch,
            'total': total,
            'percent_complete': percent_complete,
            'percent_incomplete': percent_incomplete,
            'percent_itp': percent_itp,
            'updated_time': updated_time,
        })


class ToDoShow(View):
    """
    Return ToDo items as a Markdown list.
    """

    def get(self, request, appname):
        appname, final_list, packaged_count, unpackaged_count, itp_count, \
            mismatch, total, percent_complete, percent_incomplete,\
            percent_itp, updated_time = statusbase(appname)
        unpackaged = ""
        patch = ""
        minor_stable = ""
        minor_devel = ""
        major = ""
        already_newer = ""
        for item in final_list:
            if item['satisfied'] is False:
                if item['version'] == 'NA':
                    unpackaged += " - [ ] " + item['name'] + " | " +\
                        item['requirement'] + "<br />"
                else:
                    check, requirement_raw = get_operator(item['requirement'])
                    required = LooseVersion(requirement_raw)
                    version_raw = item['version'][:item['version'].index('-')]
                    if ":" in version_raw:
                        epoch_pos = version_raw.index(":")
                        version_raw = version_raw[epoch_pos + 1:]
                    version = LooseVersion(version_raw)
                    string_incomplete = " - [ ] %s | %s | %s <br />" % (
                        item['name'], item['requirement'], version_raw)
                    string_complete = " - [x] %s | %s | %s <br />" % (
                        item['name'], item['requirement'], version_raw)
                    if len(required.version) == len(version.version):
                        if len(required.version) == 3:
                            if required.version[0] > version.version[0]:
                                major += string_incomplete
                            elif required.version[0] < version.version[0]:
                                already_newer += string_complete
                            elif required.version[1] != version.version[1]:
                                if required.version[1] < version.version[1]:
                                    already_newer += string_complete
                                elif required.version[0] > 0:
                                    minor_stable += string_incomplete
                                else:
                                    minor_devel += string_incomplete
                            else:
                                if required.version[2] < version.version[2]:
                                    already_newer += string_complete
                                patch += string_incomplete
                        elif len(required.version) == 2:
                            if required.version[0] > version.version[0]:
                                major += string_incomplete
                            elif required.version[0] < version.version[0]:
                                already_newer += string_complete
                            elif required.version[1] != version.version[1]:
                                if required.version[1] < version.version[1]:
                                    already_newer += string_complete
                                elif required.version[0] > 0:
                                    minor_stable += string_incomplete
                                else:
                                    minor_devel += string_incomplete
                        elif len(required.version) == 1:
                            if required.version[0] > version.version[0]:
                                major += string_incomplete
                            elif required.version[0] < version.version[0]:
                                already_newer += string_complete
                    else:
                        min_length = min(len(required.version),
                                         len(version.version))
                        mismatch = 0
                        for position in range(min_length):
                            if required.version[position] != \
                                    version.version[position]:
                                mismatch = position
                                break
                        if mismatch == 0:
                            major += string_incomplete
                        elif mismatch == 1:
                            if required.version[0] > 0:
                                minor_stable += string_incomplete
                            else:
                                minor_devel += string_incomplete
                        elif mismatch == 2:
                            patch += string_incomplete
        output = ""
        if unpackaged != "":
            unpackaged = "**Unpackaged gems** <br />" + unpackaged
            output += "<br />" + unpackaged
        if patch != "":
            patch = "**Patch updates** <br />" + patch
            output += "<br />" + patch
        if minor_stable != "":
            minor_stable = "**Minor updates (Stable)** <br />" + minor_stable
            output += "<br />" + minor_stable
        if minor_devel != "":
            minor_devel = "**Minor updates (Development)** <br />" + \
                minor_devel
            output += "<br />" + minor_devel
        if major != "":
            major = "**Major updates** <br />" + major
            output += "<br />" + major
        if already_newer != "":
            already_newer = "**Already Newer** <br />" + already_newer
            output += "<br />" + already_newer
        return HttpResponse(output)


class StatusDelete(View):
    """
    Delete an existing statusbar.
    """

    def get(self, request, appname):
        if request.user.is_authenticated():
            try:
                job = Job.objects.get(appname=appname)
                job.delete()
                RESOURCE_PATH = get_resource_path()
                folder = os.path.join(RESOURCE_PATH, appname)
                print folder
                shutil.rmtree(folder)
            except Exception as e:
                print e, "qer"
                pass
        else:
            return HttpResponseForbidden()
        return HttpResponseRedirect('/')
