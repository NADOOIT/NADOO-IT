import uuid
from django.db import models


# Create your models here.
class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    street = models.CharField(max_length=255, null=True, blank=True)
    house_number = models.CharField(max_length=255, null=True, blank=True)
    town = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        return (
            self.street
            + " "
            + self.house_number
            + " "
            + self.town
            + " "
            + self.postal_code
        )


class ShippingAdress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    adress = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    addressed_to = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return (
            self.addressed_to
            + ", "
            + self.adress.street
            + " "
            + self.adress.house_number
            + ", "
            + self.adress.postal_code
            + " "
            + self.adress.town
        )


class BillingAdress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    adress = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    addressed_to = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return (
            self.addressed_to
            + ", "
            + self.adress.street
            + " "
            + self.adress.house_number
            + ", "
            + self.adress.postal_code
            + " "
            + self.adress.town
        )


class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)
    shipping_address = models.ForeignKey(
        ShippingAdress, on_delete=models.SET_NULL, null=True
    )
    billing_address = models.ForeignKey(
        BillingAdress, on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        return f"{self.name}"
