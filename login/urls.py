from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.home, name='home'),
    path('view/register/', views.signup, name='signup'),
    path('view/events/', views.events, name='events'),
    path('view/requirements/', views.requirements, name='requirements'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    path('test/', views.MyCardView.as_view(), name='test'),
]
