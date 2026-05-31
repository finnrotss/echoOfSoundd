from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.core.files.storage import default_storage
from django.db.models import Q
from django.views.generic import ListView, DetailView
from .models import Track, Genre, Playlist, Profile, Comment, PlaylistTrack, Follow, Message
from .forms import TrackUploadForm
import os
import random
from django.http import JsonResponse
from django.views.decorators.http import require_POST



class TrackListView(ListView):
    """Список всех треков (CBV)""" #вьюхи как классы
    model = Track
    template_name = 'catalog/track_list.html'
    context_object_name = 'tracks'

    def get_queryset(self):
        queryset = Track.objects.filter(is_public=True).select_related('author', 'genre').order_by('-created_at') #оптимизация

        # Поиск
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__username__icontains=search_query)
            )

        # Фильтр по жанру
        genre_id = self.request.GET.get('genre', '')
        if genre_id:
            queryset = queryset.filter(genre_id=genre_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Genre.objects.all()
        return context


# Для обратной совместимости с URL
track_list = TrackListView.as_view()


def track_detail(request, slug):
    """Детальная страница трека"""
    track = get_object_or_404(Track, slug=slug)
    comments = track.comments.select_related('user').order_by('-created_at')

    # Получаем плейлисты пользователя для добавления трека
    user_playlists = []
    if request.user.is_authenticated:
        user_playlists = Playlist.objects.filter(user=request.user)

    # Обработка добавления комментария
    if request.method == 'POST' and request.user.is_authenticated:
        text = request.POST.get('text')
        timestamp = request.POST.get('timestamp')

        if text and timestamp:
            try:
                comment = Comment.objects.create(
                    track=track,
                    user=request.user,
                    text=text,
                    timestamp=int(timestamp)
                )
                messages.success(request, 'Комментарий добавлен!')
                return redirect('track_detail', slug=slug)
            except (ValueError, TypeError):
                messages.error(request, 'Неверный формат времени')
        else:
            messages.error(request, 'Заполните все поля')

    context = {
        'track': track,
        'comments': comments,
        'user_playlists': user_playlists,
    }
    return render(request, 'catalog/track_detail.html', context)


class GenreListView(ListView):
    """Список жанров (CBV)"""
    model = Genre
    template_name = 'catalog/genre_list.html'
    context_object_name = 'genres'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Жанры'
        return context


genre_list = GenreListView.as_view()


class GenreDetailView(DetailView):
    """Детальная страница жанра (CBV)"""
    model = Genre
    template_name = 'catalog/genre_detail.html'
    context_object_name = 'genre'
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Жанр: {self.object.name}"
        return context


genre_detail = GenreDetailView.as_view()


class PlaylistListView(ListView):
    """Список плейлистов (CBV)"""
    model = Playlist
    template_name = 'catalog/playlist_list.html'
    context_object_name = 'playlists'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Плейлисты'
        return context


playlist_list = PlaylistListView.as_view()


class PlaylistDetailView(DetailView):
    """Детальная страница плейлиста (CBV)"""
    model = Playlist
    template_name = 'catalog/playlist_detail.html'
    context_object_name = 'playlist'
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.name
        return context


playlist_detail = PlaylistDetailView.as_view()

@login_required
@require_POST
def toggle_like(request, slug):
    track = get_object_or_404(Track, slug=slug)
    user = request.user
    if user in track.likes.all():
        track.likes.remove(user)
        liked = False
    else:
        track.likes.add(user)
        liked = True
    track.update_likes_count()
    return JsonResponse({'liked': liked, 'likes_count': track.likes_count})

@login_required
def playlist_edit(request, slug):
    playlist = get_object_or_404(Playlist, slug=slug)
    # Только владелец может редактировать
    if playlist.user != request.user:
        return redirect('playlist_detail', slug=slug)

    if request.method == 'POST':
        playlist.name = request.POST.get('name')
        playlist.description = request.POST.get('description')
        playlist.is_public = request.POST.get('is_public') == 'on'
        if request.FILES.get('cover'):
            # Удаляем старую обложку, если нужно
            if playlist.cover:
                default_storage.delete(playlist.cover.path)
            playlist.cover = request.FILES['cover']
        playlist.save()
        return redirect('playlist_detail', slug=playlist.slug)

    return render(request, 'catalog/playlist_edit.html', {'playlist': playlist})


def profile(request, username):
    """Профиль пользователя"""
    profile_obj = get_object_or_404(Profile, user__username=username)
    user_tracks = Track.objects.filter(author=profile_obj.user, is_public=True)[:6]

    # Проверяем, подписан ли текущий пользователь
    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, following=profile_obj.user).exists()

    # Считаем подписчиков и подписки
    followers_count = Follow.objects.filter(following=profile_obj.user).count()
    following_count = Follow.objects.filter(follower=profile_obj.user).count()

    context = {
        'profile': profile_obj,
        'user_tracks': user_tracks,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
        'title': f"{profile_obj.user.username} — echoOfSound",
    }
    return render(request, 'catalog/profile.html', context)


