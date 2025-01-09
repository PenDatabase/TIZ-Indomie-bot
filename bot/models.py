from django.db import models



class Product(models.Model):
    title = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField(null=True)

    def __str__(self):
        return f"{self.id} - {self.title}"
    

class Order(models.Model):
    user_id = models.IntegerField()
    username = models.CharField(max_length=255)
    hall = models.CharField(max_length=255)
    romm_no = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.id} - username"
    

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.product}"