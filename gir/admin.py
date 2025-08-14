from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from .models import User, FrontendUser

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Только для входа в админ панель Django
    list_display = ("username", "email", "first_name", "last_name", "is_active", "is_staff", "is_superuser")
    search_fields = ("username", "first_name", "last_name", "email")
    list_filter = ("is_active", "is_staff", "is_superuser")

@admin.register(FrontendUser)
class FrontendUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "first_name", "last_name", "company", "is_active", "created_at")
    search_fields = ("username", "first_name", "last_name", "email", "company")
    list_filter = ("is_active", "company", "created_at")
    
    fieldsets = (
        ("Основна інформація", {
            "fields": ("username", "password", "email", "first_name", "last_name")
        }),
        ("Контактна інформація", {
            "fields": ("phone", "company")
        }),
        ("Додатково", {
            "fields": ("is_active",)
        }),
        ("Метадані", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    readonly_fields = ("created_at", "updated_at")
    
    class Media:
        css = {
            'all': ('https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',)
        }
        js = (
            'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
            'gir/js/password_buttons.js',
        )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:  # Если создаем нового пользователя
            form.base_fields['password'].help_text = "Пароль буде автоматично захешований. Використовуйте кнопку 'Згенерувати' для створення безпечного пароля."
        else:  # Если редактируем существующего
            # Заменяем поле пароля на наше кастомное
            from django import forms
            form.base_fields['password'] = forms.CharField(
                label="Пароль",
                widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                help_text="Введіть новий пароль або використайте кнопку 'Згенерувати'",
                required=False
            )
        
        return form
    
    def save_model(self, request, obj, form, change):
        # Хешируем пароль при любых изменениях
        if 'password' in form.changed_data or not change:
            if not obj.password:
                obj.password = obj.generate_password()
            else:
                # Хешируем введенный пароль
                from django.contrib.auth.hashers import make_password
                obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)