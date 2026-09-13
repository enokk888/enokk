from django.db import models
from django.contrib import admin
from django.utils import timezone
import datetime


class Question(models.Model):
    text = models.CharField(max_length=200)
    publication_date = models.DateTimeField("date published", default=timezone.now)

    @admin.display(
            boolean=True,
            ordering="publication_date",
            description="was published recently"
        )

    def was_published_recently(self):
        time = timezone.now()
        return time - datetime.timedelta(days=1) <= self.publication_date <= time

    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.text
        


