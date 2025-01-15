from django.urls import path
from .views import paystack_callback, telegram_webhook, get_order_details

urlpatterns = [
    path('paystack/callback/', paystack_callback, name='paystack_callback'),
    path('webhook', telegram_webhook, name="telegram_webhook"),
    path("api/orders/<int:order_id>/", get_order_details, name="order-details"),
]
