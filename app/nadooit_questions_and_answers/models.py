import uuid
from django.db import models

# Create your models here.
class Question_Answer(models.Model):
    question_answer_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    question_answer_date = models.DateTimeField(auto_now_add=True)
    question_answer_question = models.TextField(blank=True)
    question_answer_answer = models.TextField(blank=True)

    def __str__(self):
        return self.question_answer_question + " " + self.question_answer_answer
