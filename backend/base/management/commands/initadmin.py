from django.conf import settings
from django.core.management.base import BaseCommand
from ...models import User
from os import environ

class Command(BaseCommand):
    def handle(self, *args, **options):
        if User.objects.count() == 0:
            username = environ.get("DJANGO_SUPERUSER_USERNAME")
            password = environ.get("DJANGO_SUPERUSER_PASSWORD")
            print(f"Creating account for {username}")
            admin = User.objects.create_superuser(username=username, password=password)
            admin.is_active = True
            admin.is_admin = True
            admin.save()
        else:
            print('Admin accounts can only be initialized if no Users exist')