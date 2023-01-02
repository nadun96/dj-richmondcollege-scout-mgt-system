from django.contrib import admin
from . import models


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'pk', 'is_mem', 'is_skr', 'is_sec', 'is_ldr']
    list_filter = ['username', 'is_mem', 'is_skr', 'is_sec', 'is_ldr']


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'surname',
                    'entrance_number', 'email', 'birthday', 'contact']
    list_filter = ['id', 'user', 'surname',
                   'entrance_number', 'email', 'birthday', 'contact']


@admin.register(models.Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'id',  'address', 'telephone', 'email']
    list_filter = ['id', 'name']


@admin.register(models.UserFile)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['user', 'id']
    list_filter = ['id']


@admin.register(models.MemberRole)
class UserRolesAdmin(admin.ModelAdmin):
    list_display = ['id', 'profile', 'role',  'active', 'start', 'end']
    list_filter = ['id', 'profile', 'role',  'active', 'start', 'end']


@admin.register(models.Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'receiver', 'date']
    list_filter = ['id', 'sender', 'receiver', 'date']


@admin.register(models.MembershipFee)
class MembershipFeeAdmin(admin.ModelAdmin):
    list_display = ['id', 'member', 'amount', 'for_year', 'date', 'is_paid']
    list_filter = ['id', 'member', 'amount', 'for_year', 'date', 'is_paid']


@admin.register(models.Complete)
class CompleteAdmin(admin.ModelAdmin):
    list_display = ['id']
    list_filter = ['id']
