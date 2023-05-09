from urllib import response
from django.test import TestCase
from django.contrib.auth import get_user_model
from filesystem.models import PublicFiles, PublicFolders, PrivateFiles, PrivateFolders, SharedFiles, SharedFolders, SharedPrivateFiles, SharedPrivateFolders
from django.urls import reverse, resolve
from datetime import datetime
from django.core.files.uploadedfile import SimpleUploadedFile

# Public files/folder tests
class PublicFilesTest(TestCase):
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

        self.publicfolder = PublicFolders.objects.create(
            folder_name='test_folder',
            owner=self.user,
            permission_field='All',
            recycled=False
        )

        self.publicfile = PublicFiles.objects.create(
            filename=SimpleUploadedFile(
                "best_file_eva.txt",
                b"these are the file contents!"   # note the b in front of the string [bytes]
            ),
            owner=self.user,
            permission_field='All',
            folder=self.publicfolder,
            recycled=False
        )

        self.sharedfile = SharedFiles.objects.create(
            filename = self.publicfile,
            user = self.superuser,
            permission_field='All'
        )

        self.sharedfolder = SharedFolders.objects.create(
            folder_name = self.publicfolder,
            user = self.superuser,
            permission_field='All'
        )

    def test_string_representation(self):
        self.assertEqual(str(self.publicfolder.folder_name), 'test_folder')

    def test_absolute_url(self):
        self.assertEqual(self.publicfile.get_absolute_url(), f'/home/')

    def test_publicfile_list_view(self):
        self.client.login(username=self.superuser.username, password='password')
        response = self.client.get(reverse('file_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'filesystem/file_list.html')
        self.assertContains(response, self.publicfile.permission_field)
        self.client.logout()

    def test_publicfile_update_view(self):
        data = {
            'filename': SimpleUploadedFile(
                "best_file_eva.txt",
                b"these are the updated file contents!"   # note the b in front of the string [bytes]
            ),
            'owner': self.user.id,
            'folder': self.publicfolder,
            }

        self.client.login(username=self.superuser.username, password='password')
        response =  self.client.post(reverse('update_public_file', args=[self.publicfile.id]),  data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(PublicFiles.objects.filter(owner=self.user).exists())
        self.client.logout()


# Private files/folder tests
class PrivateFilesTest(TestCase):
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

        self.privatefolder = PrivateFolders.objects.create(
            folder_name='test_folder',
            owner=self.user,
            permission_field='All',
            recycled=False
        )

        self.privatefile = PrivateFiles.objects.create(
            filename=SimpleUploadedFile(
                "best_file_eva.txt",
                b"these are the file contents!"   # note the b in front of the string [bytes]
            ),
            owner=self.user,
            permission_field='All',
            folder=self.privatefolder,
            recycled=False
        )

        self.sharedprivatefile = SharedPrivateFiles.objects.create(
            filename = self.privatefile,
            user = self.superuser,
            permission_field='All'
        )

        self.sharedprivatefolder = SharedPrivateFolders.objects.create(
            folder_name = self.privatefolder,
            user = self.superuser,
            permission_field='All'
        )

    def test_string_representation(self):
        self.assertEqual(str(self.privatefolder.folder_name), 'test_folder')

    def test_absolute_url(self):
        self.assertEqual(self.privatefile.get_absolute_url(), f'/private_files/')

    def test_privatefile_list_view(self):
        self.client.login(username=self.superuser.username, password='password')
        response = self.client.get(reverse('private_file_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'filesystem/private_file_list.html')
        self.assertContains(response, self.privatefile.permission_field)
        self.client.logout()

    def test_privatefile_update_view(self):
        data = {
            'filename': SimpleUploadedFile(
                "best_file_eva.txt",
                b"these are the updated file contents!"   # note the b in front of the string [bytes]
            ),
            'owner': self.user.id,
            'folder': self.privatefolder,
            }

        self.client.login(username=self.superuser.username, password='password')
        response =  self.client.post(reverse('update_private_file', args=[self.privatefile.id]),  data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(PrivateFiles.objects.filter(owner=self.user).exists())
        self.client.logout()
    