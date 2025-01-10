from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from django.conf import settings
from .models import Order  # Import your models as necessary
from telebot import TeleBot  # Import PyTelegramAPI (Assuming you have initialized your bot)

# Initialize the bot
bot = TeleBot(token=settings.TELEGRAM_BOT_TOKEN)  # Your bot token from BotFather

@csrf_exempt
def paystack_callback(request):
    """
    Handle Paystack's callback after payment.
    """
    if request.method == "POST":
        # Step 1: Verify the payment using the Paystack API
        data = request.POST
        payment_reference = data.get('reference')
        
        # Make a request to Paystack's API to verify the payment
        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        }
        verification_url = f'https://api.paystack.co/transaction/verify/{payment_reference}'
        response = requests.get(verification_url, headers=headers)
        payment_data = response.json()
        
        if payment_data['status'] and payment_data['data']['status'] == 'success':
            # Step 2: Update your order status to completed
            order_id = payment_data['data']['order_id']
            try:
                order = Order.objects.get(id=order_id)
                order.completed = True
                order.save()

                # Step 3: Notify the user of the successful payment via Telegram bot
                user_id = order.user_id  # Assuming you store the user_id with the order
                bot.send_message(user_id, "Your payment was successful! Your order is now complete.")
                
                return JsonResponse({'status': 'success', 'message': 'Payment verified and order updated.'})
            except Order.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Order not found.'})
        else:
            # Step 4: If payment is not successful, notify the user
            user_id = order.user_id  # Assuming you store the user_id with the order
            bot.send_message(user_id, "Your payment was not successful. Please try again.")
            return JsonResponse({'status': 'error', 'message': 'Payment not successful.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})
