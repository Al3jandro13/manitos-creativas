from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def teacher_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_teacher:
            messages.error(request, 'Acceso solo para profesores.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def student_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_student:
            messages.error(request, 'Acceso solo para estudiantes.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper
