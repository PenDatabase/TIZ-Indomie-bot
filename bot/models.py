from django.db import models
import uuid



class Product(models.Model):
    title = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField(null=True)

    def __str__(self):
        return f"{self.id} - {self.title}"
    

class Order(models.Model):
    user_id = models.IntegerField()
    username = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    hall = models.CharField(max_length=255)
    room_no = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id} - username"

    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = self.username
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.product}"