from django.urls import path
from . import views

app_name = 'member'
urlpatterns = [
    path('profile/', views.view_profile, name='profile'),

    path('profile/<int:user_id>/', views.user_profile, name='profile'),
    path('profile/up/', views.profile_update, name='update_profile'),

    #path('hikes/', views.view_hikes, name='hikes'),
    path('hikes/<int:user_id>/', views.hikes, name='hikes'),
    path('hikes/add/', views.add_hike, name='profile_add_hike'),

    #path('projects/', views.view_projects, name='projects'),
    path('projects/<int:user_id>/', views.projects, name='projects'),
    path('projects/add/', views.add_project, name='profile_add_project'),

    #path('camps/', views.view_camps, name='camps'),
    path('camps/<int:user_id>/', views.camps, name='camps'),
    path('camps/add/', views.add_camp, name='profile_add_camp'),

    #path('badges/', views.view_badges, name='badges'),
    path('badges/<int:user_id>/', views.badges, name='badges'),
    path('badges/app/', views.apply_requirement,
         name='apply_requirement'),

    path('announce/', views.view_announce, name='messages'),
    path('sat/', views.saturday_posts, name='articles'),
    path('sat/lv/', views.PostListView.as_view(), name='post'),

]
