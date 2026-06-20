from django.urls import path,include
from . import views


urlpatterns = [ 
    path('',views.index,name='index'),
    path('signup/',views.signup,name='signup'),
    path('login/',views.login,name='login'),
    path('owner_signup/',views.owner_signup,name='owner_signup'),
    path('owner_login/',views.owner_login,name='owner_login'),
    path('logout/', views.logout_view, name='logout'),
        
]
