
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.hashers import make_password
import secrets
import string

class User(AbstractUser):
    # Только для входа в админ панель Django
    # Наследуем все стандартные поля Django
    pass

    def __str__(self):
        return f"{self.username} (адмін)"

    class Meta:
        verbose_name = "Адміністратор"
        verbose_name_plural = "Адміністратори"

class FrontendUser(models.Model):
    # Пользователи фронтенда - полностью независимая система
    username = models.CharField(max_length=150, unique=True, verbose_name="Логін")
    password = models.CharField(max_length=128, verbose_name="Пароль")
    email = models.EmailField(unique=True, verbose_name="Email", blank=True, null=True)
    first_name = models.CharField(max_length=200, blank=True, verbose_name="Ім'я")
    last_name = models.CharField(max_length=200, blank=True, verbose_name="Прізвище")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    company = models.CharField(max_length=200, blank=True, null=True, verbose_name="Компанія")
    # photo = models.ImageField(upload_to="frontend_user_photos/", blank=True, null=True, verbose_name="Фото")  # временно отключено
    is_active = models.BooleanField(default=True, verbose_name="Активний")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    def __str__(self):
        return f"{self.username} (користувач)"

    def save(self, *args, **kwargs):
        # Хешируем пароль при сохранении
        if not self.pk or self._state.adding:  # Если это новый объект
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def generate_password(self):
        # Генерируем случайный пароль
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for i in range(12))
        self.password = password
        return password

    def check_password(self, raw_password):
        # Проверяем пароль
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)

    class Meta:
        verbose_name = "Користувач"
        verbose_name_plural = "Користувачі"
