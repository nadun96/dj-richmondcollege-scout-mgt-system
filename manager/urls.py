from django.urls import path
from . import views

app_name = 'manager'

urlpatterns = [

    path('view/', views.manage_view, name='main'),
    path('events/', views.manage_edit, name='events'),
    path('wall/', views.manage_wall, name='manage_wall'),
    path('welcome/', views.manage_patrols, name='manage_patrols'),
    path('announce/', views.manage_announcements, name='manage_announce'),
    path('badge/', views.manage_badges, name='manage_badges'),

    # code for manage roles in views
    path('role/', views.manage_roles, name='manage_roles'),
    path('role/tog/', views.toggle_role, name='toggle_roles'),
    #path('role/get/', views.toggle_role, name='toggle_roles'),


    # code for manage leaders in views
    path('leaders/', views.manage_leaders, name='manage_leaders'),
    path('leaders/tog/', views.toggle_leader, name='toggle_leaders'),
    path('leaders/rm/', views.rm_leader, name='rm_leaders'),



    path('member/', views.manage_member, name='manage_member'),
    path('member/toggle/', views.activate_member, name='activate_member'),
    path('member/fee/add/', views.add_membership_fee, name='add_membership_fee'),

    path('add/hike/', views.add_hike, name='add_hike'),
    path('list/hike/', views.add_hike, name='list_hike'),

    path('add/camp/', views.add_camp, name='add_camp'),
    path('list/camp/', views.add_camp, name='list_camp'),

    path('add/project/', views.add_project, name='add_project'),
    path('list/project/', views.add_project, name='list_project'),

    path('add/patrol/', views.add_patrol, name='add_patrol'),
    path('get/patrol/', views.get_patrol, name='get_patrol'),
    path('del/patrol/', views.del_patrol, name='del_patrol'),
    path('assign/patrol/', views.assign_patrol, name='assign_patrol'),

    path('add/badge/', views.add_badge, name='add_badge'),
    path('get/badges/', views.get_badges, name='get_badges'),

    path('add/requirement/', views.add_requirement, name='add_requirement'),
    path('get/requirements/', views.get_requirements, name='get_requirements'),

    path('add/photo/', views.add_photo, name='add_photo'),
    path('add/post/', views.add_post, name='add_post'),

    path('add/announce/', views.add_announce, name='add_announce'),
    path('get/announce/', views.get_announce, name='get_announce'),

    path('get/profiles/', views.get_profiles, name='get_profiles'),


]
