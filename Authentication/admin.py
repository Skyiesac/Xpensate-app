from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.

class UserModelAdmin(BaseUserAdmin):

  list_display = ('email','created_at', 'is_admin', 'is_active')
  list_filter = ('is_admin','is_active',)
  field = (
      ('User Credentials', {'fields': ('email', 'password')}),
    )
 
  add_field = (
      ( {
          'fields': ('email','password1', 'password2'),
      }),
  )
  search_fields = ('email','phone_number','created_at')
  ordering = ('email',)
  filter_horizontal = ()


class EmailOTPModelAdmin(admin.ModelAdmin):
  list_display = ('email', 'otp','otp_created_at')
  fieldsets = (
      ('Details', {'fields': ('email', 'otp',)}),
  )

admin.site.register(User, UserModelAdmin)
admin.site.register(EmailOTP, EmailOTPModelAdmin)