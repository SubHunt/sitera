from django.shortcuts import render, redirect
from django.views.generic import FormView
from django.views import View
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import re
from .models import ContactRequest
from .forms import ContactRequestForm
from .utils import send_contact_notification, send_auto_reply, send_consultation_notification, format_phone_number


class ContactRequestView(FormView):
    template_name = 'contacts/contact_request.html'
    form_class = ContactRequestForm
    success_url = reverse_lazy('contacts:contact_request')

    def form_valid(self, form):
        # Сохраняем форму
        contact_request = form.save()

        # Отправляем уведомление на email
        try:
            send_contact_notification(contact_request)
            # Отправляем автоматический ответ клиенту
            send_auto_reply(contact_request)
        except Exception as e:
            # Если email не отправился, все равно сохраняем запрос
            print(f"Ошибка при отправке email: {e}")

        messages.success(
            self.request,
            'Ваш запрос успешно отправлен! Мы свяжемся с вами в ближайшее время.'
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Можно добавить дополнительный контекст
        return context


@method_decorator(csrf_exempt, name='dispatch')
class RequestKPView(View):
    """Обработка формы запроса КП из модального окна"""

    def post(self, request):
        # Очищаем номер телефона от маски
        post_data = request.POST.copy()
        if 'phone' in post_data:
            post_data['phone'] = re.sub(r'\D', '', post_data['phone'])

        # Добавляем тип запроса "КП"
        post_data['request_type'] = 'kp'

        form = ContactRequestForm(post_data)

        if form.is_valid():
            # Устанавливаем тип запроса "КП"
            contact_request = form.save(commit=False)
            contact_request.request_type = 'kp'
            contact_request.save()

            # Отправляем уведомление на email
            try:
                send_contact_notification(contact_request)
                # Отправляем автоматический ответ клиенту
                send_auto_reply(contact_request)
            except Exception as e:
                # Если email не отправился, все равно сохраняем запрос
                print(f"Ошибка при отправке email: {e}")

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
        phone_raw = '+77474818328'
        context = {
            'form': form,
            'contact_info': {
                'phone': '+7(747)481-83-28',
                'phone_raw': phone_raw,
                'phone_formatted': format_phone_number(phone_raw),
                'email': 'info@sitera.kz',
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
        # Очищаем номер телефона от маски
        post_data = request.POST.copy()
        if 'phone' in post_data:
            post_data['phone'] = re.sub(r'\D', '', post_data['phone'])

        # Добавляем тип запроса "Консультация" если не указан
        if 'request_type' not in post_data:
            post_data['request_type'] = 'consultation'

        form = ContactRequestForm(post_data)

        if form.is_valid():
            # Сохраняем форму
            contact_request = form.save()

            # Отправляем уведомление на email
            try:
                send_contact_notification(contact_request)
                # Отправляем автоматический ответ клиенту
                send_auto_reply(contact_request)
            except Exception as e:
                # Если email не отправился, все равно сохраняем запрос
                print(f"Ошибка при отправке email: {e}")

            # Если запрос AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.'
                })
            else:
                messages.success(
                    request,
                    'Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.'
                )
                return redirect('contacts:contact_page')
        else:
            # Если форма невалидна
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
            else:
                context = {
                    'form': form,
                    'contact_info': {
                        'phone': '+7(747)481-83-28',
                        'phone_raw': phone_raw,
                        'phone_formatted': format_phone_number(phone_raw),
                        'email': 'info@sitera.kz',
                        'address': 'Республика Казахстан, г. Астана, ул. Е 652, дом 12, НП 13',
                        'working_hours': 'Пн-Пт: 9:00 - 18:00',
                        'coordinates': {
                            'lat': 51.057761,
                            'lng': 71.423153
                        }
                    }
                }
                return render(request, 'contacts/contact_page.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class ConsultationRequestView(View):
    """Обработка формы запроса консультации с главной страницы"""

    def post(self, request):
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        organization = request.POST.get('organization', '').strip()
        message = request.POST.get('message', '').strip()

        # Очищаем номер телефона от маски
        phone = re.sub(r'\D', '', phone)

        # Валидация обязательных полей
        if not name or not phone:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Пожалуйста, заполните обязательные поля: имя и телефон.'
                })
            else:
                messages.error(
                    request, 'Пожалуйста, заполните обязательные поля: имя и телефон.')
                return redirect('/')

        # Создаем объект ContactRequest для сохранения в базе данных
        contact_request = ContactRequest(
            name=name,
            phone=phone,
            email=email,
            organization=organization,
            message=message,
            request_type='consultation'
        )
        contact_request.save()

        # Отправляем уведомление на email
        try:
            send_consultation_notification(
                name, phone, email, organization, message)
            # Отправляем автоматический ответ клиенту
            if email:  # Только если указан email
                send_auto_reply(contact_request)
        except Exception as e:
            # Если email не отправился, все равно обрабатываем форму
            print(f"Ошибка при отправке email: {e}")

        # Если запрос AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Ваша заявка успешно отправлена! Мы свяжемся с вами в ближайшее время.'
            })
        else:
            messages.success(
                request,
                'Ваша заявка успешно отправлена! Мы свяжемся с вами в ближайшее время.'
            )
            return redirect('/#contact')
