"""
Models for the one_goose project
"""

from django.db import models
from django.contrib.auth.models import User

class Goal(models.Model):
    name = models.CharField(max_length=140, blank=False, null=False)
    description = models.TextField(blank=True, default='')
    creator = models.ForeignKey('auth.User', related_name='goals')
    created = models.DateTimeField(editable=False, auto_now_add=True)
    modified = models.DateTimeField(editable=False, auto_now=True)

    def __unicode__(self):
        return self.name

class Checkin(models.Model):
    goal = models.ForeignKey('Goal', related_name='checkins', blank=False)
    modified = models.DateTimeField(editable=False, auto_now=True)
    message = models.CharField(max_length=140, null=False)
    creator = models.ForeignKey('auth.User', related_name='checkins', on_delete=models.CASCADE) # TODO check if the checkin creator is always the goal creator
    created = models.DateTimeField(editable=False, auto_now_add=True)

    def __unicode__(self):
        return self.message
