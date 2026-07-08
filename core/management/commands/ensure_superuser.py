import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Idempotently create a Django superuser from the DJANGO_SUPERUSER_* "
        "environment variables. Does nothing if the user already exists."
    )

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')

        if not username or not password:
            self.stdout.write(
                'DJANGO_SUPERUSER_USERNAME/PASSWORD not set; skipping superuser creation.'
            )
            return

        User = get_user_model()
        username_field = User.USERNAME_FIELD

        if User.objects.filter(**{username_field: username}).exists():
            self.stdout.write(f"Superuser '{username}' already exists; nothing to do.")
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(f"Created superuser '{username}'."))
