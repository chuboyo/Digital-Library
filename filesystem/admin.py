from django.contrib import admin

from django.contrib.auth import get_user_model
from .models import (PublicFiles, SharedFiles, PublicFolders, SharedFolders, PrivateFiles,
                      PrivateFolders, SharedPrivateFiles, SharedPrivateFolders, Announcement)

admin.site.register(PublicFolders)
admin.site.register(PublicFiles)
admin.site.register(SharedFiles)
admin.site.register(SharedFolders)
admin.site.register(PrivateFolders)
admin.site.register(PrivateFiles)
admin.site.register(SharedPrivateFiles)
admin.site.register(SharedPrivateFolders)
admin.site.register(Announcement)

# Register your models here.