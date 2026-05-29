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
