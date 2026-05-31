from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Треки
    path('tracks/', views.track_list, name='track_list'),
    path('tracks/<slug:slug>/', views.track_detail, name='track_detail'),
    path('upload/', views.track_upload, name='track_upload'),
    path('tracks/<slug:slug>/delete/', views.track_delete, name='track_delete'),

    path('profile/<str:username>/', views.profile, name='profile'),
    path('my-profile/', views.my_profile, name='my_profile'),
    path('profile-edit/', views.profile_edit, name='profile_edit'),

    path('genres/', views.genre_list, name='genre_list'),
    path('genre/<slug:slug>/', views.genre_detail, name='genre_detail'),

    path('playlists/', views.playlist_list, name='playlist_list'),
    path('playlist/create/', views.playlist_create, name='playlist_create'),
    path('playlist/<slug:slug>/', views.playlist_detail, name='playlist_detail'),
    path('tracks/<slug:track_slug>/add-to-playlist/', views.add_to_playlist, name='add_to_playlist'),
    path('playlist/<slug:slug>/edit/', views.playlist_edit, name='playlist_edit'),
    path('track/<slug:slug>/like/', views.toggle_like, name='track_like'),

    path('search/', views.search, name='search'),
    path('random-track/', views.random_track, name='random_track'),

    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),
    path('profile/<str:username>/followers/', views.followers_list, name='followers_list'),
    path('profile/<str:username>/following/', views.following_list, name='following_list'),

    path('messages/', views.messages_list, name='messages_list'),
    path('messages/<str:username>/', views.conversation, name='conversation'),
    path('send-message/<str:username>/', views.send_message, name='send_message'),

    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]