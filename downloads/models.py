from django.db import models
from django.utils import timezone
import datetime


class TrustedFile(models.Model):
    file = models.FileField(upload_to="downloads")
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="download_images")
    description = models.TextField(max_length=1000, default=f"description")
    developer_notes = models.TextField(max_length=1000, default=f"developer notes")
    publication_date = models.DateTimeField("date published")
    last_update_date = models.DateTimeField("latest update")
    download_count = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)

    def was_published_recently(self):
        time = timezone.now()
        return time - datetime.timedelta(days=30) <= self.publication_date <= time

    def was_updated_recently(self):
        time = timezone.now()
        return time - datetime.timedelta(days=30) <= self.last_update_date <= time

    def __str__(self):
        return self.title
