from django.contrib import admin

from .models import StationSlotStatus, StationStaffProfile


@admin.register(StationStaffProfile)
class StationStaffProfileAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'full_name', 'station', 'phone', 'is_active')
    list_filter = ('is_active', 'station')
    search_fields = ('employee_id', 'full_name', 'user__username', 'phone')


@admin.register(StationSlotStatus)
class StationSlotStatusAdmin(admin.ModelAdmin):
    list_display = ('station', 'slot', 'status', 'updated_by', 'updated_at')
    list_filter = ('status', 'station')
