from django.urls import reverse
from django.utils.translation import gettext as _
from django.db import models

""" hikes model """


class Hike(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    year = models.DateField(blank=False)
    date = models.DateField(blank=False)
    time = models.TimeField(blank=False)
    nights = models.PositiveIntegerField(blank=True, default=0)
    is_day = models.BooleanField(default=True)
    location = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.title} | {self.year.strftime("%Y")}'


"""camp model """


class Camp(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=False)
    date = models.DateField(blank=False)
    time = models.TimeField(blank=False)
    nights = models.PositiveIntegerField(blank=False)
    is_day = models.BooleanField(default=False)
    is_overseas = models.BooleanField(default=False)
    country = models.CharField(blank=True, max_length=50)
    location = models.CharField(blank=False, max_length=50)

    def __str__(self):
        return f'{self.title} | {self.date.strftime("%Y-%b")}'


""" project model """


class Project(models.Model):
    title = models.CharField(blank=False, max_length=255)
    description = models.TextField(blank=True)
    date = models.DateField(blank=False)
    time = models.TimeField(blank=False)
    location = models.CharField(blank=False, max_length=50)
    coordinator = models.CharField(blank=True, max_length=50)

    def __str__(self):
        return f'{self.title} | {self.date.strftime("%Y")}'


""" Badge model for badges """


class Badge(models.Model):
    level = models.PositiveIntegerField(blank=False, unique=True)
    name = models.CharField(max_length=255, blank=False, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Badge")
        verbose_name_plural = _("Badges")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("Badge_detail", kwargs={"pk": self.pk})


""" Requirement Model for requirements """


class Requirement(models.Model):
    number = models.PositiveIntegerField(blank=False)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Requirement")
        verbose_name_plural = _("Requirements")

    def __str__(self):
        return (f'({self.badge.level},{self.number}) {self.name}')

    def get_absolute_url(self):
        return reverse("Requirement_detail", kwargs={"pk": self.pk})
