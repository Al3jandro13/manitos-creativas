def set_teacher_role(backend, user, response, *args, **kwargs):
    if not user.role:
        user.role = 'teacher'
        user.save()


def use_logged_in_user(strategy, user=None, *args, **kwargs):
    """If a user is already authenticated, associate Google with their account instead of creating a new one."""
    if not user:
        request = getattr(strategy, 'request', None)
        if request and request.user.is_authenticated:
            return {'user': request.user, 'is_new': False}


def require_existing_account(strategy, details, user=None, *args, **kwargs):
    """If no existing account found for this Google login, redirect to the registration panel."""
    if user is None:
        request = strategy.request
        request.session['google_login_email'] = details.get('email', '')
        request.session['google_login_name'] = (
            details.get('fullname') or details.get('first_name', '')
        )
        from django.urls import reverse
        return strategy.redirect(reverse('google_no_account'))
