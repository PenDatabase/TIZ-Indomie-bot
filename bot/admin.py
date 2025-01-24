from django.contrib import admin
from .models import Product, Order, OrderItem, DeliveryDate, Reciept

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(DeliveryDate)
admin.site.register(Reciept)
