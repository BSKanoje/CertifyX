from django.db import models
from django.conf import settings


class Candidate(models.Model):
    company = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    course_title = models.CharField(max_length=200)
    college = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.name
