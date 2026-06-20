from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import UserProfile, OwnerProfile
from .decorators import client_required


# ==================================================
# Home Page View
# Displays the landing page of the EV Point system
# ==================================================

def index(request):
    return render(request, 'home/index.html')


# ==================================================
# Client Registration View
# Handles new user account creation and profile setup
# ==================================================

def signup(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        name = request.POST.get('name')
        phone = request.POST.get('phone')

        # Check whether username already exists
        if User.objects.filter(username=username).exists():

            return render(
                request,
                'home/signup.html',
                {'error': 'Username already exists'}
            )

        # Check whether email already exists
        if User.objects.filter(email=email).exists():

            return render(
                request,
                'home/signup.html',
                {'error': 'Email already exists'}
            )

        # Create Django authentication user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Create client profile linked to the user
        UserProfile.objects.create(
            user=user,
            name=name,
            phone=phone
        )

        # Redirect user to login page
        return redirect('login')

    return render(request, 'home/signup.html')


# ==================================================
# Client Login View
# Authenticates users and grants dashboard access
# ==================================================

def login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and hasattr(user, 'userprofile'):

            # Create authenticated session
            auth_login(request, user)

            return redirect('client_dashboard')

        else:

            return render(
                request,
                'home/login.html',
                {'error': 'Invalid username or password'}
            )

    return render(request, 'home/login.html')


# ==================================================
# Client Dashboard View
# Displays the main dashboard for logged-in clients
# ==================================================

@client_required
def client_dashboard(request):

    # Allow access only to authenticated users
    if not request.user.is_authenticated:

        return redirect('login')

    return render(request, 'home/client_dashboard.html')


# ==================================================
# Logout View
# Terminates user session and redirects to login
# ==================================================

@require_POST
@login_required
def logout_view(request):

    logout(request)

    return redirect('index')


# ==================================================
# Owner Registration View
# Handles EV station owner account creation
# ==================================================

def owner_signup(request):

    if request.method == "POST":

        owner_name = request.POST.get('owner_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check whether username already exists
        if User.objects.filter(username=username).exists():

            return render(
                request,
                'home/owner_signup.html',
                {'error': 'Username already exists'}
            )

        # Check whether email already exists
        if User.objects.filter(email=email).exists():

            return render(
                request,
                'home/owner_signup.html',
                {'error': 'Email already exists'}
            )

        # Create Django authentication user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Create owner profile linked to the user
        OwnerProfile.objects.create(
            user=user,
            owner_name=owner_name,
            phone=phone
        )

        # Redirect owner to login page
        return redirect('owner_login')

    return render(request, 'home/owner_signup.html')


# ==================================================
# Owner Login View
# Authenticates station owners and opens dashboard
# ==================================================

def owner_login(request):

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and hasattr(user, 'ownerprofile'):

            # Create authenticated owner session
            auth_login(request, user)

            return redirect('owner_dashboard')

        else:

            return render(
                request,
                'home/owner_login.html',
                {'error': 'Invalid username or password'}
            )

    return render(request, 'home/owner_login.html')
