from django.conf.urls import patterns, include, url
from tastypie.api import Api
from django.contrib import admin

from .api import GoalResource, UserResource, CheckinResource


admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(GoalResource())
v1_api.register(CheckinResource())
v1_api.register(UserResource())

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(v1_api.urls)),
)
