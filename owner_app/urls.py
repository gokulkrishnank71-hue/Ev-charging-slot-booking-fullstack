from django.urls import path

from . import views


urlpatterns = [
    path('owner_dashboard/',views.owner_dashboard,name='owner_dashboard'),
    path('add_station/',views.add_station,name='add_station'),
    path('staff/',views.manage_staff,name='manage_staff'),
    path('staff/add/',views.add_staff,name='add_staff'),
    path('staff/<int:staff_id>/toggle/',views.toggle_staff,name='toggle_staff'),

]
