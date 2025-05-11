from django.contrib import admin

# Register your models here.


from django.contrib import admin
from .models import MikroTikRouter, AccessTicket, Plan

@admin.register(MikroTikRouter)
class MikroTikRouterAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip_address', 'username', 'api_port')
    search_fields = ('name', 'ip_address')

@admin.register(AccessTicket)
class AccessTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_code', 'user', 'plan_name', 'start_date', 'expiry_date', 'is_active')
    search_fields = ('ticket_code', 'user__username')
    list_filter = ('is_active',)

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'bandwidth_limit', 'price', 'duration_months')
    search_fields = ('name',)
