from django.contrib import admin
from . import models


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'date']
    list_filter = ['id', 'title', 'date']


@admin.register(models.Photo)
class PhotosAdmin(admin.ModelAdmin):

    list_display = ['id', 'title',
                    'date', 'location']
    list_filter = ['id', 'title',
                   'date', 'location']


@admin.register(models.Patrol)
class PatrolAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_filter = ['id', 'name']


@admin.register(models.Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'date']
    list_filter = ['id', 'title', 'date']
