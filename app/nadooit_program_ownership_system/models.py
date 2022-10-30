import uuid
from django.db import models
from nadooit_crm.models import Customer
from nadooit_program.models import NadooitProgram
from nadooit_time_account.models import TimeAccount
from nadooit_hr.models import Employee


# Create your models here.


class NadooitProgramShare(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    share_of = models.ForeignKey(NadooitProgram, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        return self.id


class NadooitCustomerProgram(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program_time_saved_per_execution_in_seconds = models.IntegerField(default=0)

    # TODO this relation means that every program can only be assigned to one time account. This is not correct. A program can be assigned to multiple time accounts.
    time_account = models.ForeignKey(TimeAccount, on_delete=models.SET_NULL, null=True)
    over_charge = models.BooleanField(default=False)
    program = models.ForeignKey(NadooitProgram, on_delete=models.SET_NULL, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        return str(self.id) + " " + self.program.name


class NadooitCustomerProgramManager(models.Model):
    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, primary_key=True
    )
    can_create_customer_program = models.BooleanField(default=False)
    can_delete_customer_program = models.BooleanField(default=False)

    list_of_customers_the_manager_is_responsible_for = models.ManyToManyField(
        Customer, blank=True
    )

    def __str__(self):
        display_name = self.employee.user.display_name
        if display_name is not None:
            return display_name
        username = self.employee.user.username
        if username is not None:
            return username
        return self.employee.user.user_code
