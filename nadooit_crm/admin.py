from django.contrib import admin

from nadooit_crm.models import Address, BillingAdress, Customer,  Employee, ShippingAdress

class CustomerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Customer._meta.fields]


class AddressAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Address._meta.fields]


# Register your models here.
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(ShippingAdress)
admin.site.register(BillingAdress)	
admin.site.register(Employee)