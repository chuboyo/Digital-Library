#  import modules, classes and functions to create signals 
from allauth.account.signals import user_signed_up, email_confirmed
from .models import CustomUser
from notification.models import Notification
from django.dispatch import receiver
from .models import CustomUser
from allauth.account.models import EmailAddress
from django.db.models.signals import pre_save, post_save
from django.conf import settings
from django.core.mail import send_mail


#This sets "is_active" to True so dj_all_auth can send out account confirmation emails
@receiver(user_signed_up)
def user_signed_up_(request, user, **kwargs):
    user.is_active = True
    user.save()

#signal used to deactivate account after email has been confirmed 
@receiver(email_confirmed)
def email_confirmed_(request, email_address, **kwargs):
    user = CustomUser.objects.get(email=email_address.email)
    admins = CustomUser.objects.filter(is_custom_admin=True)
    # for admin in admins:
    #     Notification.objects.create(notification_type=8, to_user=admin, from_user=user)
    Notification.objects.create(notification_type=8, from_user=user)
    user.is_active = False
    user.save()

#signal used to send email to user when account is activated by an admin
@receiver(pre_save, sender=CustomUser, dispatch_uid='active')
def active(sender, instance, **kwargs):
    if instance.is_active and CustomUser.objects.filter(pk=instance.pk, is_active=False).exists():
        subject = 'Active account'
        message = '%s your account is now active' %(instance.username)
        from_email = settings.DEFAULT_FROM_EMAIL
        send_mail(subject, message, from_email, [instance.email], fail_silently=False)

    