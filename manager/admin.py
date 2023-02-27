from django.contrib import admin
from . import models


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'date']
    list_filter = ['title', 'date']
    search_fields = ['date', 'title']


@admin.register(models.Photo)
class PhotosAdmin(admin.ModelAdmin):
    list_display = ['id', 'title',
                    'date', 'location']
    list_filter = ['id', 'title',
                   'date', 'location']
    search_fields = ['date', 'title']


@admin.register(models.Patrol)
class PatrolAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_filter = ['name']
    search_fields = ['name']


@admin.register(models.Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'date']
    list_filter = ['id', 'title', 'date']
    search_fields = ['date']
