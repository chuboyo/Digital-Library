# import modules to build custom template tag for notificartion
from django import template
from notification.models import Notification
from django.db.models import Q


# build function for custom template tag by filtering notification objects from Notification table 
# based on integer meaning. Calculate total notification count for admins and regular users and 
# return values in context
register = template.Library()
@register.inclusion_tag('notification/show_notifications.html', takes_context=True)
def show_notifications(context):
    request_user = context['request'].user
    user_specific_notifications = Notification.objects.filter((Q(notification_type=1) | Q(notification_type=2) | Q(notification_type=3) | Q(notification_type=4)) & Q(to_user=request_user)).exclude(user_has_seen=True).order_by('-date')
    user_specific_notifications_count = user_specific_notifications.count()
    # general_notifications = Notification.objects.filter(to_user__isnull=True).exclude(user_has_seen=True).order_by('-date')
    general_announcements = Notification.objects.filter(Q(notification_type=5) & Q(to_user=request_user)).exclude(user_has_seen=True).order_by('-date')
    general_announcements_count = general_announcements.count()
    admin_announcements = Notification.objects.filter(Q(notification_type=6) & Q(to_user=request_user)).exclude(user_has_seen=True).order_by('-date')
    admin_announcements_count = admin_announcements.count()
    # email_change = Notification.objects.filter(Q(notification_type=7) & Q(to_user=request_user)).exclude(user_has_seen=True).order_by('-date')
    email_change = Notification.objects.filter(Q(notification_type=7)).exclude(user_has_seen=True).order_by('-date')
    email_change_count = email_change.count()
    # new_user_registration = Notification.objects.filter(Q(notification_type=8) & Q(to_user=request_user)).exclude(user_has_seen=True).order_by('-date')
    new_user_registration = Notification.objects.filter(Q(notification_type=8)).exclude(user_has_seen=True).order_by('-date')
    new_user_registration_count = new_user_registration.count()
    total_notification_count = user_specific_notifications_count + general_announcements_count
    total_notification_count_admin = user_specific_notifications_count + general_announcements_count + admin_announcements_count + email_change_count + new_user_registration_count
    return {'specific_notifications': user_specific_notifications, 'general_announcements': general_announcements, 
            'admin_announcements': admin_announcements, 'email_change_requests': email_change, 'new_user_registrations': new_user_registration,
            'notification_count': total_notification_count, 'admin_count': total_notification_count_admin, 'request_user': request_user}