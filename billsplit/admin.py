from django.contrib import admin
from .models import Group, GroupMember, Bill, BillParticipant
from Authentication.models import User

class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'groupowner', 'created_at')
    search_fields = ('name', 'groupowner__email')

class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ('group', 'member', 'date_join')
    search_fields = ('group__name', 'member__email')

class BillAdmin(admin.ModelAdmin):
    list_display = ('billname', 'group', 'amount', 'billowner', 'billdate')
    search_fields = ('billname', 'group__name', 'billowner__email')

class BillParticipantAdmin(admin.ModelAdmin):
    list_display = ('bill', 'participant', 'amount', 'paid')
    search_fields = ('bill__billname', 'participant__email')

admin.site.register(Group, GroupAdmin)
admin.site.register(GroupMember, GroupMemberAdmin)
admin.site.register(Bill, BillAdmin)
admin.site.register(BillParticipant, BillParticipantAdmin)