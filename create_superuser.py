import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "skaagpay_backend.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

phone = "9999999999"
password = "adminpassword"

if not User.objects.filter(phone_number=phone).exists():
    User.objects.create_superuser(phone_number=phone, full_name="Admin User", password=password)
    print(f"Superuser created: Phone={phone}, Password={password}")
else:
    print("Superuser already exists")
