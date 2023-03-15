# import modules, classes and functions to create views
from django.shortcuts import render
import os, json
from django.http import JsonResponse, HttpResponse
from .models import Notification
from django.db.models import Q
from django.contrib.auth import get_user_model

# Create your views here.

# function to check if request is ajax request
def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' 

# function to mark selected notification as read
def mark_notification_read(request):
    if is_ajax(request=request) and request.method=='POST':
        notification_id = request.POST.get('notification_id')
        notification = Notification.objects.get(id=notification_id)
        notification.user_has_seen = True 
        notification.save()
        data = {'status':'success'}
        return JsonResponse(data, status=200)
    else:
        data = {'status':'error'}
        return JsonResponse(data, status=400)
    
# function to mark all notifications as read
def mark_all_notification_read(request):
    if is_ajax(request=request) and request.method=='POST':
        user_id = request.POST.get('user_id')
        user = get_user_model().objects.get(id=user_id)
        notifications = Notification.objects.filter(to_user=user)
        email_change_and_user_registered = Notification.objects.filter(Q(notification_type=7) | Q(notification_type=8))
        for notification in email_change_and_user_registered:
            notification.user_has_seen = True 
            notification.save()
        for notification in notifications:
            notification.user_has_seen = True 
            notification.save()
        data = {'status':'success'}
        return JsonResponse(data, status=200)
    else:
        data = {'status':'error'}
        return JsonResponse(data, status=400)
    

# function to allow email change from notification
def allow_email_change(request):
    if is_ajax(request=request) and request.method == 'POST':
        pk = request.POST.get('user_id')
        profile = get_user_model().objects.get(id=pk)
        profile.email_change_approved = True
        profile.email_change_requested = False
        profile.save()
        data = {'status': 'success'}
        return JsonResponse(data, status=200)
    else:
        data = {'status': 'error'}
        return JsonResponse(data, status=400)
    

# function to activate new user from notification
def activate_new_user(request):
    if is_ajax(request=request) and request.method == 'POST':
        pk = request.POST.get('user_id')
        profile = get_user_model().objects.get(id=pk)
        profile.is_active = True
        profile.save()
        data = {'status': 'success'}
        return JsonResponse(data, status=200)
    else:
        data = {'status': 'error'}
        return JsonResponse(data, status=400)
    
# List all notifications
def all_notifications(request):
    request_user = request.user
    user_specific_notifications = Notification.objects.filter((Q(notification_type=1) | Q(notification_type=2) | Q(notification_type=3) | Q(notification_type=4)) & Q(to_user=request_user)).exclude(user_has_seen=True).order_by('-date')
    user_specific_notifications_count = user_specific_notifications.count()
    # general_notifications = Notification.objects.filter(to_user__isnull=True).exclude(user_has_seen=True).order_by('-date')
    general_announcements = Notification.objects.filter(Q(notification_type=5) & Q(to_user=request_user)).exclude(user_has_seen=True).order_by('-date')
    general_announcements_count = general_announcements.count()
    admin_announcements = Notification.objects.filter(Q(notification_type=6) & Q(to_user=request_user)).exclude(user_has_seen=True).order_by('-date')
    admin_announcements_count = admin_announcements.count()
    email_change = Notification.objects.filter(Q(notification_type=7)).exclude(user_has_seen=True).order_by('-date')
    email_change_count = email_change.count()
    new_user_registration = Notification.objects.filter(Q(notification_type=8)).exclude(user_has_seen=True).order_by('-date')
    new_user_registration_count = new_user_registration.count()
    total_notification_count = user_specific_notifications_count + general_announcements_count
    total_notification_count_admin = user_specific_notifications_count + general_announcements_count + admin_announcements_count + email_change_count + new_user_registration_count
    context =  {'specific_notifications': user_specific_notifications, 'general_announcements': general_announcements, 
            'admin_announcements': admin_announcements, 'email_change_requests': email_change, 'new_user_registrations': new_user_registration,
            'notification_count': total_notification_count, 'admin_count': total_notification_count_admin, 'request_user': request_user}
    return render(request, 'notification/all_notifications.html' , context)