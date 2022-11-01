import uuid
from django.db import models

# Create your models here.
class Program(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)

    # program_dependencies is a list of programs that this program depends on. They are represented as a list of strings. The list is empty if there are no dependencies.
    program_dependencies = models.TextField(
        default="", blank=True, null=True, editable=True
    )

    def __str__(self):
        return self.name
