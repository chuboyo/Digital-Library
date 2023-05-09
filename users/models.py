# import modules, classes and functions to build user model
from django.contrib.auth.models import AbstractUser 
from django.db import models
from django.urls import reverse
import uuid

# set up drop down options that correlate with user roles for the system
user_roles = [
    # ('is_custom_admin', 'Admin'),
    ('manager', 'Manager'),
    ('content_manager', 'Content Manager'),
    ('contributor', 'Contributor'),
    ('commenter', 'Commenter'),
    ('viewer', 'Viewer'),
]

# create a customuser class and set up fields for the db table
class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_role = models.CharField(max_length=20, choices=user_roles, default='viewer')
    profile_picture = models.ImageField(blank=True)
    date = models.DateField(auto_now_add=True)
    is_custom_admin = models.BooleanField(blank=True, default=False)
    email_change_requested = models.BooleanField(blank=True, default=False)
    email_change_approved = models.BooleanField(blank=True, default=False)

    # modify the init method of this class to override 'is_active field' setting it to 'false' from its default
    # value of 'true'
    # def __init__(self,*args,**kwargs):
    #     if not args:
    #         kwargs.setdefault('is_active', False)
    #     super(CustomUser,self).__init__(*args,**kwargs)

    #  set url to reverse to when operations are performed on this model
    def get_absolute_url(self):
        return reverse('user_detail', args=[str(self.id)])

    class Meta:
        ordering = ['first_name']


    