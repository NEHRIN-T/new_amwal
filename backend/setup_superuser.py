import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "amwal")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@amwal.local")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "amwal")

try:
    user = User.objects.get(username=username)
    user.email = email
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.portal = "both"
    user.role = "system_admin"
    user.save()
    print(f"Superuser '{username}' updated successfully.")
except User.DoesNotExist:
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        portal="both",
        role="system_admin"
    )
    print(f"Superuser '{username}' created successfully.")
