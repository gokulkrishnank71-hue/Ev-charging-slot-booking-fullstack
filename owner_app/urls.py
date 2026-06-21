from django.urls import path

from . import views
from .apiviews import OwnerDetailAPIView, OwnerListAPIView


urlpatterns = [
    path('owner_dashboard/',views.owner_dashboard,name='owner_dashboard'),
    path('add_station/',views.add_station,name='add_station'),
    path('staff/',views.manage_staff,name='manage_staff'),
    path('staff/add/',views.add_staff,name='add_staff'),
    path('staff/<int:staff_id>/toggle/',views.toggle_staff,name='toggle_staff'),

    path('api/owners/',OwnerListAPIView.as_view(),name='owner-api-list'),
    path('api/owners/<int:pk>/',OwnerDetailAPIView.as_view(),name='owner-api-detail'),
]
