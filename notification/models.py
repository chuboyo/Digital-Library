# import modules, classes and functions to build models
from django.db import models
from django.contrib.auth import get_user_model
from filesystem.models import PublicFiles, PrivateFiles, PublicFolders, PrivateFolders, Announcement

# notification model with integers 1-8 representing the various notification types
class Notification(models.Model):
    # 1 = file_shared, 2 = folder_shared, 3 = file_renamed, 4 = folder_renamed, 5 = general_announcement
    # 6 = admin_announcement, 7 = email_change_request, 8 = new_user_registration
    notification_type = models.IntegerField(null=True, blank=True)
    to_user = models.ForeignKey(get_user_model(), related_name='notification_to', on_delete=models.CASCADE, null=True, blank=True)
    from_user = models.ForeignKey(get_user_model(), related_name='notification_from', on_delete=models.CASCADE, null=True, blank=True)
    publicfile = models.ForeignKey(PublicFiles, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    privatefile = models.ForeignKey(PrivateFiles, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    publicfolder = models.ForeignKey(PublicFolders, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    privatefolder = models.ForeignKey(PrivateFolders, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    old_file_name = models.CharField(max_length=30, null=True, blank=True)
    old_folder_name = models.CharField(max_length=30, null=True, blank=True)
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    user_has_seen = models.BooleanField(default=False)

    def __str__(self):
        return f' {self.notification_type}'