from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import User


class ActivityLogMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.user.is_authenticated:
            content_type = ContentType.objects.get_for_model(User)
            LogEntry.objects.create(
                user=request.user,
                content_type=content_type,
                object_id=request.user.id,
                object_repr=str(request.user),
                action_flag=2,
                change_message='User activity: ' + request.path
            )
