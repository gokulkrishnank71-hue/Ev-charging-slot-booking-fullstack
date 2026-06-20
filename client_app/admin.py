from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'station', 'date', 'slot_name', 'status', 'status_updated_by', 'created_at')
    list_filter = ('status', 'date', 'station')
    search_fields = ('user__username', 'station__station_name', 'slot_name')