@login_required
def my_profile(request):
    """Профиль текущего пользователя"""
    return profile(request, request.user.username)


@login_required
def profile_edit(request):
    """Редактирование профиля"""
    profile_obj, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        bio = request.POST.get('bio', '')
        location = request.POST.get('location', '')
        website = request.POST.get('website', '')
        avatar = request.FILES.get('avatar')
        cover = request.FILES.get('cover')

        profile_obj.bio = bio
        profile_obj.location = location
        profile_obj.website = website

        if avatar:
            # Удаляем старую аватарку
            if profile_obj.avatar:
                if os.path.isfile(profile_obj.avatar.path):
                    os.remove(profile_obj.avatar.path)
            profile_obj.avatar = avatar
        if cover:
            if profile_obj.cover and os.path.isfile(profile_obj.cover.path):
                os.remove(profile_obj.cover.path)
            profile_obj.cover = cover

        profile_obj.save()
        messages.success(request, 'Профиль успешно обновлен!')
        return redirect('my_profile')

    context = {
        'profile': profile_obj,
        'title': 'Редактировать профиль',
    }
    return render(request, 'catalog/profile_edit.html', context)


def search(request):
    """Поиск треков и артистов"""
    query = request.GET.get('q', '')
    tracks = []
    artists = []

    if query:
        # Если запрос начинается с @, ищем артистов
        if query.startswith('@'):
            username_query = query[1:]  # Убираем @
            artists = User.objects.filter(
                username__icontains=username_query
            ).select_related('profile')[:20]
        else:
            # Иначе ищем треки
            tracks = Track.objects.filter(
                Q(is_public=True) & (
                    Q(title__icontains=query) |
                    Q(author__username__icontains=query)
                )
            ).select_related('author', 'genre')[:20]

    context = {
        'tracks': tracks,
        'artists': artists,
        'query': query,
        'title': 'Поиск',
    }
    return render(request, 'catalog/search.html', context)


# Авторизация
def register_view(request):
    """Регистрация нового пользователя"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Валидация
        errors = []
        if not username or not password1 or not password2:
            errors.append('Все поля обязательны для заполнения')
        elif password1 != password2:
            errors.append('Пароли не совпадают')
        elif len(password1) < 8:
            errors.append('Пароль должен содержать минимум 8 символов')
        elif User.objects.filter(username=username).exists():
            errors.append('Пользователь с таким именем уже существует')

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            # Создание пользователя
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            login(request, user)
            messages.success(request, f'Добро пожаловать, {username}!')
            return redirect('home')

    return render(request, 'catalog/register.html')


def login_view(request):
    """Вход пользователя"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')

    return render(request, 'catalog/login.html')


def logout_view(request):
    """Выход пользователя"""
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('home')


@login_required
def track_upload(request):
    """Загрузка трека"""
    if request.method == 'POST':
        form = TrackUploadForm(request.POST, request.FILES)
        if form.is_valid():
            track = form.save(commit=False)
            track.author = request.user
            track.save()
            messages.success(request, f'Трек "{track.title}" успешно загружен!')
            return redirect('track_detail', slug=track.slug)
    else:
        form = TrackUploadForm()

    context = {
        'form': form,
        'title': 'Загрузить трек',
    }
    return render(request, 'catalog/track_upload.html', context)


@login_required
def track_delete(request, slug):
    """Удаление трека"""
    track = get_object_or_404(Track, slug=slug)

    # Проверяем, что пользователь является автором трека
    if track.author != request.user:
        messages.error(request, 'Вы не можете удалить чужой трек!')
        return redirect('track_detail', slug=slug)

    if request.method == 'POST':
        track_title = track.title
        track.delete()
        messages.success(request, f'Трек "{track_title}" успешно удалён!')
        return redirect('my_profile')

    context = {
        'track': track,
        'title': f'Удалить трек: {track.title}',
    }
    return render(request, 'catalog/track_delete.html', context)


@login_required
def add_to_playlist(request, track_slug):
    """Добавление трека в плейлист"""
    track = get_object_or_404(Track, slug=track_slug)

    if request.method == 'POST':
        playlist_id = request.POST.get('playlist_id')

        if playlist_id:
            playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)

            # Проверяем, не добавлен ли уже трек в плейлист
            if PlaylistTrack.objects.filter(playlist=playlist, track=track).exists():
                messages.warning(request, f'Трек уже есть в плейлисте "{playlist.name}"')
            else:
                # Получаем максимальный порядковый номер
                max_order = PlaylistTrack.objects.filter(playlist=playlist).count()

                PlaylistTrack.objects.create(
                    playlist=playlist,
                    track=track,
                    order=max_order
                )
                messages.success(request, f'Трек добавлен в плейлист "{playlist.name}"')
        else:
            messages.error(request, 'Выберите плейлист')

    return redirect('track_detail', slug=track_slug)


