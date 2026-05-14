"""
Run this script to create/ensure the superadmin account exists.
Usage: python manage.py shell < create_superadmin.py
Or run directly: python create_superadmin.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Create or update superadmin
if User.objects.filter(username='superadmin').exists():
    user = User.objects.get(username='superadmin')
    user.email = 'superadmin@gmail.com'
    user.user_type = 'admin'
    user.is_staff = True
    user.is_superuser = True
    user.set_password('superadmin')
    user.save()
    print("[OK] superadmin account updated.")
else:
    user = User.objects.create_superuser(
        username='superadmin',
        email='superadmin@gmail.com',
        password='superadmin',
        user_type='admin',
        is_staff=True,
        is_superuser=True,
    )
    print("[OK] superadmin account created.")

print("  username: superadmin")
print("  email   : superadmin@gmail.com")
print("  password: superadmin")
