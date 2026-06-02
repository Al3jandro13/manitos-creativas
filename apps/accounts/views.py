import urllib.request
import urllib.parse
import urllib.error
import json as _json
import base64
import email.mime.text as _mime_text
import email.mime.multipart as _mime_multi
import email.mime.base as _mime_base
import email.encoders as _mime_enc

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy

from .forms import LoginForm, StudentRegisterForm, TeacherRegisterForm
from .models import CustomUser


def _send_via_gmail(social, recipients, subject, body_text, attachment_tuples=None):
    """
    Envía un correo usando Gmail API con el token OAuth2 almacenado.
    attachment_tuples: lista de (filename, bytes_content, content_type)
    Retorna (ok: bool, error: str|None).
    """
    from django.conf import settings

    def build_raw():
        msg = _mime_multi.MIMEMultipart()
        msg['to'] = ', '.join(recipients)
        msg['subject'] = subject
        msg.attach(_mime_text.MIMEText(body_text, 'plain', 'utf-8'))
        for fname, fcontent, ftype in (attachment_tuples or []):
            main, sub = ftype.split('/', 1) if '/' in ftype else ('application', 'octet-stream')
            part = _mime_base.MIMEBase(main, sub)
            part.set_payload(fcontent)
            _mime_enc.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{fname}"')
            msg.attach(part)
        return base64.urlsafe_b64encode(msg.as_bytes()).decode()

    def post_to_gmail(token):
        payload = _json.dumps({'raw': build_raw()}).encode()
        req = urllib.request.Request(
            'https://gmail.googleapis.com/gmail/v1/users/me/messages/send',
            data=payload,
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        )
        try:
            with urllib.request.urlopen(req, timeout=15):
                return True, None
        except urllib.error.HTTPError as e:
            return False, e.code
        except Exception as exc:
            return False, str(exc)

    extra = social.extra_data or {}
    token = extra.get('access_token')
    if not token:
        return False, 'Sin token de acceso. Vuelve a vincular tu cuenta de Google.'

    ok, err = post_to_gmail(token)
    if ok:
        return True, None

    if err == 401:
        refresh = extra.get('refresh_token')
        if not refresh:
            return False, 'Token expirado. Vuelve a vincular tu cuenta de Google para renovar el acceso.'
        try:
            data = urllib.parse.urlencode({
                'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
                'client_secret': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
                'refresh_token': refresh,
                'grant_type': 'refresh_token',
            }).encode()
            req = urllib.request.Request(
                'https://oauth2.googleapis.com/token', data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                new_token = _json.loads(resp.read()).get('access_token')
        except Exception as exc:
            return False, f'Error al refrescar token: {exc}'
        if not new_token:
            return False, 'No se pudo renovar el token. Vuelve a vincular tu cuenta de Google.'
        social.extra_data['access_token'] = new_token
        social.save()
        ok2, err2 = post_to_gmail(new_token)
        return (True, None) if ok2 else (False, f'Error al enviar: {err2}')

    return False, f'Error de Gmail API ({err}). Intenta de nuevo.'


@login_required
def student_profile_view(request):
    if not request.user.is_student:
        return redirect('teacher_dashboard')
    from apps.classroom.views import _student_sidebar_context
    from apps.games.models import GameSession
    from apps.activities.models import ActivitySubmission
    ctx = _student_sidebar_context(request.user)
    ctx['games_played'] = GameSession.objects.filter(student=request.user).count()
    ctx['activities_done'] = ActivitySubmission.objects.filter(
        student=request.user, status__in=['submitted', 'reviewed', 'approved']
    ).count()
    ctx['active_page'] = 'profile'
    return render(request, 'student/profile.html', ctx)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'¡Bienvenido/a, {user.first_name}! 🌟')
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, '¡Hasta pronto! 👋')
    return redirect('landing')


def google_no_account_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    google_email = request.session.get('google_login_email', '')
    google_name = request.session.get('google_login_name', '')
    return render(request, 'accounts/google_no_account.html', {
        'google_email': google_email,
        'google_name': google_name,
    })


def register_student_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    from apps.classroom.models import Course
    courses = Course.objects.filter(is_active=True).select_related('teacher').order_by('name')

    form = StudentRegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            course_id = request.POST.get('course_id')
            if course_id:
                try:
                    course = Course.objects.get(pk=course_id, is_active=True)
                    course.students.add(user)
                except Course.DoesNotExist:
                    pass
            login(request, user)
            messages.success(request, f'¡Cuenta creada! Bienvenido/a {user.first_name} 🎉')
            return redirect('student_dashboard')
        else:
            messages.error(request, 'Por favor corrige los errores.')

    return render(request, 'accounts/register_student.html', {'form': form, 'courses': courses})