@login_required
def playlist_create(request):
    """Создание нового плейлиста"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        is_public = request.POST.get('is_public') == 'on'

        if name:
            # Генерируем slug
            from django.utils.text import slugify
            import uuid
            base_slug = slugify(name)

            if not base_slug:
                base_slug = f"playlist-{uuid.uuid4().hex[:8]}"

            slug = base_slug
            counter = 1
            while Playlist.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            playlist = Playlist.objects.create(
                name=name,
                slug=slug,
                user=request.user,
                description=description,
                is_public=is_public
            )
            messages.success(request, f'Плейлист "{name}" создан!')
            return redirect('playlist_detail', slug=playlist.slug)
        else:
            messages.error(request, 'Введите название плейлиста')

    context = {
        'title': 'Создать плейлист',
    }
    return render(request, 'catalog/playlist_create.html', context)


# Подписки
@login_required
def follow_user(request, username):
    """Подписаться на пользователя"""
    user_to_follow = get_object_or_404(User, username=username)

    if user_to_follow == request.user:
        messages.error(request, 'Вы не можете подписаться на себя')
    else:
        Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
        messages.success(request, f'Вы подписались на {username}')

    return redirect('profile', username=username)


@login_required
def unfollow_user(request, username):
    """Отписаться от пользователя"""
    user_to_unfollow = get_object_or_404(User, username=username)

    Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
    messages.success(request, f'Вы отписались от {username}')

    return redirect('profile', username=username)


@login_required
def followers_list(request, username):
    """Список подписчиков пользователя"""
    user = get_object_or_404(User, username=username)
    followers = Follow.objects.filter(following=user).select_related('follower')

    context = {
        'user': user,
        'followers': followers,
        'title': f'Подписчики {username}',
    }
    return render(request, 'catalog/followers_list.html', context)


@login_required
def following_list(request, username):
    """Список подписок пользователя"""
    user = get_object_or_404(User, username=username)
    following = Follow.objects.filter(follower=user).select_related('following')

    context = {
        'user': user,
        'following': following,
        'title': f'Подписки {username}',
    }
    return render(request, 'catalog/following_list.html', context)


# Личные сообщения
@login_required
def messages_list(request):
    """Список диалогов"""
    # Получаем всех пользователей, с которыми есть переписка
    sent_to = Message.objects.filter(sender=request.user).values_list('recipient', flat=True).distinct()
    received_from = Message.objects.filter(recipient=request.user).values_list('sender', flat=True).distinct()

    user_ids = set(sent_to) | set(received_from)
    users = User.objects.filter(id__in=user_ids)

    # Для каждого пользователя получаем последнее сообщение
    dialogs = []
    for user in users:
        last_message = Message.objects.filter(
            Q(sender=request.user, recipient=user) | Q(sender=user, recipient=request.user)
        ).order_by('-created_at').first()

        unread_count = Message.objects.filter(
            sender=user, recipient=request.user, is_read=False
        ).count()

        dialogs.append({
            'user': user,
            'last_message': last_message,
            'unread_count': unread_count,
        })

    # Сортируем по времени последнего сообщения
    dialogs.sort(key=lambda x: x['last_message'].created_at, reverse=True)

    context = {
        'dialogs': dialogs,
        'title': 'Сообщения',
    }
    return render(request, 'catalog/messages_list.html', context)


@login_required
def conversation(request, username):
    """Диалог с пользователем"""
    other_user = get_object_or_404(User, username=username)

    # Получаем все сообщения между пользователями
    chat_messages = Message.objects.filter(
        Q(sender=request.user, recipient=other_user) | Q(sender=other_user, recipient=request.user)
    ).order_by('created_at')

    # Отмечаем непрочитанные сообщения как прочитанные
    Message.objects.filter(sender=other_user, recipient=request.user, is_read=False).update(is_read=True)

    # Обработка отправки сообщения
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            Message.objects.create(
                sender=request.user,
                recipient=other_user,
                text=text
            )
            return redirect('conversation', username=username)

    context = {
        'other_user': other_user,
        'chat_messages': chat_messages,
        'title': f'Диалог с {username}',
    }
    return render(request, 'catalog/conversation.html', context)


@login_required
def send_message(request, username):
    """Отправить сообщение пользователю (редирект на диалог)"""
    other_user = get_object_or_404(User, username=username)
    return redirect('conversation', username=username)

def home(request):
    popular_tracks = Track.objects.filter(is_public=True).order_by('-plays_count')[:8]
    subscribed_playlists = []
    if request.user.is_authenticated:
        following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
        subscribed_playlists = Playlist.objects.filter(
            user__id__in=following_users,
            is_public=True
        ).order_by('-created_at')[:8]

    context = {
        'popular_tracks': popular_tracks,
        'subscribed_playlists': subscribed_playlists,
    }
    return render(request, 'catalog/home.html', context)

def random_track(request):
    tracks = Track.objects.filter(is_public=True)
    if tracks.exists():
        track = random.choice(tracks)
        return redirect('track_detail', slug=track.slug)
    # Если треков нет, редирект на главную
    return redirect('home')