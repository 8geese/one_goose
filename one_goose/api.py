from tastypie.resources import ModelResource
from one_goose.models import Goal, Checkin
from django.contrib.auth.models import User
from tastypie import fields

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser']

class GoalResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')

    class Meta:
        queryset = Goal.objects.all()
        resource_name = 'goal'

class CheckinResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    goal = fields.ForeignKey(GoalResource, 'goal')

    class Meta:
        queryset = Checkin.objects.all()
        resource_name = 'checkin'