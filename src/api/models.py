from django.utils import timezone
from django.db import models

import datetime


# Command to  add new migrations: python manage.py makemigrations api
# Command to save new migrations: python manage.py migrate
class ScheduledDate(models.Model):
    """
    Hour: 8 to 18,
    Date: day/month/year
    """
    date = models.DateTimeField('scheduled meeting')
    name = models.CharField(max_length=200)

    objects = models.Manager()

    def __str__(self):
        return str(self.date)
