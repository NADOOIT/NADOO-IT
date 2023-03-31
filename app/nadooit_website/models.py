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


class Section(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    time_spend_reading = models.IntegerField(default=0)

    def __str__(self):
        return self.title


# The page is build over time. To build the page a number of sections are needed.
# The order of the sections is dynamic and is algorithmically determined.
# Each order is saved in the database. The best order is the one with the highest score.
# The score is calculated by the number of visits to the page and the number of visits to the sections.
# The goal is to find the best order of the sections.
# To do this, the sections are randomly ordered in experiments.
# Groups of these orders then compete against each other.
# Over time the best order is found.
# The best order is then used to build the page.
# The best order is the one with the highest score.
# The goal of the page is to get the visitor to the end of the page or directly to the contact form.
# The contact form is at the end of the page and in the middle of the navigation bar.
# The navigation bar is at the top of the page.
# Getting the visitor to click on either the contact form or the navigation bar is the goal and is rewarded with a higher score.


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    # the sections in the order
    sections = models.ManyToManyField(Section)
    # the score of the order
    score = models.IntegerField(default=0)
    # the number of visits to the order
    visits = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id)


class Htmx_session(models.Model):
    id = models.AutoField(primary_key=True)
    # the sections in the order
    sections = models.ManyToManyField(Section)
    # the score of the order
    score = models.IntegerField(default=0)
    # the number of visits to the order
    visits = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id)
