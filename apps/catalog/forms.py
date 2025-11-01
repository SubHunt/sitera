from django import forms
from .models import Product, Category


class ImportForm(forms.Form):
    file = forms.FileField(
        label='Выберите файл для импорта',
        help_text='Поддерживаемые форматы: CSV, XLSX, JSON',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx,.json'
        })
    )

    update_existing = forms.BooleanField(
        label='Обновлять существующие товары',
        required=False,
        initial=False,
        help_text='Если включено, существующие товары будут обновлены данными из файла'
    )

    delete_missing = forms.BooleanField(
        label='Удалять отсутствующие товары',
        required=False,
        initial=False,
        help_text='Если включено, товары отсутствующие в файле будут удалены из базы'
    )


class ProductImportForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'article', 'description', 'category', 'subcategory',
                  'availability', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'article': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'subcategory': forms.Select(attrs={'class': 'form-control'}),
            'availability': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
