from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('user/', views.user_profile, name='user_profile'),
    path('change-password/', views.change_password, name='change_password'),
]