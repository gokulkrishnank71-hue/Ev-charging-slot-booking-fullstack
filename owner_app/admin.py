from django.contrib import admin
from .models import EVStation
from .models import chargingslot


@admin.register(EVStation)
class EVStationAdmin(admin.ModelAdmin):

    list_display = (
        'station_id',
        'station_name',
        'owner',
        'city',
        'station_type',
        'total_slots',
        'rate_per_unit',
        'phone_number',
        'is_active',
        'operational_status',
    )

    search_fields = (
        'station_name',
        'city',
        'phone_number'
    )

    list_filter = (
        'city',
        'station_type',
        'is_active',
        'operational_status',
    )

    list_editable = (
        'is_active',
    )

    


    admin.site.register(chargingslot)
