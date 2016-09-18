#!/usr/bin/env python

from django.contrib.auth import authenticate
from django.contrib import messages
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.shortcuts import render

from webgemdeps.models import User
from webgemdeps.forms import SignInForm, NewStatusForm
from webgemdeps.utils import get_available_apps, get_resource_path, get_status

import os


class StatusCreate(View):
    """
    Handle creation of new status bar.
    """

    def post(self, request):
        print "\n\n\n\n\n\n"
        print request
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
                with open(os.path.join(folder, 'Gemfile'), 'w') as gemfile:
                    gemfile.write(gemfile_content)
                with open(os.path.join(folder, 'Gemfile.lock'), 'w') as gemfilelock:
                    gemfilelock.write(gemfile_lock_content)
                result = get_status.delay(folder, clean_name, input_version)
                print result.id
            else:
                raise Exception
        except Exception as e:
            print Exception, e
            messages.error(request, "Something went wrong.")
            return HttpResponseRedirect('/')
        messages.success(request, "Added successfully.")
        return HttpResponseRedirect('/')
