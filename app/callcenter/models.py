import uuid
from django.db import models

# Create your models here.
from django.db import models
from nadooit_website.models import Session
from nadooit_auth.models import User
from nadooit_hr.models import EmployeeContract


class CallCenterWorkerContract(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_contract = models.OneToOneField(EmployeeContract, on_delete=models.CASCADE)
    is_active_worker = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"CallCenter Worker Contract: {self.employee_contract.employee} - {self.employee_contract.customer}"


class CallCenterManagerContract(models.Model):
    contract = models.OneToOneField(EmployeeContract, on_delete=models.CASCADE)

    # If true, the call center manager can create CallCenterWorkerContracts
    can_create_worker_contract = models.BooleanField(default=False)

    # If true, the call center manager can deactivate CallCenterWorkerContracts
    can_deactivate_worker_contract = models.BooleanField(default=False)

    # If true, the call center manager can promote other employees to CallCenterManager
    can_promote_to_manager = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    def __str__(self) -> str:
        return f"CallCenterManagerContract between: {self.contract.employee} - {self.contract.customer}"

    def get_abilities(self):
        return {
            "can_create_worker_contract": self.can_create_worker_contract,
            "can_deactivate_worker_contract": self.can_deactivate_worker_contract,
            "can_promote_to_manager": self.can_promote_to_manager,
        }


class MeetingRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, null=True, blank=True
    )  # Make session optional
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True
    )  # Make user optional
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("accepted", "Accepted"),
            ("denied", "Denied"),
        ],
        default="pending",
    )

    def __str__(self):
        if self.session:
            return f"{self.session} - {self.status}"
        elif self.user:
            return f"{self.user} - {self.status}"
        else:
            return f"{self.id} - {self.status}"
