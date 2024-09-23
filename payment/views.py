from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
import braintree
import weasyprint
from django.urls import reverse

from orders.models import Order

from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from io import BytesIO

from payment.models import Payment
from shop.services import BelizeBankPaymentGateway, BelizeBankPaymentGatewayError


# Create your views here.
def payment_process(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)

    payment = Payment.objects.filter(order=order).first()

    if not payment:
        payment = Payment.objects.create(order=order, amount=order.get_total_cost())

        gateway = BelizeBankPaymentGateway(
            username=settings.BELIZE_BANK_USERNAME,
            password=settings.BELIZE_BANK_PASSWORD,
            mode=settings.BELIZE_BANK_MODE
        )

        try:
            payment_response = gateway.authorize_payment(
                amount=int(payment.amount * 100),  # Convert to cents
                order_number=str(payment.order.id),
                return_url=request.build_absolute_uri(reverse('payment:payment_status', args=[payment.id]))
            )
            payment.transaction_id = payment_response['orderId']
            payment.payment_url = payment_response['formUrl']
            payment.save()
            return render(request, 'payment/process.html', {'payment': payment})
        except BelizeBankPaymentGatewayError as e:
            payment.status = 'Failed'
            payment.save()
            return JsonResponse({'error': str(e)}, status=400)
    return render(request, 'payment/process.html', {'payment': payment})


def payment_status(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)

    if payment.status in ['Paid', 'Failed']:
        return JsonResponse({'status': payment.status})

    gateway = BelizeBankPaymentGateway(
        username=settings.BELIZE_BANK_USERNAME,
        password=settings.BELIZE_BANK_PASSWORD,
        mode=settings.BELIZE_BANK_MODE
    )

    try:
        status_response = gateway.get_payment_status(payment.transaction_id)
        order_status = status_response.get('orderStatus')


        status_mapping = {
            0: 'Registered but not paid',
            1: 'Pre-authorized amount on hold',
            2: 'Fully authorized',
            3: 'Canceled',
            4: 'Refunded',
            5: 'Authorization procedure initiated',
            6: 'Authorization declined'
        }

        payment.status = status_mapping.get(order_status, 'Unknown')
        payment.save()
        return JsonResponse({'status': payment.status})
    except BelizeBankPaymentGatewayError as e:
        return JsonResponse({'error': str(e)}, status=400)
    
def payment_done(request):
       return render(request, 'payment/done.html')
def payment_canceled(request):
       return render(request, 'payment/canceled.html')