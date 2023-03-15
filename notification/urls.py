# import modules, classes and functions to create urls
from django.urls import path

from .views import mark_notification_read, mark_all_notification_read, all_notifications, allow_email_change, activate_new_user

urlpatterns = [
    path('mark_read/', mark_notification_read, name='mark_read'),
    path('mark_all_read/', mark_all_notification_read, name='mark_all_read'),
    path('all/', all_notifications, name='all_notifications'),
    path('allow_email_change/', allow_email_change, name='allow_email_change'),
    path('activate_user/', activate_new_user, name='activate_user'),
]