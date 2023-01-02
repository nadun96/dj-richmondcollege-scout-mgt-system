from django.contrib import admin
# Register your models here.
from . import models


@admin.register(models.Item)
class ItemsAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'id', 'item_price', 'item_quantity_received',
                    'item_quantity_available', 'item_purchased_date', 'item_units']

    list_filter = ['item_name', 'id',  'item_price', 'item_quantity_received',
                   'item_quantity_available', 'item_purchased_date', 'item_units']


@admin.register(models.Broken)
class BrokenAdmin(admin.ModelAdmin):
    list_display = ['item', 'id', 'item_quantity_broken', 'item_broken_date',]
    list_filter = ['item', 'id', 'item_quantity_broken', 'item_broken_date']


@admin.register(models.Lend)
class LendAdmin(admin.ModelAdmin):
    list_display = ['item', 'id', 'user', 'item_quantity_lent',
                    'item_lent_date', 'date_returned_date']

    list_filter = ['item', 'id', 'user', 'item_quantity_lent',
                   'item_lent_date', 'date_returned_date']
