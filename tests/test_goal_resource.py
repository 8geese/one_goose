from django.contrib.auth.models import User
from one_goose.models import Goal
from tastypie.test import ResourceTestCase
from one_goose.api import GoalResource


class GoalResourceTest(ResourceTestCase):
    fixtures = ['goals.json', 'users.json']

    def setUp(self):
        super(GoalResourceTest, self).setUp()

        # create an extra pair of user because salted password are hard
        self.username = 'test0r'
        self.password = 'pass'
        self.user = User.objects.create_user(self.username, 'test0r@example.com', self.password)

        self.username_2 = 'test0r2zzz'
        self.password_2 = 'passzz'
        self.user_2 = User.objects.create_user(self.username_2, 'test0r2@example.com', self.password_2)

        self.test_item = Goal(**{
            "name": "test",
            "description": "do bad things to this later",
            "creator": self.user
        })

        self.put_data = {
            "description": "newer description"
        }

        self.test_item.save()

        self.user_url = '/api/v1/user/{0}/'.format(self.user.pk)
        self.user_url_2 = '/api/v1/user/{0}/'.format(self.user_2.pk)

        self.list_url = '/api/v1/goal/'
        self.item_url = '/api/v1/goal/{0}/'


    def get_credentials(self):
        return self.create_basic(username=self.username, password=self.password)


    def get_other_credentials(self):
        return self.create_basic(username=self.username_2, password=self.password_2)

    """
    random people not in the org probably shouldn't see your goals
    """

    def test_get_list_no_auth(self):
        resp = self.api_client.get(self.list_url, format='json')
        self.assertHttpUnauthorized(resp)


    def test_get_list(self):
        resp = self.api_client.get(self.list_url, format='json', authentication=self.get_credentials())

        self.assertValidJSONResponse(resp)

        # fixture has 8, +1 for the one we use for testing edits and delete
        self.assertEqual(len(self.deserialize(resp)['objects']), 9)


    def test_get_detail(self):
        resp = self.api_client.get(self.item_url.format(1), format='json', authentication=self.get_credentials())

        self.assertValidJSONResponse(resp)

        deserialized = self.deserialize(resp)
        self.assertKeys(deserialized, ['created', 'creator', 'description', 'id', 'modified', 'name', 'resource_uri'])
        self.assertEquals(deserialized['resource_uri'], self.item_url.format(1))
        self.assertEquals(deserialized['id'], 1)


    def test_non_auth_put(self):
        resp = self.api_client.put(self.item_url.format(self.test_item.id), format='json',
                                   authentication=self.get_other_credentials(), data=self.put_data)
        self.assertHttpUnauthorized(resp)
        self.assertEquals(Goal.objects.get(pk=self.test_item.id).description, self.test_item.description)


    def test_put(self):
        resp = self.api_client.put(self.item_url.format(self.test_item.id), format='json',
                                   authentication=self.get_credentials(), data=self.put_data)

        self.assertHttpAccepted(resp)
        self.assertEquals(Goal.objects.get(pk=self.test_item.id).description, self.put_data['description'])


    def test_post(self):
        resp = self.api_client.post(self.list_url, format='json', authentication=self.get_credentials(), data={
            'name': "testname",
            'description': "thisisatest"
        })

        self.assertHttpCreated(resp)
        goal = Goal.objects.last()
        self.assertEquals(goal.name, "testname")
        self.assertEquals(goal.description, "thisisatest")
        self.assertEquals(goal.creator, self.user)


    def test_non_auth_delete(self):
        count = Goal.objects.count()
        resp = self.api_client.delete(self.item_url.format(self.test_item.id), format='json',
                                   authentication=self.get_other_credentials())

        self.assertHttpUnauthorized(resp)
        self.assertEquals(Goal.objects.count(), count)


    def test_delete(self):
        count = Goal.objects.count()
        resp = self.api_client.delete(self.item_url.format(self.test_item.id), format='json',
                                   authentication=self.get_credentials())


        self.assertHttpAccepted(resp)
        self.assertEquals(Goal.objects.count(), (count-1))




