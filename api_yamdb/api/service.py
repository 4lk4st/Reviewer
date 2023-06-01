
import secrets

from django.core.mail import send_mail


def send_confirmation_email(email, confirmation_code):
    subject = 'Confirmation Code'
    message = f'Ваш код для получения токена: {confirmation_code}'
    sender = 'mr.iskhakov.r@yandex.ru'
    recipient_list = [email]
    send_mail(subject, message, sender, recipient_list)


def generate_confirmation_code(length=20):
    confirmation_code = secrets.token_hex(10)
    return confirmation_code
