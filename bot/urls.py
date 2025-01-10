from django.urls import path
from .views import paystack_callback

urlpatterns = [
    path('paystack/callback/', paystack_callback, name='paystack_callback'),
]
