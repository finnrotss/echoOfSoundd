from django.contrib import admin
from .models import (
    Genre, Profile, Track, Comment, Playlist, PlaylistTrack, Follow, Play
)
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'created_at')
    search_fields = ('user__username', 'user__email', 'bio')
    list_filter = ('created_at',)
    raw_id_fields = ('user',)

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'plays_count', 'is_public', 'created_at')
    list_filter = ('is_public', 'genre', 'downloads_allowed', 'created_at')
    search_fields = ('title', 'description', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-created_at',)
    list_editable = ('is_public', 'plays_count')
    raw_id_fields = ('author', 'genre')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('track', 'user', 'timestamp', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text', 'user__username', 'track__title')
    raw_id_fields = ('track', 'user')

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('name', 'description', 'user__username')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('-created_at',)
    raw_id_fields = ('user',)
    
    def cover_preview(self, obj):
        if obj.cover:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 8px;" />',
                               obj.cover.url)
        return "—"
    cover_preview.short_description = 'Обложка'

@admin.register(PlaylistTrack) #треки в плейлистах
class PlaylistTrackAdmin(admin.ModelAdmin):
    list_display = ('playlist', 'track', 'order', 'added_at')
    list_filter = ('playlist',)
    raw_id_fields = ('playlist', 'track')

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__username', 'following__username')
    raw_id_fields = ('follower', 'following')

@admin.register(Play)
class PlayAdmin(admin.ModelAdmin):
    list_display = ('track', 'user', 'ip_address', 'played_at')
    list_filter = ('played_at',)
    search_fields = ('track__title', 'user__username')
    raw_id_fields = ('track', 'user')
    readonly_fields = ('track', 'user', 'ip_address', 'played_at') #только для чтения

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