def register_teacher_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = TeacherRegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Bienvenido/a, profe {user.first_name}! 🎉')
            return redirect('teacher_dashboard')
        else:
            messages.error(request, 'Por favor corrige los errores.')

    return render(request, 'accounts/register_teacher.html', {'form': form})


@login_required
def teacher_profile_view(request):
    if not request.user.is_teacher:
        return redirect('student_dashboard')
    from apps.activities.models import Activity
    from apps.accounts.models import CustomUser, TeacherProfile
    from social_django.models import UserSocialAuth

    profile, _ = TeacherProfile.objects.get_or_create(user=request.user)
    total_activities = Activity.objects.filter(teacher=request.user).count()
    total_students = CustomUser.objects.filter(role='student').count()

    google_social = UserSocialAuth.objects.filter(user=request.user, provider='google-oauth2').first()
    google_linked = google_social is not None
    google_email = ''
    if google_social:
        extra = google_social.extra_data or {}
        google_email = extra.get('email', '') or request.user.email or ''

    if request.method == 'POST':
        u = request.user
        u.first_name = request.POST.get('first_name', u.first_name).strip()
        u.last_name  = request.POST.get('last_name',  u.last_name).strip()
        new_email = request.POST.get('email', u.email).strip()
        if new_email and new_email != u.email:
            u.email = new_email
        u.save()
        profile.subject_specialty = request.POST.get('subject_specialty', '').strip()
        profile.years_experience  = int(request.POST.get('years_experience', 0) or 0)
        profile.bio               = request.POST.get('bio', '').strip()
        profile.save()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        if new_password and new_password == confirm_password:
            u.set_password(new_password)
            u.save()
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, u)
        ctx = {
            'profile': profile,
            'total_activities': total_activities,
            'total_students': total_students,
            'success': True,
            'google_linked': google_linked,
            'google_email': google_email,
        }
        return render(request, 'teacher/profile.html', ctx)

    ctx = {
        'profile': profile,
        'total_activities': total_activities,
        'total_students': total_students,
        'google_linked': google_linked,
        'google_email': google_email,
    }
    return render(request, 'teacher/profile.html', ctx)


@login_required
def dashboard_view(request):
    if request.user.is_teacher:
        return redirect('teacher_dashboard')
    return redirect('student_dashboard')


@login_required
def send_email_view(request):
    if not request.user.is_teacher:
        return redirect('student_dashboard')
    from social_django.models import UserSocialAuth

    students = CustomUser.objects.filter(role='student').order_by('first_name')
    google_social = UserSocialAuth.objects.filter(user=request.user, provider='google-oauth2').first()
    sent = False
    error = None

    if request.method == 'POST':
        raw_to      = request.POST.get('to_emails', '').strip()
        subject     = request.POST.get('subject', '').strip()
        body        = request.POST.get('body', '').strip()
        attachments = request.FILES.getlist('attachments')

        recipients = [e.strip() for e in raw_to.replace(';', ',').split(',') if e.strip()]

        if not recipients:
            error = 'Escribe al menos un correo destinatario.'
        elif not subject:
            error = 'El asunto es obligatorio.'
        elif not body:
            error = 'El mensaje no puede estar vacío.'
        elif not google_social:
            error = 'Debes vincular tu cuenta de Google en tu perfil antes de enviar correos.'
        else:
            attachment_data = [(f.name, f.read(), f.content_type) for f in attachments]
            ok, err = _send_via_gmail(google_social, recipients, subject, body, attachment_data)
            if ok:
                sent = True
            else:
                error = f'No se pudo enviar: {err}'

    return render(request, 'teacher/send_email.html', {
        'students': students,
        'sent': sent,
        'error': error,
        'google_linked': google_social is not None,
    })


@login_required
def disconnect_google_view(request):
    if not request.user.is_teacher:
        return redirect('student_dashboard')
    if request.method == 'POST':
        from social_django.models import UserSocialAuth
        UserSocialAuth.objects.filter(user=request.user, provider='google-oauth2').delete()
        messages.success(request, 'Cuenta de Google desvinculada correctamente.')
    return redirect('teacher_profile')


@login_required
def teacher_students_list(request):
    if not request.user.is_teacher:
        return redirect('student_dashboard')
    from django.db.models import Q
    from apps.accounts.models import StudentProfile

    students = CustomUser.objects.filter(role='student').select_related('student_profile').order_by('first_name', 'last_name')

    q = request.GET.get('q', '').strip()
    if q:
        students = students.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(username__icontains=q)
        )

    level = request.GET.get('level', '')
    if level in ('A', 'B'):
        students = students.filter(student_profile__level=level)

    return render(request, 'teacher/students/list.html', {
        'students': students,
        'q': q,
        'level': level,
        'total': students.count(),
    })


