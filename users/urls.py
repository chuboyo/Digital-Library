# import modules, classes and functions to create views
from django.urls import path

from .views import (UserListView, RegistrationListView, UserDetailView, UserUpdateView, AdminUpdateView, 
DeactivateUserUpdateView, UserDeleteView)

# urls to access templates for various user related pages
urlpatterns = [
    path('profile/', UserListView.as_view(), name='user_list'),
    path('profile/registration', RegistrationListView.as_view(), name='reg_list'),
    path('profile/<uuid:pk>', UserDetailView.as_view(), name='user_detail'),
    path('profile/<uuid:pk>/edit/', UserUpdateView.as_view(), name='user_edit'),
    path('profile/<uuid:pk>/admin_edit/', AdminUpdateView.as_view(), name='admin_edit'),
    # path('profile/<uuid:pk>/user_edit_email/', UserRequestEmailChange.as_view(), name='user_edit_email'),
    # path('profile/<uuid:pk>/admin_edit_email/', AdminRequestEmailChange.as_view(), name='admin_edit_email'),
    path('profile/<uuid:pk>/deactivate_edit/', DeactivateUserUpdateView.as_view(), name='deactivate_edit'),
    path('profile/<uuid:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    #'profile/uuid---/request_email_change'
]
