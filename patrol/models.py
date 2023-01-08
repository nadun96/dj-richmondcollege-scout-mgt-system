from django.db import models

# Create your models here.
from django.db import models
from core.models import Profile


class Attendance(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    marker = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='marker')
    date = models.DateField(auto_now_add=True)
    member = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='member')
    time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return self.title
