"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView 
from django.conf import settings
from django.conf.urls.static import static
from core.views import health, migrations_status

urlpatterns = [
    path("admin/", admin.site.urls),
    path("gir/", include("gir.urls")),
    path("api/health/", health),
    path("api/migrations/", migrations_status),
    path("", include("gir.urls")),  # главная страница теперь использует gir.urls
]

# Добавляем обработку статических файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Медиа файлы должны быть доступны и в продакшене для импорта
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
