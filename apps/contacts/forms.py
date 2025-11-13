from django import forms
from .models import ContactRequest


class ContactRequestForm(forms.ModelForm):
    class Meta:
        model = ContactRequest
        fields = ['name', 'organization', 'phone',
                  'email', 'request_type', 'product', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ваше имя *',
                'required': True
            }),
            'organization': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Название организации'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+7 (___) ___-__-__',
                'type': 'tel',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'email@example.com'
            }),
            'request_type': forms.Select(attrs={
                'class': 'form-input'
            }),
            'product': forms.Select(attrs={
                'class': 'form-input'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Опишите ваш запрос...',
                'required': True
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = self.fields['product'].queryset.filter(
            is_active=True)
        self.fields['product'].empty_label = "Выберите товар (необязательно)"
        self.fields['product'].required = False

        # Делаем поля обязательными
        self.fields['name'].required = True
        self.fields['phone'].required = True
        self.fields['message'].required = False
