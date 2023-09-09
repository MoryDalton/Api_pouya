from django.contrib import admin
from users.models import Users, ValidNumbers, EmailVerify

from django.contrib.auth.admin import UserAdmin
from django.forms import TextInput, Textarea, CharField
from django.db import models


class UserAdminConfig(UserAdmin):
    model = Users
    search_fields = ('phone', 'family', 'email', 'store', 'created_date')
    list_filter = ('phone', 'email', 'created_date', 'is_active', 'is_staff')
    ordering = ('-created_date',)
    list_display = ('phone', 'name', 'family', 'email', 'store', 'created_date', 'is_superuser', 
                    'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('phone', 'name', 'family', 'email', 'password')}),
        ('Permissions', {'fields': ('is_superuser', 'is_staff', 'is_active')}),
        # ('Personal', {'fields': (' ',)}),
    )
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 20, 'cols': 60})},
    }
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'name', 'family', 'email', 'password1', 'password2', 'is_superuser', 'is_active', 'is_staff')}
         ),
    )


class ValidNumbersAdminConfig(admin.ModelAdmin):
    model = ValidNumbers

    search_fields = ('id', 'phone', 'name', 'created_date')
    list_filter = ('id', 'phone', 'name', 'created_date')
    ordering = ('-created_date',)
    list_display = ('id', 'phone', 'name', 'created_date')


# class SmsAdminConfig(admin.ModelAdmin):
#     model = Sms

#     search_fields = ('id', 'phone', 'code', 'created_date')
#     list_filter = ('id', 'phone', 'code', 'created_date')
#     ordering = ('-created_date',)
#     list_display = ('id', 'phone', 'code', 'created_date')

class EmailVerifyAdminConfig(admin.ModelAdmin):
    model = EmailVerify

    search_fields = ('id', 'email', 'code', 'created_date')
    list_filter = ('id', 'email', 'code', 'created_date')
    ordering = ('-created_date',)
    list_display = ('id', 'email', 'code', 'created_date')


admin.site.register(Users, UserAdminConfig)
admin.site.register(ValidNumbers, ValidNumbersAdminConfig)
admin.site.register(EmailVerify, EmailVerifyAdminConfig)
# admin.site.register(Sms, SmsAdminConfig)
