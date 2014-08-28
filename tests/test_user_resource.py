from django.contrib.auth.models import User
from tastypie.test import ResourceTestCase
from one_goose.api import UserResource


class UserResourceTest(ResourceTestCase):

    fixtures = ['users.json']

    def setUp(self):
        super(UserResourceTest, self).setUp()

        # grab first fixture user (for edits etc)
        self.user_1 = User.objects.get(id=1)
        self.user_2 = User.objects.get(id=2)

        self.user_url = '/api/v1/user/{0}/'.format(self.user_1.pk)
        self.list_url = '/api/v1/user/'

        self.patch_data = {
            "password": "asdfhdsaudhas",
             "first_name": "asdf",
             "last_name": "wat"
        }

        self.maxDiff = None


    def get_credentials(self):
        return self.create_basic(username=self.user_1.username, password=self.user_1.password)

    def get_credentials_2(self):
        return self.create_basic(username=self.user_2.username, password=self.user_2.password)

    def test_get_list(self):
        resp = self.api_client.get(self.list_url, format='json')

        self.assertValidJSONResponse(resp)

        # 3 users in fixture
        self.assertEqual(len(self.deserialize(resp)['objects']), 3)

        # my first test user
        self.assertKeys(self.deserialize(resp)['objects'][0], ['date_joined', 'id', 'first_name', 'last_name', 'username', 'resource_uri', 'last_login'])
        self.assertEqual(self.deserialize(resp)['objects'][0]['username'], 'caffodian')


    def test_get_detail(self):
        # should work with no auth
        resp = self.api_client.get(self.user_url, format='json')

        self.assertValidJSONResponse(resp)

        # We use ``assertKeys`` here to just verify the keys, not all the data.
        self.assertKeys(self.deserialize(resp), ['date_joined', 'id', 'first_name', 'last_name', 'username', 'resource_uri', 'last_login'])

        self.assertEqual(self.deserialize(resp)['username'], 'caffodian')


    def test_patch_unauthorized(self):
        # no auth
        resp = self.api_client.patch(self.user_url, format='json', data={"first_name": "asdf"})
        self.assertHttpUnauthorized(resp)

        # wrong user auth
        resp_2 = self.api_client.patch(self.user_url, format='json', data={"first_name": "asdf"}, authentication=self.get_credentials_2)
        self.assertHttpUnauthorized(resp_2)

    def test_delete_not_allowed(self):
        resp = self.api_client.delete(self.user_url, format='json', authentication=self.get_credentials)

        self.assertHttpUnauthorized(resp)

    def test_post_user(self):
        username = 'asdjfhfhuf'
        password = 'qqqqqq'

        resp = self.api_client.post(self.list_url, format='json', data={
            'username': username,
            'password': password
        })

        self.assertHttpCreated(resp)

        # TODO look more into last() to confirm it's to my understanding that it always is last inserted
        user = User.objects.last()
        self.assertEquals(user.username, username)



