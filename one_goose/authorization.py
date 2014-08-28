from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized

"""
Authorization which only allows creator to make write ops, but all reads are public
reference: http://django-tastypie.readthedocs.org/en/latest/authorization.html
"""


class CreatorWriteOnlyAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        # all goals and check-ins are public
        return object_list

    def read_detail(self, object_list, bundle):
        # all
        return True

    def create_list(self, object_list, bundle):
        # Assuming they're auto-assigned to ``user``.
        return object_list

    def create_detail(self, object_list, bundle):
        return bundle.obj.creator == bundle.request.user

    def update_list(self, object_list, bundle):
        allowed = [obj for obj in object_list if obj.creator == bundle.request.user]

        return allowed

    def update_detail(self, object_list, bundle):
        return bundle.obj.creator == bundle.request.user

    def delete_list(self, object_list, bundle):
        return bundle.obj.creator == bundle.request.user

    def delete_detail(self, object_list, bundle):
        return bundle.obj.creator == bundle.request.user


class UserMatchWriteOnlyAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        # all users are public
        return object_list

    def read_detail(self, object_list, bundle):
        # all
        return True

    def create_list(self, object_list, bundle):
        return object_list

    def create_detail(self, object_list, bundle):

        return bundle.obj.id == bundle.request.user.id

    def update_list(self, object_list, bundle):
        # don't allow batch edits ...(this is batch edits right? :x)
        raise Unauthorized("Sorry, no batch edits.")

    def update_detail(self, object_list, bundle):

        return bundle.obj.id == bundle.request.user.id

    def delete_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")