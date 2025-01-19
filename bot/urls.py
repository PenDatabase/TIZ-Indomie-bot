from django.urls import path
from django.views.generic.base import RedirectView
from .views import paystack_callback, get_order_details, home

urlpatterns = [
    path('', home, name="telegram_url"),
    path('paystack/callback/', paystack_callback, name='paystack_callback'),
    path("api/orders/<int:order_id>/", get_order_details, name="order-details"),
]
