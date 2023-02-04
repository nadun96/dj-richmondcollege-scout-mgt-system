from django.urls import path
from . import views

app_name = 'patrol'

urlpatterns = [

    path('view/applied/', views.view_examine, name='examine_tab'),

    path('view/examine/page/<int:pk>/', views.examine_form, name='examine_form'),

    path('evaluate/', views.evaluate, name='evaluate'),

    path('view/members/', views.contact, name='contact_tab'),

    path('view/profile/<int:user>/', views.view_member, name='view_member'),

    path('view/profile/', views.view_profile, name='profile_tab'),

    path('view/attendance/', views.view_attendance, name='attendance_tab'),

    path('add/attendance/', views.add_attendance, name='add_attendance'),

]
