from django.utils import timezone
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.db import models
from login.utils import generate_username

User = get_user_model()

# auto username signal before save


@receiver(pre_save, sender=User)
def set_username(sender, instance, created, **kwargs):
    if created:
        instance.username = generate_username()
        instance.save()


models.signals.pre_save.connect(set_username, sender=User)
