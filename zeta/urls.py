
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

admin.AdminSite.site_header = 'R C S G Admin'
admin.AdminSite.index_title = 'Admin'


urlpatterns = [

    path('', include('login.urls')),

    path('store/', include('store.urls')),

    path('admin/', admin.site.urls),

    #path('api-auth/', include('rest_framework.urls')),

    path('member/', include('member.urls')),

    path('manager/', include('manager.urls')),

    #path('core/', include('core.urls')),

    path('patrol/', include('patrol.urls')),

    path('__debug__/', include('debug_toolbar.urls')),

    #path('django_plotly_dash/', include('django_plotly_dash.urls')),

    path('report_builder/', include('report_builder.urls')),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
