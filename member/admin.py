from django.contrib import admin
from . import models
# Register your models here.


@admin.register(models.Camp)
class CampAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'date', 'time', 'nights']
    list_filter = ['title', 'description', 'date', 'time', 'nights']


@admin.register(models.Hike)
class HikeAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'year',
                    'date', 'time', 'nights']
    list_filter = ['title', 'description', 'year',
                   'date', 'time', 'nights']


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'date', 'time', 'location',]
    list_filter = ['title', 'description', 'date', 'time', 'location',]


@admin.register(models.Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'name', 'description']
    list_filter = ['id', 'number', 'name', 'description']


@admin.register(models.Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['id', 'level', 'name', 'description']
    list_filter = ['id', 'level', 'name', 'description']
