from django.db import models



class Product(models.Model):
    title = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField(null=True)

    def __str__(self):
        return f"{self.id} - {self.title}"
    

class Order(models.Model):
    user_id = models.BigIntegerField()
    username = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    hall = models.CharField(max_length=255)
    room_no = models.CharField(max_length=255)
    payed = models.BooleanField(default=False)
    delivery_status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id} - {self.username}"

    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = self.username
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"Product: {self.product.title}, Quantity: {self.quantity}, Order ID: {self.order.id}"
    

class Reciept(models.Model):
    trxref = models.CharField(max_length=255)
    order_id = models.CharField(max_length=255)
    reference = models.CharField(max_length=255)
