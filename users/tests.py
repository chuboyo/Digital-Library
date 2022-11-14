""" code to check if a new ordinary user and a new superuser can be created"""
from django.test import TestCase

from django.contrib.auth import get_user_model

class customUserTests(TestCase):
     def test_create_user(self):
         User = get_user_model()
         newUser = User.objects.create_user(
             email='badman@gmail.com',
             username='badman',
             password='password'
         )
         self.assertEquals(newUser.email, 'badman@gmail.com')
         self.assertEquals(newUser.username, 'badman')
         self.assertTrue(newUser.is_active)
         self.assertFalse(newUser.is_staff)
         self.assertFalse(newUser.is_superuser)


     def test_create_superuser(self):
         superUser = get_user_model()
         newSuperUser = superUser.objects.create_superuser(
             email='super@gmail.com',
             username='superman',
             password='superpass'
         )
         self.assertEquals(newSuperUser.email, 'super@gmail.com')
         self.assertEquals(newSuperUser.username, 'superman')
         self.assertTrue(newSuperUser.is_active)
         self.assertTrue(newSuperUser.is_staff)
         self.assertTrue(newSuperUser.is_superuser)
