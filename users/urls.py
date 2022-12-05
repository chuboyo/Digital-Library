# import modules, classes and functions to create views
from django.urls import path

from .views import (user_list_view, set_admin, user_search_results, delete_profile_picture, request_email_change,
EmailChangeListView, RegistrationSearchListView, RegistrationListView, UserDetailView, UserUpdateView, AdminUpdateView, 
AdminUpdateEmailView, UserDeleteView,)

# urls to access templates for various user related pages
urlpatterns = [
    path('profile/', user_list_view, name='user_list'),
    path('profile/search_results', user_search_results, name='user_search_list'),
    path('profile/set_admin/<uuid:pk>', set_admin, name="set_admin"),
    path('profile/registration', RegistrationListView.as_view(), name='reg_list'),
    path('profile/registration/search_results', RegistrationSearchListView.as_view(), name='reg_search_list'),
    path('profile/email_change', EmailChangeListView.as_view(), name='email_list'),
    path('profile/<uuid:pk>', UserDetailView.as_view(), name='user_detail'),
    path('profile/<uuid:pk>/edit/', UserUpdateView.as_view(), name='user_edit'),
    path('profile/<uuid:pk>/edit/delete_profile_picture', delete_profile_picture, name='delete_picture'),
    path('profile/<uuid:pk>/admin_edit/', AdminUpdateView.as_view(), name='admin_edit'),
    path('profile/<uuid:pk>/edit/request_email_change', request_email_change, name='request_email_change'),
    path('profile/<uuid:pk>/admin_edit_email/', AdminUpdateEmailView.as_view(), name='admin_edit_email'),
    path('profile/<uuid:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
]
