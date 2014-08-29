from django.db import IntegrityError
from tastypie.exceptions import BadRequest, Unauthorized
from tastypie.resources import ModelResource
from django.contrib.auth.models import User
from tastypie.validation import CleanedDataFormValidation
from django.contrib.auth.forms import UserChangeForm
from tastypie import fields
from tastypie.serializers import Serializer
from tastypie.authentication import BasicAuthentication, MultiAuthentication, Authentication

from one_goose.models import Goal, Checkin
from .forms import GoalForm, CheckinForm
from .validation import ModelFormValidation, uri_to_pk
from .authorization import CreatorWriteOnlyAuthorization, UserMatchWriteOnlyAuthorization


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser']
        # the fall-through for authentication needs to go last or it will match you as an AnonymousUser and give up
        authentication = MultiAuthentication(BasicAuthentication(), Authentication())
        allowed_methods = ['get', 'post', 'patch']
        validation = CleanedDataFormValidation(form_class=UserChangeForm)
        authorization = UserMatchWriteOnlyAuthorization()

    def obj_create(self, bundle, **kwargs):
        try:
            # tried doing this with calling super.obj_create and then calling set_password, but it never seemed to
            # set the password correctly.  WTF.  probably not a good use of time to investigate
            user = User.objects.create_user(bundle.data.get('username'), bundle.data.get('email', ''),
                                            bundle.data.get('password'))
            bundle.obj = user
        except IntegrityError:
            raise BadRequest('That username already exists')
        return bundle


class GoalResource(ModelResource):
    creator = fields.ForeignKey(UserResource, 'creator')

    class Meta:
        queryset = Goal.objects.all()
        allowed_methods = ['get', 'post', 'patch', 'delete']
        resource_name = 'goal'
        serializer = Serializer()
        authorization = CreatorWriteOnlyAuthorization()
        authentication = MultiAuthentication(BasicAuthentication())
        validation = CleanedDataFormValidation(form_class=GoalForm)

    def obj_create(self, bundle, **kwargs):
        # okay, finally found the pre create hook.  :(

        return super(GoalResource, self).obj_create(bundle, creator=bundle.request.user)


class CheckinResource(ModelResource):
    creator = fields.ForeignKey(UserResource, 'creator')
    goal = fields.ForeignKey(GoalResource, 'goal')

    class Meta:
        queryset = Checkin.objects.all()
        allowed_methods = ['get', 'post', 'patch', 'delete']
        resource_name = 'checkin'
        serializer = Serializer()
        authorization = CreatorWriteOnlyAuthorization()
        authentication = MultiAuthentication(BasicAuthentication())

        @property
        def validation(self):
            return ModelFormValidation(form_class=CheckinForm, resource=CheckinResource)

    def obj_create(self, bundle, **kwargs):
        # this is ridiculous, i must be misunderstanding something, unless it has something to do with the weird hacks
        # to validate

        if bundle.data.get('goal'):
            parent = Goal.objects.get(pk=uri_to_pk(bundle.data['goal']))

            if parent.creator != bundle.request.user:
                raise Unauthorized("You're checking in to a goal you don't own")
        else:
            parent = bundle.obj.goal

        return super(CheckinResource, self).obj_create(bundle, creator=bundle.request.user, goal=parent)

    def obj_update(self, bundle, **kwargs):
        # bump off the id from kwargs so this doesn't call create.  very confuse.
        try:
            bundle.data['pk'] = kwargs.get('pk')
        except:
            raise BadRequest("cant get id somehow")

        return super(CheckinResource, self).obj_update(bundle, **kwargs)