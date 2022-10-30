#Author: Christoph Backhaus
#Date: 2022-10-30
#Version: 1.0.0
#Description: model for the nadooit api execution system. It contains the models for handling the executions of nadooit software.
#Compatibility: Django 4
#License: TBD



import uuid

# model imports
from nadooit_crm.models import Customer
from nadooit_hr.models import Employee
from nadooit_program_ownership_system.models import NadooitCustomerProgram

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
    
    # the customer program that was executed
    customer_program = models.ForeignKey(
        NadooitCustomerProgram, on_delete=models.SET_NULL, null=True
    )
    
    # creation date of the execution
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        return self.customer_program.program.name



@receiver(models.signals.post_save, sender=CustomerProgramExecution)
def cutomer_program_execution_was_created(sender, instance, created, *args, **kwargs):
    """
    
    a new execution is created, the time saved is charged to the time account of the customer that is assigned to the program.
    
    """
    
    if created:
        # reduce the customer_programs time_account by the program_time_saved_in_seconds
        
        # gets the customer program of the execution
        nadooit_customer_program = NadooitCustomerProgram.objects.get(id=instance.customer_program.id)
        
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
    obj = NadooitCustomerProgram.objects.get(id=instance.customer_program.id)
    obj.time_account.time_balance_in_seconds = (
        obj.time_account.time_balance_in_seconds
        + instance.program_time_saved_in_seconds
    )
    obj.time_account.save()

# This is a User Role. It can gives the user the right to create, delete customer program executions.
# Also it can give the user the right to give these rights to other users. 
class CustomerProgramExecutionManager(models.Model):
    # The employee that gets the rights
    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, primary_key=True
    )
    
    # If true the customer can create customer program executions
    can_create_customer_program_execution = models.BooleanField(default=False)
    
    # If true the customer can delete customer program executions
    can_delete_customer_program_execution = models.BooleanField(default=False)
    
    # If true the customer can give the rights to other users 
    can_give_customerprogramexecutionmanager_role = models.BooleanField(default=False)

    
    list_of_customers_the_manager_is_responsible_for = models.ManyToManyField(
        Customer, blank=True
    )

    # if display_name is not null, then use it, otherwise use username. if username is not null, then use it, otherwise use user_code
    def __str__(self):
        display_name = self.employee.user.display_name
        if display_name is not None:
            return display_name
        username = self.employee.user.username
        if username is not None:
            return username
        return self.employee.user.user_code
