from django.contrib import admin
from . import models
# Register your models here.


@admin.register(models.Camp)
class CampAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'nights']
    list_filter = ['title', 'date', 'nights']
    search_fields = ['title', 'date']


@admin.register(models.Hike)
class HikeAdmin(admin.ModelAdmin):
    list_display = ['title',  'year',
                    'date', 'time', 'nights']
    list_filter = ['title',  'year',
                   'date', 'time', 'nights']
    search_fields = ['title', 'date']


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'time', 'location',]
    list_filter = ['title', 'date', 'time', 'location',]
    search_fields = ['title', 'date']


@admin.register(models.Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = ['name', 'number', ]
    list_filter = ['name', 'number', ]
    search_fields = ['name']


@admin.register(models.Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['level', 'name', 'description']
    list_filter = ['level', 'name']
    search_fields = ['date', 'name']
