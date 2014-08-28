"""
admin class for one_goose
"""

from django.contrib import admin

from .models import Goal, Checkin


admin.site.register(Goal)
admin.site.register(Checkin)