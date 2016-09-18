#!/usr/bin/env python

import os

from celery.decorators import task
from celery.utils.log import get_task_logger

from gemdeps import GemDeps

logger = get_task_logger(__name__)


@task
def get_status(path, appname, version):
    core = GemDeps(appname)
    gemfile_path = os.path.join(path, 'Gemfile')
    core.process(gemfile_path)
    core.write_output(path)
    core.generate_dot(path)
    return True
