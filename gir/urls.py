from django.urls import path
from django.contrib.auth import views as auth_views
from .views import dashboard, home, frontend_login, frontend_logout

urlpatterns = [
    path("", home, name="home"),  # главная страница с формой логина
    path("login/", frontend_login, name="frontend_login"),  # обработка логина
    path("logout/", frontend_logout, name="frontend_logout"),  # выход
    path("dashboard/", dashboard, name="dashboard"),  # защищенная страница dashboard
]