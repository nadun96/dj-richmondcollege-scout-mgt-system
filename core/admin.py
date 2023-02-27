from django.contrib import admin
from . import models


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'pk', 'is_mem', 'is_skr', 'is_sec', 'is_ldr']
    list_filter = ['username', 'is_mem', 'is_skr', 'is_sec', 'is_ldr']
    search_fields = ['username']


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'surname',
                    'entrance_number', 'email', 'birthday', 'contact']
    list_filter = ['user', 'surname',
                   'entrance_number', 'email', 'birthday', 'contact']
    search_fields = ['user__username', 'surname']


@admin.register(models.Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'id',  'address', 'telephone', 'email']
    list_filter = ['id', 'name']


@admin.register(models.UserFile)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['user']
    list_filter = ['user']
    search_fields = ['user']


@admin.register(models.MemberRole)
class UserRolesAdmin(admin.ModelAdmin):
    list_display = ['id', 'profile', 'role',  'active', 'start', 'end']
    list_filter = ['id', 'profile', 'role',  'active', 'start', 'end']
    search_fields = ['profile__user__username', 'role__name']


@admin.register(models.Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'receiver', 'date']
    list_filter = ['id', 'sender', 'receiver', 'date']
    search_fields = ['date']


@admin.register(models.MembershipFee)
class MembershipFeeAdmin(admin.ModelAdmin):
    list_display = ['member', 'amount', 'for_year', 'date', 'is_paid']
    list_filter = ['member', 'amount', 'for_year', 'date', 'is_paid']
    search_fields = ['member__user__username', 'for_year']


@admin.register(models.Complete)
class CompleteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'examiner', 'requirement',
                    'applied', 'completed', 'stage')
    list_filter = ('stage',)
    search_fields = ('user__user__username',
                     'examiner__user__username', 'requirement__name')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user.profile
        super().save_model(request, obj, form, change)


@admin.register(models.Leader)
class LeaderAdmin(admin.ModelAdmin):
    list_display = ('name', 'patrol', 'start', 'end', 'is_active')
    list_filter = ('patrol', 'is_active')
    search_fields = ('name__user__username', 'patrol__name')
