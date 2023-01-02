from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [

    path('view/main/', views.main, name='main'),

    path('view/items/', views.items, name='items'),

    path('view/broken/', views.broken, name='broken'),

    path('view/lend/', views.lend, name='lend'),

    path('view/reports/', views.reports, name='reports'),

    path('add/item/', views.add_item, name='add_item'),

    path('add/broken/', views.add_broken, name='add_broken'),

    path('add/repaired/', views.add_repaired, name='add_repaired'),

    path('add/lend/', views.add_lend, name='add_lend'),

    path('return/lend/', views.return_lend, name='return_lend'),

]
