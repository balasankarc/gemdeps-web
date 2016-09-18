#!/usr/bin/env python

import os

from celery.decorators import task
from celery.utils.log import get_task_logger
from gemdeps import GemDeps
from webgemdeps.models import Job

logger = get_task_logger(__name__)


def get_available_apps():
    completed_apps = []
    pending_apps = []
    for job in Job.objects.all():
        celery_result = get_status.AsyncResult(str(job.job_id))
        print celery_result.status
        position = job.appname.index('-')
        name = job.appname[:position]
        version = job.appname[position + 1:]
        if celery_result.status == 'SUCCESS':
            completed_apps.append(
                {'appname': job.appname, 'name': name, 'version': version})
        elif celery_result.status == 'PENDING':
            completed_apps.append(
                {'appname': job.appname, 'name': name, 'version': version})
    return completed_apps, pending_apps


def get_available_apps2():
    RESOURCE_PATH = get_resource_path()
    print RESOURCE_PATH
    directories = [os.path.join(RESOURCE_PATH, x) for x in
                   os.listdir(RESOURCE_PATH) if
                   os.path.isdir(RESOURCE_PATH + '/' + x)]
    apps = []
    for directory in directories:
        gemfile_lock_path = os.path.join(directory, 'Gemfile.lock')
        deb_status_path = os.path.join(directory, 'debian_status.json')
        if os.path.isfile(gemfile_lock_path) and \
                os.path.isfile(deb_status_path):
            basename = os.path.basename(directory)
            position = basename.index('-')
            name = basename[:position]
            version = basename[position + 1:]
            apps.append({'name': name, 'version': version})
    return apps


def get_resource_path():
    APP_PATH = os.path.dirname(os.path.dirname(os.path.abspath(
        __file__)))
    RESOURCE_PATH = os.path.join(APP_PATH, 'webgemdeps', 'resources')
    return RESOURCE_PATH


@task
def get_status(path, appname, version):
    core = GemDeps(appname)
    gemfile_path = os.path.join(path, 'Gemfile')
    core.process(gemfile_path)
    core.write_output(path)
    core.generate_dot(path)
    return True
