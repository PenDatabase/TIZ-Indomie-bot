from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError




class Product(models.Model):
    title = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField(null=True)

    def __str__(self):
        return f"{self.id} - {self.title}"
    



class DeliveryDate(models.Model):
    date = models.DateField()

    def __str__(self):
        return f"{self.date.strftime('%A, %B %d %Y')}"
    
    def clean(self):
        super().clean()

        if DeliveryDate.objects.exists() and self.id not in DeliveryDate.objects.values_list("id", flat=True):
            raise ValidationError("You cannot create more than one Delivery date at a time, Please Modify the existing date")
        if self.date < timezone.now().date():
            raise ValidationError({"date": "Deliver Date must be today's date or farther in time"})
    


class Order(models.Model):
    user_id = models.BigIntegerField()
    username = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    hall = models.CharField(max_length=255)
    room_no = models.CharField(max_length=255)
    payed = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    delivery_date = models.ForeignKey(DeliveryDate, on_delete=models.PROTECT, null=True, default=True)

    def __str__(self):
        return f"Order #{self.id}"

    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = self.username
            self.delivery_date = DeliveryDate.objects.order_by("-id").first()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"Product: {self.product.title}, Quantity: {self.quantity}, Order ID: {self.order.id}"
    

class Reciept(models.Model):
    trxref = models.CharField(max_length=255)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, )
    reference = models.CharField(max_length=255)


