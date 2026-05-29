from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import Announcement, FameBoardEntry
from apps.accounts.decorators import teacher_required, student_required
from apps.accounts.models import CustomUser
from apps.activities.models import Activity, ActivitySubmission
from apps.games.models import GameSession


def _student_sidebar_context(user):
    """Return sidebar context variables for student pages."""
    try:
        profile = user.student_profile
    except Exception:
        profile = None

    assigned = Activity.objects.filter(status='published').filter(
        Q(assigned_to_all=True) | Q(assigned_students=user)
    ).distinct()
    completed_ids = ActivitySubmission.objects.filter(
        student=user, status__in=['submitted', 'reviewed', 'approved']
    ).values_list('activity_id', flat=True)
    pending_tasks = assigned.exclude(id__in=completed_ids).count()

    recent_submissions = ActivitySubmission.objects.filter(
        student=user, status='approved'
    ).select_related('activity__category').order_by('-submitted_at')[:3]

    return {
        'profile': profile,
        'pending_tasks': pending_tasks,
        'recent_submissions': recent_submissions,
    }


@login_required
@teacher_required
def teacher_dashboard(request):
    activities = Activity.objects.filter(teacher=request.user)
    activity_stats = activities.aggregate(
        total=Count('id'),
        published=Count('id', filter=Q(status='published')),
    )
    pending_submissions = ActivitySubmission.objects.filter(
        activity__teacher=request.user, status='submitted'
    ).select_related('student', 'activity')
    students = CustomUser.objects.filter(role='student').select_related('student_profile')

    context = {
        'stats': {
            'total_activities': activity_stats['total'],
            'published': activity_stats['published'],
            'pending_reviews': pending_submissions.count(),
            'total_students': students.count(),
        },
        'recent_activities': activities.select_related('category').order_by('-created_at')[:8],
        'pending_submissions': pending_submissions[:5],
        'recent_announcements': Announcement.objects.filter(
            teacher=request.user, is_active=True
        ).order_by('-created_at')[:3],
        'fame_entries': FameBoardEntry.objects.filter(teacher=request.user)[:6],
        'students': students,
    }
    return render(request, 'teacher/dashboard.html', context)


@login_required
@teacher_required
def fame_board(request):
    entries = FameBoardEntry.objects.filter(teacher=request.user, is_active=True)
    students = CustomUser.objects.filter(role='student').select_related('student_profile')

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        student = get_object_or_404(CustomUser, id=student_id, role='student')
        FameBoardEntry.objects.create(
            student=student,
            teacher=request.user,
            title=request.POST.get('title', '¡Excelente trabajo!'),
            description=request.POST.get('description', ''),
            medal_type=request.POST.get('medal_type', 'star'),
        )
        messages.success(request, f'¡{student.first_name} ingresó al Salón de la Fama! 🏆')
        return redirect('fame_board')

    context = {'entries': entries, 'students': students}
    return render(request, 'teacher/fame_board.html', context)


@login_required
@teacher_required
def announcements_view(request):
    announcements = Announcement.objects.filter(teacher=request.user)

    if request.method == 'POST':
        Announcement.objects.create(
            title=request.POST.get('title', ''),
            message=request.POST.get('message', ''),
            announcement_type=request.POST.get('announcement_type', 'info'),
            teacher=request.user,
        )
        messages.success(request, '¡Aviso publicado! 📢')
        return redirect('announcements')

    return render(request, 'teacher/announcements.html', {'announcements': announcements})


@login_required
@student_required
def student_dashboard(request):
    my_submissions = ActivitySubmission.objects.filter(student=request.user)

    assigned_activities = Activity.objects.filter(
        status='published'
    ).filter(
        Q(assigned_to_all=True) | Q(assigned_students=request.user)
    ).distinct()

    completed_ids = my_submissions.filter(
        status__in=['submitted', 'reviewed', 'approved']
    ).values_list('activity_id', flat=True)

    pending = assigned_activities.exclude(id__in=completed_ids).count()
    completed_games = GameSession.objects.filter(
        student=request.user, is_completed=True
    ).count()
    fame_entries = FameBoardEntry.objects.filter(student=request.user, is_active=True)
    announcements = Announcement.objects.filter(is_active=True).order_by('-created_at')[:3]

    try:
        profile = request.user.student_profile
    except Exception:
        profile = None

    context = {
        'profile': profile,
        'pending_tasks': pending,
        'completed_games': completed_games,
        'fame_entries': fame_entries,
        'announcements': announcements,
        'recent_submissions': my_submissions.filter(
            status='approved'
        ).select_related('activity__category').order_by('-submitted_at')[:3],
    }
    return render(request, 'student/dashboard.html', context)


@login_required
@student_required
def student_logros(request):
    fame_entries = FameBoardEntry.objects.filter(
        student=request.user, is_active=True
    ).order_by('-created_at')

    ctx = _student_sidebar_context(request.user)
    ctx.update({'fame_entries': fame_entries})
    return render(request, 'student/logros.html', ctx)
