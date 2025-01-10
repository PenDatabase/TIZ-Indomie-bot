import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Order

@csrf_exempt
def paystack_callback(request):
    """
    Handle Paystack's callback after payment.
    """
    if request.method == "GET":
        # Step 1: Extract reference and trxref from the URL parameters
        payment_reference = request.GET.get('reference')
        trxref = request.GET.get('trxref')
        order_id = request.GET.get("order_id")

        if not payment_reference or not trxref:
            return JsonResponse({'status': 'error', 'message': 'Missing reference or trxref.'}, status=400)

        # Step 2: Verify the payment using the Paystack API
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        }
        verification_url = f'https://api.paystack.co/transaction/verify/{trxref}'
        response = requests.get(verification_url, headers=headers)
        
        # Debugging response
        print("\n\nPaystack API Response:\n", response.text, "\n\n")
        payment_data = response.json()
        
        if payment_data['status'] and payment_data['data']['status'] == 'success':
            # Step 3: Update your order status to completed
            print("Order ID to verify:", order_id)  # Log order_id
            
            try:
                order = Order.objects.get(id=order_id)
                order.completed = True
                order.save()

               

                return JsonResponse({'status': 'success', 'message': 'Payment verified and order updated.'})
            except Order.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Order not found.'})
        else:
            # Handle failed payment
            try:
                order = Order.objects.get(reference=payment_reference)
                
            except (Order.DoesNotExist, UnboundLocalError):
                # Log error if order is not found
                print("Order not found for failed payment.")
            
            return JsonResponse({'status': 'error', 'message': 'Payment not successful.'})

    # If the request is not GET
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)
