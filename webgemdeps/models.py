from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class Job(models.Model):
    appname = models.CharField(max_length=100)
    job_id = models.CharField(max_length=100)
