import uuid
from django.db import models

from nadooit_crm.models import Customer
from nadooit_hr.models import Employee

def get_time_as_string_in_hour_format_for_time_in_seconds_as_integer(time):
    return str(time // 3600) + ':' + str((time % 3600) // 60) + ':' + str(time % 60)


# Create your models here.
class TimeAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    time_balance_in_seconds = models.BigIntegerField(null=True, blank=True, default=0)
    
    def __str__(self):	
        return get_time_as_string_in_hour_format_for_time_in_seconds_as_integer(self.time_balance_in_seconds) + ' ' + str(self.id)	 

class TimeAccountEmployee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    time_account = models.ForeignKey(TimeAccount, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)
    def __str__(self):
        if self.employee.user.display_name == "":
            return self.employee.user.user_code + ' ' + get_time_as_string_in_hour_format_for_time_in_seconds_as_integer(self.time_account.time_balance_in_seconds)
        else:
            return self.employee.user.display_name + ' ' + get_time_as_string_in_hour_format_for_time_in_seconds_as_integer(self.time_account.time_balance_in_seconds)

class CustomerNadooitTimeAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    time_account = models.ForeignKey(TimeAccount, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)
    def __str__(self):
        return self.customer.name + ' ' + get_time_as_string_in_hour_format_for_time_in_seconds_as_integer(self.time_account.time_balance_in_seconds)	
    
class WorkTimeAccountEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    time_account = models.ForeignKey(TimeAccountEmployee, on_delete=models.CASCADE)
    work_time = models.TimeField(null=True, blank=True)
    work_date = models.DateField(null=True, blank=True)
    ENTRY_TYPE = (
        ('IN', 'IN'),
        ('OUT', 'OUT'),
    )
    entry_trype = models.CharField(max_length=3, choices=ENTRY_TYPE, default='IN')
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)
    def __str__(self):
        if self.time_account.employee.user.display_name == "":
            return self.work_time.strftime('%H:%M') + ' ' + self.work_date.strftime('%Y-%m-%d') + ' ' + self.entry_trype + ' ' + self.time_account.customer.name + ' ' + self.time_account.employee.user.user_code
        else:
            return self.work_time.strftime('%H:%M') + ' ' + self.work_date.strftime('%Y-%m-%d') + ' ' + self.entry_trype + ' ' + self.time_account.customer.name + ' ' + self.time_account.employee.user.display_name