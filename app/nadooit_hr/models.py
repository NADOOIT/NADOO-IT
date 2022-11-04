from datetime import datetime
from email.policy import default
import uuid
from django.db import models
from nadooit_auth.models import User
from nadooit_crm.models import Customer

# Create your models here.

# model for an employee
# an employee can work for multiple customers
# the relationship between an employee and a customer is defined by the EmployeeContract model
class Employee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # a customers field that shows what customers the employee is assigned to
    # customers_the_employee_works_for = models.ManyToManyField(Customer)

    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        display_name = self.user.display_name
        if display_name is not None:
            return display_name
        username = self.user.username
        if username is not None:
            return username
        return self.user.user_code


class EmployeeContract(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # the employee that is assigned to the customer
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    # the start date of the contract
    start_date = models.DateField(auto_now_add=True)

    # the end date of the contract
    end_date = models.DateField(null=True, blank=True)

    # if false the contract is not active and hidden from the frontend
    is_active = models.BooleanField(default=True)
    deactivation_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        return f"{self.employee} - {self.customer}"


class EmployeeManager(models.Model):

    # the employee that gets the manager role
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)

    # A list of all the customers the employee manager is assigned to
    list_of_customers_the_manager_is_responsible_for = models.ManyToManyField(
        Customer, blank=True
    )

    # A list of all the epmloyees that are managed by this manager
    list_of_employees_the_manager_has_given_the_role_to = models.ManyToManyField(
        Employee,
        blank=True,
        related_name="list_of_employees_the_employee_manager_has_given_the_role_to",
    )

    # if true, the employee manager can assign employees to customers
    can_add_new_employee = models.BooleanField(default=False)

    # if true, the employee manager can remove employees from customers
    can_delete_employee = models.BooleanField(default=False)

    # if true, the employee manager can give the role of employee manager to other employees
    can_give_manager_role = models.BooleanField(default=False)

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

    can_give_manager_role = models.BooleanField(default=False)

    list_of_customers_the_manager_is_responsible_for = models.ManyToManyField(
        Customer, blank=True
    )

    list_of_employees_the_manager_has_given_the_role_to = models.ManyToManyField(
        Employee,
        blank=True,
        related_name="list_of_employees_the_customer_manager_has_given_the_role_to",
    )

    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        if self.employee.user.display_name is not None:
            return self.employee.user.display_name
        return self.employee.user.user_code
