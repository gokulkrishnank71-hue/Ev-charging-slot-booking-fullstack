from django.db import models
from django.contrib.auth.models import User

# ==================================================
# EV Point - User Profile Models
# Stores additional information for clients and station owners
# ==================================================


# ==================================================
# Client Profile Model
# Stores additional details for registered EV Point users
# ==================================================
class UserProfile(models.Model):
    # Link profile with Django authentication user
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Full name of the client
    name = models.CharField(max_length=100)

    # Contact number of the client
    phone = models.CharField(max_length=15)

    # Return username for admin display
    def __str__(self):
        return self.user.username



# ==================================================
# Owner Profile Model
# Stores information about EV charging station owners
# ==================================================
class OwnerProfile(models.Model):
    # Link owner profile with Django authentication user
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Name of the station owner
    owner_name = models.CharField(max_length=100)

    # Contact number of the owner
    phone = models.CharField(max_length=15)

    # Return username for admin display
    def __str__(self):
        return self.user.username