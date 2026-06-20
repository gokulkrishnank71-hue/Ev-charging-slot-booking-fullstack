from django.contrib import admin
from .models import OwnerProfile, UserProfile

admin.site.register(UserProfile)
admin.site.register(OwnerProfile)