@login_required
def teacher_student_detail(request, pk):
    if not request.user.is_teacher:
        return redirect('student_dashboard')
    from django.shortcuts import get_object_or_404
    from apps.accounts.models import StudentProfile
    from apps.activities.models import ActivitySubmission
    from apps.games.models import GameSession
    from apps.classroom.models import Course

    student = get_object_or_404(CustomUser, pk=pk, role='student')
    profile, _ = StudentProfile.objects.get_or_create(user=student)
    courses = Course.objects.filter(students=student)
    recent_submissions = ActivitySubmission.objects.filter(
        student=student
    ).select_related('activity').order_by('-submitted_at')[:6]
    games_played = GameSession.objects.filter(student=student).count()
    activities_done = ActivitySubmission.objects.filter(
        student=student, status__in=['submitted', 'reviewed', 'approved']
    ).count()

    return render(request, 'teacher/students/detail.html', {
        'student': student,
        'profile': profile,
        'courses': courses,
        'recent_submissions': recent_submissions,
        'games_played': games_played,
        'activities_done': activities_done,
    })


@login_required
def teacher_student_edit(request, pk):
    if not request.user.is_teacher:
        return redirect('student_dashboard')
    from django.shortcuts import get_object_or_404
    from apps.accounts.models import StudentProfile

    student = get_object_or_404(CustomUser, pk=pk, role='student')
    profile, _ = StudentProfile.objects.get_or_create(user=student)

    errors = {}
    if request.method == 'POST':
        student.first_name = request.POST.get('first_name', student.first_name).strip()
        student.last_name = request.POST.get('last_name', student.last_name).strip()
        new_username = request.POST.get('username', student.username).strip()
        if new_username != student.username and CustomUser.objects.filter(username=new_username).exclude(pk=student.pk).exists():
            errors['username'] = 'Ese nombre de usuario ya está en uso.'
        else:
            student.username = new_username
        student.email = request.POST.get('email', student.email).strip()
        if not errors:
            student.save()
        profile.level = request.POST.get('level', profile.level)
        try:
            profile.age = int(request.POST.get('age') or profile.age)
        except (ValueError, TypeError):
            pass
        profile.parent_name = request.POST.get('parent_name', profile.parent_name).strip()
        profile.parent_email = request.POST.get('parent_email', profile.parent_email).strip()
        profile.parent_phone = request.POST.get('parent_phone', '').strip()
        profile.selected_avatar = request.POST.get('selected_avatar', profile.selected_avatar)
        profile.save()
        new_password = request.POST.get('new_password', '').strip()
        if new_password:
            student.set_password(new_password)
            student.save()
        if not errors:
            messages.success(request, f'Información de {student.get_full_name()} actualizada correctamente.')
            return redirect('teacher_student_detail', pk=student.pk)

    return render(request, 'teacher/students/edit.html', {
        'student': student,
        'profile': profile,
        'level_choices': StudentProfile.LEVEL_CHOICES,
        'avatar_choices': StudentProfile.AVATAR_CHOICES,
        'errors': errors,
    })


@login_required
def teacher_student_delete(request, pk):
    if not request.user.is_teacher:
        return redirect('student_dashboard')
    from django.shortcuts import get_object_or_404

    student = get_object_or_404(CustomUser, pk=pk, role='student')
    if request.method == 'POST':
        name = student.get_full_name() or student.username
        student.delete()
        messages.success(request, f'Estudiante {name} eliminado correctamente.')
    return redirect('teacher_students')


@login_required
def ai_draft_email_view(request):
    """Genera un borrador de correo con Claude."""
    if not request.user.is_teacher:
        from django.http import JsonResponse
        return JsonResponse({'error': 'No autorizado'}, status=403)

    import json
    from django.http import JsonResponse
    from django.conf import settings

    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data    = json.loads(request.body)
        prompt  = data.get('prompt', '').strip()
        subject = data.get('subject', '').strip()
    except Exception:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    if not prompt:
        return JsonResponse({'error': 'Describe qué quieres comunicar.'}, status=400)

    api_key = getattr(settings, 'ANTHROPIC_API_KEY', '') or ''
    if not api_key:
        return JsonResponse({'error': 'API key de IA no configurada.'}, status=500)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        system = (
            "Eres una asistente experta en comunicación educativa. "
            "Redactas correos profesionales, cálidos y claros para docentes de preescolar "
            "que se dirigen a padres o acudientes. Responde SOLO con el cuerpo del correo, "
            "sin asunto, sin saludos genéricos de apertura como 'Estimado/a', "
            "empieza directamente con el contenido. Usa español colombiano, tono amable y formal."
        )
        user_msg = f"Asunto del correo: {subject}\n\nInstrucción: {prompt}"
        response = client.messages.create(
            model='claude-sonnet-4-6',
            max_tokens=800,
            system=system,
            messages=[{'role': 'user', 'content': user_msg}],
        )
        draft = response.content[0].text.strip()
        return JsonResponse({'draft': draft})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
