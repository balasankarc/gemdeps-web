#!/usr/bin/env python

import os


def get_available_apps():
    APP_PATH = os.path.dirname(os.path.dirname(os.path.abspath(
        __file__)))
    RESOURCE_PATH = os.path.join(APP_PATH, 'webgemdeps', 'resources')
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
            name, version = os.path.basename(directory).split(
                '_')
            apps.append({'name': name, 'version': version})
    return apps
