from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import re


def format_phone_number(phone):
    """
    Форматирует номер телефона в читаемый вид: +7 (777) 123-45-67
    """
    if not phone:
        return phone

    # Удаляем все нецифровые символы
    digits = re.sub(r'\D', '', phone)

    # Если начинается с 8, заменяем на 7
    if digits.startswith('8'):
        digits = '7' + digits[1:]

    # Если начинается с +7, убираем +
    if digits.startswith('+7'):
        digits = digits[2:]

    # Если начинается с 7, оставляем как есть, иначе добавляем 7
    if not digits.startswith('7'):
        digits = '7' + digits

    # Форматируем в +7 (777) 123-45-67
    if len(digits) >= 11:
        return f"+{digits[0]} ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"

    # Если не удалось отформатировать, возвращаем оригинальный номер
    return phone


def send_contact_notification(contact_request):
    """
    Отправляет уведомление о новом запросе на почту info@sitera.kz
    """
    subject = f"Новый запрос: {contact_request.get_request_type_display()} от {contact_request.name}"

    # Формируем контекст для шаблона
    context = {
        'contact_request': contact_request,
        'request_type_display': contact_request.get_request_type_display(),
        'product_info': f" ({contact_request.product.title})" if contact_request.product and contact_request.product.title else "",
        'formatted_phone': format_phone_number(contact_request.phone)
    }

    # Рендерим HTML шаблон
    html_message = render_to_string(
        'contacts/email/notification.html', context)

    # Создаем текстовую версию
    text_message = strip_tags(html_message)

    try:
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.NOTIFICATION_EMAIL],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Ошибка при отправке email: {e}")
        return False


def send_auto_reply(contact_request):
    """
    Отправляет автоматический ответ клиенту
    """
    if not contact_request.email:
        return False

    subject = "Ваш запрос получен - Sitera"

    # Формируем контекст для шаблона
    context = {
        'contact_request': contact_request,
        'request_type_display': contact_request.get_request_type_display(),
    }

    # Рендерим HTML шаблон
    html_message = render_to_string('contacts/email/auto_reply.html', context)

    # Создаем текстовую версию
    text_message = strip_tags(html_message)

    try:
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[contact_request.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Ошибка при отправке auto-reply email: {e}")
        return False


def send_consultation_notification(name, phone, email, organization, message):
    """
    Отправляет уведомление о запросе консультации с главной страницы
    """
    subject = f"Запрос консультации от {name}"

    # Формируем контекст для шаблона
    context = {
        'name': name,
        'phone': phone,
        'email': email,
        'organization': organization,
        'message': message,
        'request_type': 'Консультация с главной страницы',
        'formatted_phone': format_phone_number(phone)
    }

    # Рендерим HTML шаблон
    html_message = render_to_string(
        'contacts/email/consultation_notification.html', context)

    # Создаем текстовую версию
    text_message = strip_tags(html_message)

    try:
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.NOTIFICATION_EMAIL],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Ошибка при отправке email консультации: {e}")
        return False
