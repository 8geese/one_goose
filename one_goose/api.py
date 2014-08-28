from django.db import IntegrityError
from tastypie.exceptions import BadRequest
from tastypie.resources import ModelResource
from django.contrib.auth.models import User
from tastypie.validation import CleanedDataFormValidation
from django.contrib.auth.forms import UserChangeForm
from tastypie import fields
from tastypie.serializers import Serializer
from tastypie.authentication import BasicAuthentication, MultiAuthentication, SessionAuthentication, Authentication

from one_goose.models import Goal, Checkin
from .forms import GoalForm, CheckinForm
from .validation import ModelFormValidation
from .authorization import CreatorWriteOnlyAuthorization, UserMatchWriteOnlyAuthorization


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser']
        # the fall-through for authentication needs to go last or it will match you as an AnonymousUser and give up
        authentication = MultiAuthentication(BasicAuthentication(), SessionAuthentication(), Authentication())
        validation = CleanedDataFormValidation(form_class=UserChangeForm)
        authorization = UserMatchWriteOnlyAuthorization()

    def obj_create(self, bundle, **kwargs):
        try:
            bundle = super(UserResource, self).obj_create(bundle, **kwargs)
            bundle.obj.set_password(bundle.data.get('password'))
            bundle.obj.save()
        except IntegrityError:
            raise BadRequest('That username already exists')
        return bundle


class GoalResource(ModelResource):
    creator = fields.ForeignKey(UserResource, 'creator')

    class Meta:
        queryset = Goal.objects.all()
        resource_name = 'goal'
        serializer = Serializer()
        authorization = CreatorWriteOnlyAuthorization()
        authentication = MultiAuthentication(BasicAuthentication(), SessionAuthentication())
        validation = CleanedDataFormValidation(form_class=GoalForm)

    def hydrate(self, bundle, request=None):
        # auto set creator.  note to self, hydrate is kinda like a pre_save in DRF
        bundle.obj.creator = User.objects.get(pk=bundle.request.user.id)
        return bundle


class CheckinResource(ModelResource):
    creator = fields.ForeignKey(UserResource, 'creator')
    goal = fields.ForeignKey(GoalResource, 'goal')

    class Meta:
        queryset = Checkin.objects.all()
        resource_name = 'checkin'
        serializer = Serializer()
        authorization = CreatorWriteOnlyAuthorization()
        authentication = MultiAuthentication(BasicAuthentication(), SessionAuthentication())

        @property
        def validation(self):
            return ModelFormValidation(form_class=CheckinForm, resource=CheckinResource)

    def hydrate(self, bundle, request=None):
        # auto set creator
        bundle.obj.creator = User.objects.get(pk=bundle.request.user.id)
        return bundle