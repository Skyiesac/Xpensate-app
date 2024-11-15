from django.contrib import admin
from .models import Tripgroup, TripMember, addedexp, tosettle
class TripMemberInline(admin.TabularInline):
    model = TripMember
    extra = 1  # Number of empty forms to display

class TripgroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'invitecode', 'created_at')
    search_fields = ('name', 'invitecode')
    readonly_fields = ('invitecode', 'created_at')
    inlines = [TripMemberInline]

class TripMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'joined_at')
    search_fields = ('user__email', 'group__name')
    readonly_fields = ('joined_at',)

class AddedExpAdmin(admin.ModelAdmin):
    list_display = ('whatfor', 'amount', 'paidby')
    search_fields = ('whatfor', 'paidby__email')

class ToSettleAdmin(admin.ModelAdmin):
    list_display = ('debtamount', 'debter', 'creditor')
    search_fields = ('debter__email', 'creditor__email')

admin.site.register(Tripgroup, TripgroupAdmin)
admin.site.register(TripMember, TripMemberAdmin)
admin.site.register(addedexp, AddedExpAdmin)
admin.site.register(tosettle, ToSettleAdmin)