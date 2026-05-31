from django.contrib.auth.models import User
from catalog.models import Profile

# Создаём профили для всех пользователей без профиля
users = User.objects.all()
for user in users:
    Profile.objects.get_or_create(user=user)

print(f"Проверено пользователей: {users.count()}")
print(f"Всего профилей: {Profile.objects.count()}")
