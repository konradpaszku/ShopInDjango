from celery import shared_task
from django.core.mail import send_mail
from .models import Order


@shared_task(bind=True)
def order_created(self, order_id):
    """Zadanie wysyłające powiadomienie za pomocą wiadomości email
    po zakończonym powodzeniem utworzeniu obiektu zamówienia"""
    order = Order.objects.all(id=order_id)
    subject = f'Zamówienie nr {order.id}'
    message = f'Witaj, {order.first_name}\n\n Złożyłeś zamówienie w naszym sklepie. Identyfikator zamówienia to {order.id}'
    mail_sent = send_mail(subject, message, 'admin@myshop.com', [order.email])

    return mail_sent
