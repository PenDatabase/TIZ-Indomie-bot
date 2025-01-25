from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, F, Sum, Q
from .models import Product, Order, OrderItem, DeliveryDate, Reciept


class ProductAdmin(admin.ModelAdmin):
    list_display = ["title", "price", "payed_quantity"]

    def payed_quantity(self, order):
        return order.payed_quantity

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            payed_quantity = Sum(
                "orderitem__quantity",
                filter=Q(orderitem__order__payed=True)
            )
        )


admin.site.register(Product, ProductAdmin)




class OrderAdmin(admin.ModelAdmin):
    exclude = ["payed"] # to exclude payed boolean value from list of fields admin can change
    list_display = ["__str__", "delivered", "full_name", "hall", "room_no", "delivery_date", "payed"]
    list_editable = ["delivered"]
    list_filter = ["payed", "delivered", "hall"]

admin.site.register(Order, OrderAdmin)


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "product__title", "quantity"]

admin.site.register(OrderItem, OrderItemAdmin)


class DeliveryDateAdmin(admin.ModelAdmin):
    list_display = ["__str__", "date", ]
    list_editable = ["date"]
    
admin.site.register(DeliveryDate, DeliveryDateAdmin)


class RecieptAdmin(admin.ModelAdmin):
    exclude = ["trxref", "reference", "order"]
    list_display = ["order", "transaction_reference", "payment_reference"]

    def transaction_reference(self, reciept):
        return format_html("<span style='color: rgb(164, 235, 72);'>{}</span>", reciept.trxref)

    def payment_reference(self, reciept):
        return format_html("<span style='color: rgb(164, 235, 72);'>{}</span>", reciept.reference)

admin.site.register(Reciept, RecieptAdmin)
