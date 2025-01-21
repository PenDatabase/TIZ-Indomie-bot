from django.urls import path
from django.views.generic.base import RedirectView
from .views import paystack_callback, get_order_details, home, admin_register

urlpatterns = [
    path('', home, name="home"),
    path('admin_register/', admin_register, name="admin_register"),
    path('telegram_bot/', RedirectView.as_view(url="https://t.me/cu_indomie_guy_bot", permanent=True), name="telegram_url"),
    path('paystack/callback/', paystack_callback, name='paystack_callback'),
    path("api/orders/<int:order_id>/", get_order_details, name="order-details"),
]