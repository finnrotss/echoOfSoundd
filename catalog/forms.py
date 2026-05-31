from django import forms
from .models import Track, Playlist, Comment


class TrackUploadForm(forms.ModelForm):
    """Форма загрузки трека"""

    class Meta:
        model = Track
        fields = ['title', 'audio_file', 'cover', 'description', 'genre', 'downloads_allowed', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название трека'
            }),
            'audio_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'audio/mp3,audio/wav'
            }),
            'cover': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Описание трека (необязательно)',
                'rows': 4
            }),
            'genre': forms.Select(attrs={
                'class': 'form-control'
            }),
            'downloads_allowed': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'title': 'Название трека',
            'audio_file': 'Аудиофайл (MP3, WAV)',
            'cover': 'Обложка (необязательно)',
            'description': 'Описание',
            'genre': 'Жанр',
            'downloads_allowed': 'Разрешить скачивание',
            'is_public': 'Публичный трек',
        }
