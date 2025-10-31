from django.shortcuts import render, redirect
from django.views.generic import FormView
from django.views import View
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import ContactRequest
from .forms import ContactRequestForm


class ContactRequestView(FormView):
    template_name = 'contacts/contact_request.html'
    form_class = ContactRequestForm
    success_url = reverse_lazy('contacts:contact_request')

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            'Ваш запрос успешно отправлен! Мы свяжемся с вами в ближайшее время.'
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Можно добавить дополнительный контекст
        return context


class RequestKPView(View):
    """Обработка формы запроса КП из модального окна"""

    def post(self, request):
        form = ContactRequestForm(request.POST)

        if form.is_valid():
            # Устанавливаем тип запроса "КП"
            contact_request = form.save(commit=False)
            contact_request.request_type = 'kp'
            contact_request.save()

            # Если запрос AJAX (из модального окна)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Ваш запрос успешно отправлен! Мы свяжемся с вами в ближайшее время.'
                })
            else:
                messages.success(
                    request,
                    'Ваш запрос успешно отправлен! Мы свяжемся с вами в ближайшее время.'
                )
                return redirect('catalog:product', slug=contact_request.product.slug if contact_request.product else '/')
        else:
            # Если форма невалидна
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
            else:
                messages.error(
                    request,
                    'Пожалуйста, исправьте ошибки в форме.'
                )
                # Возвращаем на страницу товара или на главную
                product_id = request.POST.get('product')
                if product_id:
                    from apps.catalog.models import Product
                    try:
                        product = Product.objects.get(id=product_id)
                        return redirect('catalog:product', slug=product.slug)
                    except Product.DoesNotExist:
                        pass
                return redirect('/')


class ContactPageView(View):
    """Страница контактов с картой и формой"""

    def get(self, request):
        form = ContactRequestForm()
        context = {
            'form': form,
            'contact_info': {
                'phone': '+7(747)481-83-28',
                'email': 'info@sitera.ru',
                'address': 'Республика Казахстан, г. Астана, ул. Е 652, дом 12, НП 13',
                'working_hours': 'Пн-Пт: 9:00 - 18:00',
                'coordinates': {
                    'lat': 51.057761,
                    'lng': 71.423153
                }
            }
        }
        return render(request, 'contacts/contact_page.html', context)

    def post(self, request):
        form = ContactRequestForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.'
            )
            return redirect('contacts:contact_page')
        else:
            context = {
                'form': form,
                'contact_info': {
                    'phone': '+7(747)481-83-28',
                    'email': 'info@sitera.ru',
                    'address': 'Республика Казахстан, г. Астана, ул. Е 652, дом 12, НП 13',
                    'working_hours': 'Пн-Пт: 9:00 - 18:00',
                    'coordinates': {
                        'lat': 51.057761,
                        'lng': 71.423153
                    }
                }
            }
            return render(request, 'contacts/contact_page.html', context)
