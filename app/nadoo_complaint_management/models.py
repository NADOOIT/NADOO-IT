import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from nadooit_api_executions_system.models import CustomerProgramExecution
from nadooit_hr.models import Employee

# Create your models here.


# A complaint is a message from a customer program execution manager to the creator of the customer program
# The complaint is about the customer program execution
class Complaint(models.Model):

    # This model is used to store diffent possivle states of a complaint that can be made by a customer
    class ComplaintStatus(models.TextChoices):
        OPEN = "OPEN", _("Open")
        IN_PROGRESS = "IN_PROGRESS", _("In Progress")
        CLOSED = "CLOSED", _("Closed")
        REJECTED = "REJECTED", _("Rejected")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # the customer program execution that is complained about
    customer_program_execution = models.ForeignKey(
        CustomerProgramExecution, on_delete=models.SET_NULL, null=True
    )

    # the complaint itself
    complaint = models.TextField()

    # the customer program execution manager that created the complaint
    customer_program_execution_manager = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True
    )

    # the current status of the complaint (open, closed, denied, etc.)
    status = models.CharField(
        max_length=20, choices=ComplaintStatus.choices, default=ComplaintStatus.OPEN
    )

    # the date the complaint was created
    created_at = models.DateTimeField(auto_now_add=True, editable=True)

    # the date the complaint was updated
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self):
        # the name of the customer program
        return (
            "Status: "
            + self.status
            + " Customer Program: "
            + self.customer_program_execution.customer_program.program.name
            + " Customer: "
            + self.customer_program_execution.customer_program.customer.name
            + " Customer Program Execution Manager: "
            + self.customer_program_execution_manager.user.display_name
        )
