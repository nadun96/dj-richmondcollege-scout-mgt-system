from django.urls import path
from . import views

app_name = 'patrol'

urlpatterns = [
    path('view/applied/<int:user_id>/', views.view_examine, name='examine_tab'),
    path('view/examine/page/<int:pk>/', views.examine_form, name='examine_form'),
    path('evaluate/', views.evaluate, name='evaluate'),

    path('view/members/', views.view_members, name='members_tab'),

    path('view/attendance/', views.view_attendance, name='attendance_tab'),
    path('add/attendance/', views.add_attendance, name='add_attendance'),

]
