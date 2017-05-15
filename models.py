from __future__ import unicode_literals
from datetime import datetime

import django
from django.db import models
from model_utils.models import TimeStampedModel


class Schedule(TimeStampedModel):
    """
    A model to hold any relation from a subject to other subjects
    """
    session = models.ForeignKey(Session)
    date_and_time = models.DateTimeField(blank=True, null=True)
    series = models.CharField(blank=True, null=True, max_length=200)
    date_year = models.CharField(blank=True, null=True, max_length=200)
