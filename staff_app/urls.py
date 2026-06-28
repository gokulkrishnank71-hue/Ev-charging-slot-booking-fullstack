from django.urls import path

from . import views


urlpatterns = [
    path('login/',views.staff_login,name='staff_login'),
    path('dashboard/',views.dashboard,name='staff_dashboard'),
    path('station/status/',views.update_station_status,name='update_station_status'),
    path('slots/<int:slot_id>/status/',views.update_slot_status,name='update_slot_status'),
    path('bookings/<int:booking_id>/status/',views.update_booking_status,name='update_booking_status'),

]
