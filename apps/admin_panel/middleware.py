from django.shortcuts import redirect
from .models import SystemConfig

EXEMPT_PREFIXES = (
    '/panel-admin/',
    '/servicio-suspendido/',
    '/static/',
    '/media/',
    '/staticfiles/',
)


class SystemBlockMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        for prefix in EXEMPT_PREFIXES:
            if request.path.startswith(prefix):
                return self.get_response(request)

        try:
            config = SystemConfig.objects.filter(pk=1).first()
            if config and config.is_blocked and not request.session.get('is_admin'):
                return redirect('/servicio-suspendido/')
        except Exception:
            pass

        return self.get_response(request)
