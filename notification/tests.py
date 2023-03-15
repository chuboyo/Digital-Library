from urllib import response
from django.test import TestCase
from django.contrib.auth import get_user_model
from notification.models import Notification
from django.urls import reverse, resolve
from datetime import datetime


# notification tests
class NotificationTest(TestCase):
    def setUp(self):
        self.regularuser = get_user_model().objects.create_user(
             email='regman@gmail.com',
             username='regman',
             password='password', 
             user_role='viewer'
        )

        self.user = get_user_model().objects.create_user(
             email='badman@gmail.com',
             username='badman',
             password='password', 
             is_custom_admin = True
        )

        self.superuser = get_user_model().objects.create_user(
             email='genuis@gmail.com',
             username='supergenius',
             password='password',
             is_superuser = True,
             is_custom_admin = True
        )

        self.notification = Notification.objects.create(
            notification_type=7,
            to_user=self.superuser,
            from_user=self.user
        )

    def test_string_representation(self):
        self.assertEqual(str(self.notification.notification_type), '7')


    def test_notification_list_view(self):
        self.client.login(username=self.superuser.username, password='password')
        response = self.client.get(reverse('all_notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notification/all_notifications.html')
        self.assertContains(response, self.notification.from_user.first_name)
        self.assertContains(response, self.notification.to_user.first_name)
        self.client.logout()