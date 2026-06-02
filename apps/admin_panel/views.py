import os
from django.shortcuts import render, redirect
from .models import SystemConfig

ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', '')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '')


def admin_login(request):
    if request.session.get('is_admin'):
        return redirect('admin_panel:dashboard')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            request.session['is_admin'] = True
            request.session.set_expiry(0)
            return redirect('admin_panel:dashboard')
        error = 'Usuario o contraseña incorrectos.'

    return render(request, 'admin_panel/login.html', {'error': error})


def admin_dashboard(request):
    if not request.session.get('is_admin'):
        return redirect('admin_panel:login')
    config = SystemConfig.get_instance()
    return render(request, 'admin_panel/dashboard.html', {'config': config})


def admin_logout(request):
    request.session.flush()
    return redirect('admin_panel:login')


def toggle_block(request):
    if not request.session.get('is_admin'):
        return redirect('admin_panel:login')
    if request.method == 'POST':
        config = SystemConfig.get_instance()
        config.is_blocked = not config.is_blocked
        config.save()
    return redirect('admin_panel:dashboard')


def blocked_view(request):
    return render(request, 'admin_panel/blocked.html')
