from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    price = models.FloatField()
    quantity = models.IntegerField()
    low_stock_threshold = models.IntegerField(default=10)

    def __str__(self):
        return self.name
