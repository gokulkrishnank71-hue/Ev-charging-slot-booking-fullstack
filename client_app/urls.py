from django.urls import path,include
from . import views


urlpatterns = [
    path('client_dashboard/',views.client_dashboard,name='client_dashboard'),
    path('plans_list/',views.plans_list,name='plans_list'),
    path('station_search/',views.station_search,name='station_search'),
    path('book_now/<int:station_id>/', views.book_now, name='book_now'),
    path('bookings/', views.my_bookings, name='my_bookings'),
    path('bookings/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
      ]
