import requests
import re
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.db import transaction
from .models import Order, Product, OrderItem

# telebot imports
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup




# Initialize the bot with the token
bot = telebot.TeleBot(settings.TOKEN)
website_link = settings.WEBSITE_LINK





def get_order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = OrderItem.objects.filter(order=order).select_related("product")
    data = {
        "id": order.id,
        "full_name": order.full_name,
        "hall": order.hall,
        "room_no": order.room_no,
        "items": [{"product": {"title": item.product.title}, "quantity": item.quantity} for item in items],
    }
    return JsonResponse(data)





@csrf_exempt
def paystack_callback(request):
    if request.method == "GET":
        payment_reference = request.GET.get("reference")
        trxref = request.GET.get("trxref")
        order_id = request.GET.get("order_id")

        if not payment_reference or not trxref:
            return JsonResponse({"status": "error", "message": "Missing reference or trxref."}, status=400)

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        }
        verification_url = f"https://api.paystack.co/transaction/verify/{trxref}"
        response = requests.get(verification_url, headers=headers)

        payment_data = response.json()

        if payment_data["status"] and payment_data["data"]["status"] == "success":
            try:
                order = Order.objects.get(id=order_id)
                with transaction.atomic():
                    order.payed = True
                    order.save()

                return render(
                    request,
                    "bot/payment_success.html",
                    {
                        "order_id": order.id,
                        "full_name": order.full_name,
                        "hall": order.hall,
                        "room_no": order.room_no,
                        "items": order.orderitem_set.select_related("product"),
                    },
                )
            except Order.DoesNotExist:
                return JsonResponse({"status": "error", "message": "Order not found."})
        else:
            error_message = payment_data.get("message", "Unknown error occurred.")
            return render(
                request,
                "bot/payment_failed.html",
                {"error_message": error_message, "reference": payment_reference},
            )

    return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)

