
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.hashers import make_password
import secrets
import string

class User(AbstractUser):
    # Только для входа в админ панель Django
    # Наследуем все стандартные поля Django
    
    # Добавляем поле phone как необязательное для совместимости
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон")
    
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

class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Назва")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL")
    description = models.TextField(blank=True, verbose_name="Опис")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Категорія",
        related_name='products'
    )
    title = models.CharField(max_length=500, verbose_name="Найменування")
    description = models.TextField(verbose_name="Опис", blank=True)
    unit = models.CharField(max_length=50, verbose_name="Од.вим", blank=True)
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Облікова ціна б.г. з ПДВ $",
        null=True,
        blank=True
    )
    wholesale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Гуртова ціна з ПДВ, авт% $",
        null=True,
        blank=True
    )
    sku = models.CharField(max_length=100, verbose_name="Артикул", blank=True)
    modules_count = models.IntegerField(verbose_name="Кількість модулів", null=True, blank=True)
    stock_quantity = models.IntegerField(verbose_name="Вільно на складі", default=0)
    url = models.SlugField(max_length=500, verbose_name="URL товара", blank=True)
    external_link = models.CharField(max_length=500, verbose_name="Посилання", blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Активний")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товари"
        ordering = ['title']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['sku']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.title

class ImportTemplate(models.Model):
    name = models.CharField(max_length=255, verbose_name="Назва імпорту")
    description = models.TextField(blank=True, verbose_name="Опис")
    is_active = models.BooleanField(default=True, verbose_name="Активний")
    
    # Налаштування Excel
    sheet_name = models.CharField(max_length=255, verbose_name="Назва вкладки", blank=True)
    process_all_sheets = models.BooleanField(default=True, verbose_name="Обробити всі вкладки")
    
    # Маппінг полів (JSON)
    field_mapping = models.JSONField(
        verbose_name="Маппінг полів",
        default=dict,
        help_text="JSON з маппінгом полів Excel → Django"
    )
    
    # Налаштування обробки
    skip_empty_rows = models.BooleanField(default=True, verbose_name="Пропускати порожні рядки")
    create_categories = models.BooleanField(default=True, verbose_name="Створювати категорії")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    class Meta:
        verbose_name = "Шаблон імпорту"
        verbose_name_plural = "Шаблони імпорту"
        ordering = ['name']

    def __str__(self):
        return self.name

class SettingGroup(models.Model):
    name = models.CharField(max_length=255, verbose_name="Назва групи")
    description = models.TextField(blank=True, verbose_name="Опис")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    class Meta:
        verbose_name = "Група налаштувань"
        verbose_name_plural = "Групи налаштувань"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class Setting(models.Model):
    SETTING_TYPES = [
        ('single', 'Одиночне значення'),
        ('list', 'Список значень'),
    ]
    
    group = models.ForeignKey(
        SettingGroup, 
        on_delete=models.CASCADE, 
        verbose_name="Група",
        related_name='settings'
    )
    name = models.CharField(max_length=255, verbose_name="Назва налаштування")
    key = models.CharField(max_length=255, unique=True, verbose_name="Ключ")
    setting_type = models.CharField(
        max_length=20, 
        choices=SETTING_TYPES, 
        verbose_name="Тип налаштування"
    )
    value = models.TextField(blank=True, verbose_name="Значення")
    description = models.TextField(blank=True, verbose_name="Опис")
    is_active = models.BooleanField(default=True, verbose_name="Активне")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    class Meta:
        verbose_name = "Налаштування"
        verbose_name_plural = "Налаштування"
        ordering = ['group', 'order', 'name']

    def __str__(self):
        return f"{self.name} ({self.group.name})"

class SettingValue(models.Model):
    setting = models.ForeignKey(
        Setting, 
        on_delete=models.CASCADE, 
        verbose_name="Налаштування",
        related_name='values'
    )
    value = models.CharField(max_length=500, verbose_name="Значення")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    is_active = models.BooleanField(default=True, verbose_name="Активне")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")

    class Meta:
        verbose_name = "Значення налаштування"
        verbose_name_plural = "Значення налаштувань"
        ordering = ['setting', 'order', 'value']

    def __str__(self):
        return f"{self.value} ({self.setting.name})"
