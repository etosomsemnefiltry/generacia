from django import forms


class ExcelImportForm(forms.Form):
    import_template = forms.ModelChoiceField(
        queryset=None,
        label='Шаблон імпорту',
        help_text='Виберіть шаблон для обробки файлу',
        empty_label=None
    )
    excel_file = forms.FileField(
        label='Excel файл',
        help_text='Виберіть Excel файл з номенклатурою товарів',
        widget=forms.FileInput(attrs={'accept': '.xlsx,.xls'})
    )
    process_all_sheets = forms.BooleanField(
        label='Обробити всі вкладки',
        required=False,
        initial=True,
        help_text='Якщо відмічено - обробляються всі вкладки з товарами'
    )
    specific_sheets = forms.CharField(
        label='Конкретні вкладки',
        required=False,
        help_text='Назви вкладок через кому (наприклад: "Номенклатура ВА, Номенклатура ВБ")',
        widget=forms.TextInput(attrs={'placeholder': 'Номенклатура ВА, Номенклатура ВБ'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from gir.models import ImportTemplate
        self.fields['import_template'].queryset = ImportTemplate.objects.filter(is_active=True)
