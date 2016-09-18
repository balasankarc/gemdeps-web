#!/usr/bin/env python

import os


def get_available_apps():
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
