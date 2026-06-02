from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.admin_panel.views import blocked_view

urlpatterns = [
    path('panel-admin/', include('apps.admin_panel.urls')),
    path('servicio-suspendido/', blocked_view, name='blocked'),
    path('', include('apps.core.urls')),
    path('social/', include('social_django.urls', namespace='social')),
    path('cuentas/', include('apps.accounts.urls')),
    path('actividades/', include('apps.activities.urls')),
    path('juegos/', include('apps.games.urls')),
    path('salon/', include('apps.classroom.urls')),
    path('reportes/', include('apps.reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
