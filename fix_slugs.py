import os
import django
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'echoOfSound.settings')
django.setup()

from catalog.models import Track
from django.utils.text import slugify

# Находим все треки с пустым slug
tracks_without_slug = Track.objects.filter(slug='')

print(f"Найдено треков с пустым slug: {tracks_without_slug.count()}")

for track in tracks_without_slug:
    # Генерируем slug
    base_slug = slugify(track.title)

    # Если slug пустой (кириллица), используем uuid
    if not base_slug:
        base_slug = f"track-{uuid.uuid4().hex[:8]}"

    # Проверяем уникальность
    slug = base_slug
    counter = 1
    while Track.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    track.slug = slug
    track.save()
    print(f"Обновлен трек '{track.title}' -> slug: '{slug}'")

print("Готово!")
