import uuid
from django.db import models

# Create your models here.
# create a model for someone visiting the site
# the visit holds the date and time of the visit and the site the visitor visited
class Visit(models.Model):
    # the date and time of the visit
    visit_date = models.DateTimeField(auto_now_add=True)
    # the site the visitor visited
    site = models.CharField(max_length=200)

    # the string representation of the visit
    def __str__(self):
        return self.visit_date.strftime("%Y-%m-%d %H:%M:%S") + " " + self.site


# Session
"""     session_id
        session_start_time
        session_end_time
        session_score
        session_duration
        session_section_order 
        session_made_appointment
"""


class Session(models.Model):
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_start_time = models.DateTimeField(auto_now_add=True)
    session_end_time = models.DateTimeField(auto_now_add=True)
    session_score = models.IntegerField()
    session_duration = models.IntegerField()
    session_section_order = models.CharField(max_length=200)
    session_made_appointment = models.BooleanField(default=False)

    def __str__(self):
        return (
            self.session_id
            + " "
            + self.session_start_time.strftime("%Y-%m-%d %H:%M:%S")
            + " "
            + self.session_end_time.strftime("%Y-%m-%d %H:%M:%S")
            + " "
            + str(self.session_score)
            + " "
            + str(self.session_duration)
            + " "
            + self.session_section_order
            + " "
            + str(self.session_made_appointment)
        )


# Section
"""     
    Section
    section_id a unique id for the section
    section_name a name generated from the section to be displayed
    section_html the html code of the section
"""


class Section(models.Model):
    section_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section_name = models.CharField(max_length=200)
    section_html = models.CharField(max_length=200)


# Section_Transition Test
"""
This model is used to store the test results for a section transition test
Each section transition Test consists of 2 sections
It stores the order of the ids of the the first section the visitor sees and the second section the visitor sees
It is to keep track how likely the visitor will continue to the next section after seeing the first section

    section_test_id
    section_test_date
    sectoin_test_time
    section_1_id
    section_2_id
    transition_percentage
"""


class Section_Transition_Test(models.Model):
    section_test_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    section_test_date = models.DateTimeField(auto_now_add=True)
    section_test_time = models.DateTimeField(auto_now_add=True)
    section_1_id = models.UUIDField()
    section_2_id = models.UUIDField()
    transition_percentage = models.IntegerField()

    def __str__(self):
        return (
            self.section_test_id
            + " "
            + self.section_test_date.strftime("%Y-%m-%d %H:%M:%S")
            + " "
            + self.section_test_time.strftime("%Y-%m-%d %H:%M:%S")
            + " "
            + self.section_1_id
            + " "
            + self.section_2_id
            + " "
            + str(self.transition_percentage)
        )
