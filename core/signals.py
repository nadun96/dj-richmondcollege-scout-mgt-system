from django.utils import timezone
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.db import models
import time
User = get_user_model()

# auto username signal before save


@receiver(pre_save, sender=User)
def set_username(sender, instance, created, **kwargs):
    if created:
        current_year = timezone.now().year
        users = User.objects.filter(date_joined__year=current_year)
        user_ids = [user.id for user in users]
        max_id = max(user_ids) if user_ids else 0
        next_id = max_id + 1
        next_id = str(next_id)
        instance.username = f'SC/{current_year}/{next_id.zfill(5)}'
        instance.save()


models.signals.pre_save.connect(set_username, sender=User)
