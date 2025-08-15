from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse, path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from .models import User, FrontendUser, Category, Product, ImportTemplate
from .forms import ExcelImportForm

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

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'slug', 'description', 'is_active')
        }),
    )

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'sku', 'cost_price', 'wholesale_price', 
        'stock_quantity', 'is_active', 'created_at'
    ]
    list_filter = ['category', 'is_active', 'created_at', 'updated_at']
    search_fields = ['title', 'sku']
    list_editable = ['is_active', 'cost_price', 'wholesale_price', 'stock_quantity']
    ordering = ['title']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('category', 'title', 'description', 'sku', 'unit', 'is_active')
        }),
        ('Ціни та склад', {
            'fields': ('cost_price', 'wholesale_price', 'stock_quantity')
        }),
        ('Характеристики', {
            'fields': ('modules_count', 'url', 'external_link')
        }),
    )
    prepopulated_fields = {'url': ('title',)}
    
    change_list_template = 'admin/product_changelist.html'
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.import_excel, name='import_excel'),
        ]
        return custom_urls + urls
    
    def import_excel(self, request):
        """Імпорт з Excel файлу"""
        if request.method == 'POST':
            form = ExcelImportForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    # Отримуємо вибраний шаблон
                    import_template = form.cleaned_data['import_template']
                    
                    # Отримуємо файл
                    excel_file = request.FILES["excel_file"]
                    
                    # Параметри імпорту з форми
                    process_all = form.cleaned_data['process_all_sheets']
                    specific_sheets = form.cleaned_data['specific_sheets']
                    
                    # Викликаємо команду з файлом в пам'яті
                    from django.core.management import call_command
                    from io import BytesIO
                    
                    # Створюємо тимчасовий файл в пам'яті
                    temp_file = BytesIO(excel_file.read())
                    temp_file.name = excel_file.name
                    
                    # Викликаємо команду з тимчасовим файлом
                    if specific_sheets and specific_sheets.strip():
                        sheets_list = [s.strip() for s in specific_sheets.split(',')]
                        call_command('import_products', file=temp_file, sheets=sheets_list)
                    else:
                        call_command('import_products', file=temp_file)
                    
                    messages.success(request, f'Імпорт успішно завершено за шаблоном "{import_template.name}"!')
                    
                    return HttpResponseRedirect(reverse('admin:gir_product_changelist'))
                    
                except Exception as e:
                    messages.error(request, f'Помилка імпорту: {str(e)}')
        else:
            form = ExcelImportForm()
        
        context = {
            'title': 'Імпорт товарів з Excel',
            'form': form,
            'opts': self.model._meta,
        }
        return render(request, 'admin/import_form.html', context)

@admin.register(ImportTemplate)
class ImportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'process_all_sheets', 'create_categories', 'created_at']
    list_filter = ['is_active', 'process_all_sheets', 'create_categories', 'created_at']
    search_fields = ['name', 'description']
    
    fieldsets = (
        ('Основна інформація', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Налаштування Excel', {
            'fields': ('sheet_name', 'process_all_sheets')
        }),
        ('Маппінг полів', {
            'fields': ('field_mapping',),
            'description': 'JSON з маппінгом полів Excel → Django'
        }),
        ('Налаштування обробки', {
            'fields': ('skip_empty_rows', 'create_categories')
        }),
    )





