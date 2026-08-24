import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_booking.settings')
django.setup()

from users.models import User

EMAIL = 'admin@spu.ac.za'
PASSWORD = 'AdminPass123!'
FULL_NAME = 'System Administrator'

if not User.objects.filter(email=EMAIL).exists():
    User.objects.create_superuser(
        email=EMAIL,
        full_name=FULL_NAME,
        password=PASSWORD,
        role='admin',
        student_number=None,
    )
    print(f'Superuser created: {EMAIL} / {PASSWORD}')
else:
    user = User.objects.get(email=EMAIL)
    if not user.is_superuser:
        user.is_superuser = True
        user.is_staff = True
        user.role = 'admin'
        user.set_password(PASSWORD)
        user.save()
        print(f'Existing user {EMAIL} promoted to superuser with password {PASSWORD}')
    else:
        print(f'Superuser already exists: {EMAIL}')
