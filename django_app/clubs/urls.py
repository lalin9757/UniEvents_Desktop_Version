from django.urls import path
from . import views

urlpatterns = [
    path('', views.club_list, name='club_list'),
    path('create/', views.create_club, name='club_create'),
    path('<slug:slug>/', views.club_detail, name='club_detail'),
    path('<slug:slug>/join/', views.join_club, name='join_club'),
    path('<slug:slug>/manage-members/', views.manage_club_members, name='manage_club_members'),
]