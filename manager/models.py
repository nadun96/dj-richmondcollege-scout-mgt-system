
# from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from django.db import models


class Photo(models.Model):
    """  home photo page """
    title = models.CharField(max_length=50, blank=False)
    description = models.TextField()
    date = models.DateField(blank=False)
    location = models.CharField(max_length=50, blank=False)
    file = models.ImageField(upload_to='photos', blank=False)

    def __str__(self):
        return self.title


class Post(models.Model):
    """  saturday posts """
    title = models.CharField(max_length=100, blank=False)
    description = models.TextField()
    date = models.DateField(auto_now_add=True, blank=False)
    file = models.FileField(upload_to='posts/files', blank=True)
    picture = models.ImageField(upload_to='posts/image', blank=True)

    def __str__(self):
        return f'{self.id} | {self.date}'


class Patrol(models.Model):
    """  patrol model """
    name = models.CharField(max_length=50, blank=False, unique=True)

    def __str__(self):
        return self.name

    # start = models.DateField(auto_now_add=True, blank=False)
    # end = models.DateField(blank=True, null=True)
    # is_active = models.BooleanField(default=True)


class Communication(models.Model):
    """  Send model with abstract class for sending messages and announcements """
    class Meta:
        abstract = True


class Announcement(Communication):
    """ Model Announcements for members """
    title = models.CharField(max_length=50, blank=False)
    content = models.TextField(blank=False)
    date = models.DateField(auto_now_add=True, blank=False)
    file = models.FileField(upload_to='announce', blank=True)

    def __str__(self):
        return self.title
