# Author: Christoph Backhaus
# Date: 2022-10-30
# Version: 1.0.0
# Description: model for the nadooit api execution system. It contains the models for handling the executions of nadooit software.
# Compatibility: Django 4
# License: TBD


import uuid

# model imports
from nadooit_crm.models import Customer
from nadooit_hr.models import Employee
from nadooit_program_ownership_system.models import CustomerProgram

# django imports
from django.dispatch import receiver
from django.db import models


# Create your models here.


# model for a single execution of a nadooit program.
# it records how much time was saved by the program.
class CustomerProgramExecution(models.Model):
    """_summary_
    model for a single execution of a nadooit program.
    """

    # id of the execution
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # time saved by the program in seconds
    program_time_saved_in_seconds = models.IntegerField(default=0)

    # price at the time of the execution for the program
    price_per_second_in_cent_at_the_time_of_execution = models.IntegerField(default=0)

    # the customer program that was executed
    customer_program = models.ForeignKey(
        CustomerProgram, on_delete=models.SET_NULL, null=True
    )

    # creation date of the execution
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        return self.customer_program.program.name

    def price_for_execution(self):
        return (
            self.price_per_second_in_cent_at_the_time_of_execution
            * self.program_time_saved_in_seconds
        )


@receiver(models.signals.post_save, sender=CustomerProgramExecution)
def cutomer_program_execution_was_created(sender, instance, created, *args, **kwargs):
    """

    a new execution is created, the time saved is charged to the time account of the customer that is assigned to the program.

    """

    if created:
        # reduce the customer_programs time_account by the program_time_saved_in_seconds

        # gets the customer program of the execution
        nadooit_customer_program = CustomerProgram.objects.get(
            id=instance.customer_program.id
        )

        # gets the time account of the customer program and reduces it by the time saved by the program
        nadooit_customer_program.time_account.time_balance_in_seconds = (
            nadooit_customer_program.time_account.time_balance_in_seconds
            - instance.program_time_saved_in_seconds
        )
        print("nadooit_customer_program.time_account.time_balance_in_seconds")
        nadooit_customer_program.time_account.save()


@receiver(models.signals.post_delete, sender=CustomerProgramExecution)
def customer_program_execution_was_deleted(sender, instance, *args, **kwargs):
    """
        Whenever a customer program execution is deleted this signal is triggered.

    Args:
        sender (_type_): _description_
        instance (_type_): _description_
    """

    # increase the customer_programs time_account by the program_time_saved_in_seconds
    obj = CustomerProgram.objects.get(id=instance.customer_program.id)
    obj.time_account.time_balance_in_seconds = (
        obj.time_account.time_balance_in_seconds
        + instance.program_time_saved_in_seconds
    )
    obj.time_account.save()
