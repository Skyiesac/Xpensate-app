from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.

class UserModelAdmin(BaseUserAdmin):

  list_display = ('email','created_at', 'is_admin', 'is_active')
  list_filter = ('is_admin','is_active',)
  fieldsets = (
      (None, {'fields': ('email', 'password','contact')}),
    )
 
  add_fieldsets = (
      ( None, {
        'classes': ('wide',),
          'fields': ('email', 'password','is_active',),
      }),
  )
  search_fields = ('email',)
  ordering = ('email',)
  filter_horizontal = ()


class EmailOTPModelAdmin(admin.ModelAdmin):
  list_display = ('email', 'otp','otp_created_at')
  fieldsets = (
      ('Details', {'fields': ('email', 'otp',)}),
  )

class RegisteruserModelAdmin(admin.ModelAdmin):
  list_display = ('email','password','otp')
  fieldsets= (
    ('Details', {'fields':('email', 'password', 'otp',)}),
  )
class PhoneOTPModelAdmin(admin.ModelAdmin):
  list_display = ('contact', 'otp','otp_created_at')
  fieldsets = (
      ('Details', {'fields': ('contact', 'otp',)}),
  )

class FCMTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'fcm_token')
    search_fields = ('user__email', 'fcm_token')

admin.site.register(FCMToken, FCMTokenAdmin)
admin.site.register(User, UserModelAdmin)
admin.site.register(EmailOTP, EmailOTPModelAdmin)
admin.site.register(PhoneOTP, PhoneOTPModelAdmin)
admin.site.register(Register_user , RegisteruserModelAdmin)