# import modules, classes and functions to build models
from django.db import models

from users.models import CustomUser
from django.contrib.auth import get_user_model
from django.urls import reverse
import uuid
from .storage import Storage
from django.utils import timezone
import os
# Create your models here.

# file/folder permission options
permissions = [
    ('View', 'View'),
    ('All', 'All'),
]

# options for announcements
announcement_groups = [
    ('Everyone', 'Everyone'),
    ('Admins only', 'Admins only'),
]

# Class to create public folders
class PublicFolders(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    folder_name = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    recycled = models.BooleanField(default=False)
    permission_field = models.CharField(max_length=10, choices=permissions, default='All')
    
    def __str__(self):
        return f' {self.folder_name}'
    
    class Meta:
        ordering = ['-date']
    

# Class to create public files
class PublicFiles(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.FileField(storage=Storage())
    date = models.DateField(auto_now_add=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    folder = models.ForeignKey(PublicFolders, on_delete=models.CASCADE, blank=True, null=True)
    permission_field = models.CharField(max_length=10, choices=permissions, default='All')
    recycled = models.BooleanField(default=False)

    def __str__(self):
        return f' {self.filename}'

    # def get_absolute_url(self):
    #     return reverse('file_list')

    def get_absolute_url(self):
        file = PublicFiles.objects.get(id=self.pk)
        if file.folder:
            return reverse('folder_detail', args=[str(file.folder.id)])
        else:
            return reverse('file_list')
    
    class Meta:
        ordering = ['-date']

# Class to share public files
class SharedFiles(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.ForeignKey(PublicFiles, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    permission_field = models.CharField(max_length=10, choices=permissions, default='All')

    def __str__(self):
        return f' {self.filename}'
    
    

# Class to share public folders   
class SharedFolders(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    folder_name = models.ForeignKey(PublicFolders, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    permission_field = models.CharField(max_length=10, choices=permissions, default='All')

    def __str__(self):
        return f' {self.folder_name}'
    
# Class to create private folders
class PrivateFolders(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    folder_name = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    recycled = models.BooleanField(default=False)
    permission_field = models.CharField(max_length=10, choices=permissions, default='All')
    
    def __str__(self):
        return f' {self.folder_name}'
    
    class Meta:
        ordering = ['-date']
    

# Class to create private files
class PrivateFiles(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.FileField(storage=Storage())
    date = models.DateField(auto_now_add=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    folder = models.ForeignKey(PrivateFolders, on_delete=models.CASCADE, blank=True, null=True)
    permission_field = models.CharField(max_length=10, choices=permissions, default='All')
    recycled = models.BooleanField(default=False)

    def __str__(self):
        return f' {self.filename}'

    # def get_absolute_url(self):
    #     return reverse('private_file_list')
    
    def get_absolute_url(self):
        file = PrivateFiles.objects.get(id=self.pk)
        if file.folder:
            return reverse('private_folder_detail', args=[str(file.folder.id)])
        else:
            return reverse('private_file_list')
    
    class Meta:
        ordering = ['-date']

# Class to share private files
class SharedPrivateFiles(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.ForeignKey(PrivateFiles, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    permission_field = models.CharField(max_length=10, choices=permissions, default='All')

    def __str__(self):
        return f' {self.filename}'

# Class to share private folders   
class SharedPrivateFolders(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    folder_name = models.ForeignKey(PrivateFolders, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    permission_field = models.CharField(max_length=10, choices=permissions, default='All')

    def __str__(self):
        return f' {self.folder_name}'

# # Class to make announcement for either admins only or all users
class Announcement(models.Model):
    send_to = models.CharField(max_length=15, choices=announcement_groups, default='Everyone')
    title = models.CharField(max_length=30)
    message = models.TextField(max_length=200)

    def __str__(self):
        return f' {self.title}'
    
    def get_absolute_url(self):
        return reverse('announcement')