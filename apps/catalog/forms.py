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

    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True).order_by('name'),
        label='Категория для всех товаров',
        required=False,
        empty_label='-- Использовать категорию из файла --',
        help_text='Выберите категорию, в которую будут добавлены все товары. Если не выбрано, будет использована категория из файла.',
        widget=forms.Select(attrs={
            'style': 'width: 100%;'  # Убрали form-control, оставили только width
        })
    )

    update_existing = forms.BooleanField(
        label='Обновлять существующие товары',
        required=False,
        initial=False,
        help_text='Если включено, существующие товары (по названию) будут обновлены данными из файла',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    delete_missing = forms.BooleanField(
        label='Удалять отсутствующие товары',
        required=False,
        initial=False,
        help_text='⚠️ ОСТОРОЖНО! Если включено, товары отсутствующие в файле будут удалены из базы',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
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
            'category': forms.Select(attrs={'style': 'width: 100%;'}),
            'subcategory': forms.Select(attrs={'style': 'width: 100%;'}),
            'availability': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
# from django import forms
# from .models import Product, Category
# from .widgets import HierarchicalCategorySelect


# class ImportForm(forms.Form):
#     file = forms.FileField(
#         label='Выберите файл для импорта',
#         help_text='Поддерживаемые форматы: CSV, XLSX, JSON',
#         widget=forms.FileInput(attrs={
#             'class': 'form-control',
#             'accept': '.csv,.xlsx,.json'
#         })
#     )

#     category = forms.ModelChoiceField(
#         queryset=Category.objects.filter(is_active=True),
#         label='Категория для всех товаров',
#         required=False,
#         empty_label='-- Использовать категорию из файла --',
#         help_text='Выберите категорию, в которую будут добавлены все товары. Если не выбрано, будет использована категория из файла.',
#         widget=HierarchicalCategorySelect(attrs={
#             'class': 'form-control'
#         })
#     )

#     update_existing = forms.BooleanField(
#         label='Обновлять существующие товары',
#         required=False,
#         initial=False,
#         help_text='Если включено, существующие товары (по артикулу) будут обновлены данными из файла',
#         widget=forms.CheckboxInput(attrs={
#             'class': 'form-check-input'
#         })
#     )

#     delete_missing = forms.BooleanField(
#         label='Удалять отсутствующие товары',
#         required=False,
#         initial=False,
#         help_text='⚠️ ОСТОРОЖНО! Если включено, товары отсутствующие в файле будут удалены из базы',
#         widget=forms.CheckboxInput(attrs={
#             'class': 'form-check-input'
#         })
#     )


# class ProductImportForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ['title', 'article', 'description', 'category', 'subcategory',
#                   'availability', 'is_active']
#         widgets = {
#             'title': forms.TextInput(attrs={'class': 'form-control'}),
#             'article': forms.TextInput(attrs={'class': 'form-control'}),
#             'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
#             'category': HierarchicalCategorySelect(attrs={'class': 'form-control'}),
#             'subcategory': HierarchicalCategorySelect(attrs={'class': 'form-control'}),
#             'availability': forms.Select(attrs={'class': 'form-control'}),
#             'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#         }
