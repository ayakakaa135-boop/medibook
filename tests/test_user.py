import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# اختبار إنشاء superuser
user = User.objects.create_superuser(
    email='admin@test.com',
    password='admin123456',
    first_name='Admin',
    last_name='User'
)

print(f"✅ تم إنشاء المستخدم: {user.email}")