from django.contrib.auth.models import User
from tastypie.test import ResourceTestCase
from one_goose.api import UserResource


class UserResourceTest(ResourceTestCase):

    fixtures = ['users.json']

    def setUp(self):
        super(UserResourceTest, self).setUp()

        #create an extra pair of user because salted password are hard
        self.username = 'test0r'
        self.password = 'pass'
        self.user = User.objects.create_user(self.username, 'test0r@example.com', self.password)

        self.username_2 = 'test0r2'
        self.password_2 = 'pass'
        self.user_2 = User.objects.create_user(self.username_2, 'test0r2@example.com', self.password_2)

        self.user_url = '/api/v1/user/{0}/'.format(self.user.pk)
        self.user_url_2 = '/api/v1/user/{0}/'.format(self.user_2.pk)
        self.list_url = '/api/v1/user/'

        self.patch_data = {
            "password": "asdfhdsaudhas",
             "first_name": "asdf",
             "last_name": "wat"
        }

        self.maxDiff = None




    def get_credentials(self):
        return self.create_basic(username=self.username, password=self.password)

    def get_credentials_2(self):
        return self.create_basic(username=self.username_2, password=self.password_2)

    def test_get_list(self):
        resp = self.api_client.get(self.list_url, format='json')

        self.assertValidJSONResponse(resp)

        # 3 users in fixture
        self.assertEqual(len(self.deserialize(resp)['objects']), 5)

        # my first test user
        self.assertKeys(self.deserialize(resp)['objects'][0], ['date_joined', 'id', 'first_name', 'last_name', 'username', 'resource_uri', 'last_login'])
        self.assertEqual(self.deserialize(resp)['objects'][0]['username'], 'caffodian')


    def test_get_detail(self):
        # should work with no auth
        resp = self.api_client.get(self.user_url, format='json')

        self.assertValidJSONResponse(resp)

        # We use ``assertKeys`` here to just verify the keys, not all the data.
        self.assertKeys(self.deserialize(resp), ['date_joined', 'id', 'first_name', 'last_name', 'username', 'resource_uri', 'last_login'])

        self.assertEqual(self.deserialize(resp)['username'], self.username)


    def test_put_unauthorized(self):
        # no auth
        resp = self.api_client.put(self.user_url, format='json', data={"first_name": "asdf"})
        self.assertHttpUnauthorized(resp)

        # wrong user auth
        resp_2 = self.api_client.put(self.user_url, format='json', data=self.patch_data, authentication=self.get_credentials_2())
        self.assertHttpUnauthorized(resp_2)

    def test_put(self):
        # auth as owner
        resp = self.api_client.put(self.user_url, format='json', data=self.patch_data, authentication=self.get_credentials())
        self.assertHttpAccepted(resp)

    def test_delete_not_allowed(self):
        #should not delete even if you are the user
        resp = self.api_client.delete(self.user_url, format='json', authentication=self.get_credentials())
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

    def test_post_user_dupe_username(self):
        resp = self.api_client.post(self.list_url, format='json', data={
            'username': self.username,
            'password': 'asdffasdasdsa'
        })
        self.assertHttpBadRequest(resp)



