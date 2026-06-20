from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def role_required(profile_attribute, login_url):
    """Require authentication and the profile belonging to one EV Point role."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(login_url)
            if not hasattr(request.user, profile_attribute):
                messages.error(request, 'This account does not have permission to access that page.')
                return redirect(login_url)
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator


client_required = role_required('userprofile', 'login')
owner_required = role_required('ownerprofile', 'owner_login')
staff_required = role_required('station_staff_profile', 'staff_login')
