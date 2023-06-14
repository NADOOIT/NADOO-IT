from django.db import models

from nadooit_crm.models import Customer


# Create your models here.
class Item(models.Model):
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(max_length=100)
    quantity_available = models.BigIntegerField()
    minimum_quantity = models.BigIntegerField()
    location = models.CharField(max_length=100)
    delivery_options = models.TextField()
    link = models.URLField()
    img_link = models.URLField()

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Item {self.pk}"
