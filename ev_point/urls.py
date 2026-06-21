from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/',admin.site.urls),
    path('api-auth/',include('rest_framework.urls')),
    path('',include('home.urls')),
    path('client/',include('client_app.urls')),
    path('owner/',include('owner_app.urls')),
    path('staff/',include('staff_app.urls')),
]
