from django.shortcuts import render, redirect, get_object_or_404
import braintree
from orders.models import Order
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from io import BytesIO
import weasyprint


def payment_process(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        nonce = request.POST.get('payment_method_nonce', None)
        result = braintree.Transaction.sale({
            'amount': f'{order.get_total_cost():.2f}',
            'payment_method_nonce': nonce,
            'options': {
                'submit_for_settlement': True
            }
        })
        if result.is_success:
            order.paid = True
            order.braintree_id = result.transaction.id
            order.save()

            subject = f'Mój sklep rachunek nr {order.id}'
            message = 'W załączniku przesyłamy rachunek dla ostatniego zakupu.'
            email = EmailMessage(subject,
                                 message,
                                 'admin@myshop.com',
                                 [order.email])
            html = render_to_string('orders/order/pdf.html', {'order': order})
            out = BytesIO()
            stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')]
            weasyprint.HTML(string=html).write_pdf(out,
                                                   stylesheets=stylesheets)
            email.attach(f'order_{order.id}',
                         out.getvalue(),
                         'application/pdf')
            email.send()
            return redirect('payment:done')
        else:
            return redirect('payment:canceled')
    else:
        client_token = braintree.ClientToken.generate()
        return render(request, 'payment/process.html', {
            'order': order,
            'client_token': client_token
        })

def payment_done(request):
    return render(request, 'payment/done.html')

def payment_canceled(request):
    return render(request, 'payment/canceled.html')
