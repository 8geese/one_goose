from django.contrib.auth.models import User
from one_goose.models import Goal, Checkin
from tastypie.test import ResourceTestCase
from one_goose.api import GoalResource, CheckinResource


class CheckinResourceTest(ResourceTestCase):
    fixtures = ['goals.json', 'users.json']

    def setUp(self):
        super(CheckinResourceTest, self).setUp()

        # create an extra pair of user because salted password are hard
        self.username = 'test0r'
        self.password = 'pass'
        self.user = User.objects.create_user(self.username, 'test0r@example.com', self.password)

        self.username_2 = 'test0r2zzz'
        self.password_2 = 'passzz'
        self.user_2 = User.objects.create_user(self.username_2, 'test0r2@example.com', self.password_2)

        self.test_goal = Goal(**{
            "name": "test",
            "description": "do bad things to this later",
            "creator": self.user
        })

        self.test_goal.save()

        self.test_checkin = Checkin(**{
            "message": "good job today",
            "creator": self.user,
            "goal": self.test_goal
        })

        self.test_checkin.save()

        self.put_data = {
            'message': "new message"
        }

        self.user_url = '/api/v1/user/{0}/'.format(self.user.pk)
        self.user_url_2 = '/api/v1/user/{0}/'.format(self.user_2.pk)

        self.goal_list_url = '/api/v1/goal/'
        self.goal_url = '/api/v1/goal/{0}/'

        self.list_url = '/api/v1/checkin/'
        self.item_url = '/api/v1/checkin/{0}/'


    def get_credentials(self):
        return self.create_basic(username=self.username, password=self.password)


    def get_other_credentials(self):
        return self.create_basic(username=self.username_2, password=self.password_2)


    def test_get_list_no_auth(self):
        """
        random people not in the org probably shouldn't see your goals
        """
        resp = self.api_client.get(self.list_url, format='json')
        self.assertHttpUnauthorized(resp)


    def test_get_list(self):
        resp = self.api_client.get(self.list_url, format='json', authentication=self.get_credentials())

        self.assertValidJSONResponse(resp)

        # only bothered setting up 1
        self.assertEqual(len(self.deserialize(resp)['objects']), 1)


    def test_get_detail(self):
        resp = self.api_client.get(self.item_url.format(1), format='json', authentication=self.get_credentials())

        self.assertValidJSONResponse(resp)

        deserialized = self.deserialize(resp)
        self.assertKeys(deserialized, ['created', 'creator', 'goal', 'id','message', 'modified', 'resource_uri'])
        self.assertEquals(deserialized['resource_uri'], self.item_url.format(1))
        self.assertEquals(deserialized['id'], 1)


    def test_non_auth_patch(self):
        resp = self.api_client.patch(self.item_url.format(self.test_checkin.id), format='json',
                                   authentication=self.get_other_credentials(), data=self.put_data)
        self.assertHttpUnauthorized(resp)
        self.assertEquals(Checkin.objects.get(pk=self.test_checkin.id).message, self.test_checkin.message)


    def test_patch(self):
        resp = self.api_client.patch(self.item_url.format(self.test_checkin.id), format='json',
                                   authentication=self.get_credentials(), data=self.put_data)

        self.assertHttpAccepted(resp)
        self.assertEquals(Checkin.objects.get(pk=self.test_checkin.id).message, self.put_data['message'])


    def test_post(self):
        resp = self.api_client.post(self.list_url, format='json', authentication=self.get_credentials(), data={
            "name": "testname",
            "message": "thisisatest",
            "goal": self.goal_url.format(self.test_goal.id)
        })


        self.assertHttpCreated(resp)
        checkin = Checkin.objects.last()
        self.assertEquals(checkin.goal, self.test_goal)
        self.assertEquals(checkin.message, "thisisatest")
        self.assertEquals(checkin.creator, self.user)


    def test_non_auth_delete(self):
        count = Checkin.objects.count()
        resp = self.api_client.delete(self.item_url.format(self.test_checkin.id), format='json',
                                   authentication=self.get_other_credentials())

        self.assertHttpUnauthorized(resp)
        self.assertEquals(Checkin.objects.count(), count)


    def test_delete(self):
        count = Checkin.objects.count()
        resp = self.api_client.delete(self.item_url.format(self.test_checkin.id), format='json',
                                   authentication=self.get_credentials())


        self.assertHttpAccepted(resp)
        self.assertEquals(Checkin.objects.count(), (count-1))




