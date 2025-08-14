from django.urls import path
from . import views

app_name = 'gir'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.frontend_login, name='frontend_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.frontend_logout, name='frontend_logout'),
]