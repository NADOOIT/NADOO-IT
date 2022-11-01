import uuid
from django.db import models
from nadooit_auth.models import User
from nadooit_crm.models import Customer

# Create your models here.


class Employee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # a customers field that shows what customers the employee is assigned to
    customers_the_employee_works_for = models.ManyToManyField(Customer)

    def __str__(self):
        display_name = self.user.display_name
        if display_name is not None:
            return display_name
        username = self.user.username
        if username is not None:
            return username
        return self.user.user_code


class EmployeeManager(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    
    list_of_customers_the_manager_is_responsible_for = models.ManyToManyField(
        Customer, blank=True
    )

    list_of_employees_the_manager_has_given_the_role_to = models.ManyToManyField(
        Employee, blank=True, related_name="list_of_employees_the_employee_manager_has_given_the_role_to"
    )
    
    can_give_EmployeeManager_role = models.BooleanField(default=False)

    def __str__(self):
        display_name = self.employee.user.display_name
        if display_name is not None:
            return display_name
        username = self.employee.user.username
        if username is not None:
            return username
        return self.employee.user.user_code


class CustomerManager(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    
    can_give_CustomerManager_role = models.BooleanField(default=False)
    
    list_of_customers_the_manager_is_responsible_for = models.ManyToManyField(
        Customer, blank=True
    )
    
    list_of_employees_the_manager_has_given_the_role_to = models.ManyToManyField(
    Employee, blank=True, related_name="list_of_employees_the_customer_manager_has_given_the_role_to"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        if self.employee.user.display_name is not None:
            return self.employee.user.display_name + " - " + self.customer.name
        return self.employee.name + " " + self.customer.name
