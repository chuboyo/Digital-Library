from django.contrib import admin

from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
# from .models import EmailRequest

# expose model fields from 'CustomUser' model to display in admin
class customUserAdmin(UserAdmin):
    model = get_user_model()
    list_display = ['email', 'username', 'is_active','is_custom_admin', 'user_role']

# Register models in django admin
admin.site.register(get_user_model(), customUserAdmin)
# admin.site.register(EmailRequest)
