from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from .models import Activity, ActivityCategory, ActivitySubmission
from apps.accounts.decorators import teacher_required, student_required
from apps.accounts.models import CustomUser
from apps.classroom.views import _student_sidebar_context


# ─── TEACHER VIEWS ────────────────────────────────────────────────────────────

@login_required
@teacher_required
def teacher_activity_list(request):
    activities = Activity.objects.filter(teacher=request.user)
    stats = activities.aggregate(
        total=Count('id'),
        published=Count('id', filter=Q(status='published')),
        draft=Count('id', filter=Q(status='draft')),
    )
    context = {
        'activities': activities.select_related('category'),
        'categories': ActivityCategory.objects.all(),
        'total': stats['total'],
        'published': stats['published'],
        'draft': stats['draft'],
    }
    return render(request, 'teacher/tasks/list.html', context)


@login_required
@teacher_required
def teacher_activity_create(request):
    categories = ActivityCategory.objects.all()
    students = CustomUser.objects.filter(role='student').select_related('student_profile')

    if request.method == 'POST':
        data = request.POST
        try:
            category = get_object_or_404(ActivityCategory, id=data['category'])
            difficulty = int(data.get('difficulty', 1))
            reward_stars = int(data.get('reward_stars', 3))
            activity = Activity.objects.create(
                title=data['title'],
                description=data['description'],
                category=category,
                teacher=request.user,
                difficulty=difficulty,
                status=data.get('status', 'draft'),
                reward_stars=reward_stars,
                reward_sticker=data.get('reward_sticker', 'star'),
                instructions=data.get('instructions', ''),
                assigned_to_all=data.get('assigned_to_all') == 'on',
            )
            if data.get('due_date'):
                activity.due_date = data['due_date']
                activity.save()
            if request.FILES.get('image'):
                activity.image = request.FILES['image']
                activity.save()
            messages.success(request, f'¡Actividad "{activity.title}" creada! 🎉')
            return redirect('teacher_activity_list')
        except (ValueError, TypeError) as e:
            messages.error(request, f'Datos inválidos en el formulario: {e}')
        except Exception as e:
            messages.error(request, f'Error al crear: {e}')

    context = {'categories': categories, 'students': students}
    return render(request, 'teacher/tasks/create.html', context)


@login_required
@teacher_required
def teacher_activity_detail(request, pk):
    activity = get_object_or_404(Activity, pk=pk, teacher=request.user)
    submissions = activity.submissions.select_related('student').order_by('-submitted_at')
    context = {'activity': activity, 'submissions': submissions}
    return render(request, 'teacher/tasks/detail.html', context)


@login_required
@teacher_required
def review_submission(request, submission_id):
    submission = get_object_or_404(ActivitySubmission, id=submission_id,
                                   activity__teacher=request.user)
    if request.method == 'POST':
        try:
            stars = int(request.POST.get('stars_awarded', 0))
        except (ValueError, TypeError):
            stars = 0
        feedback = request.POST.get('teacher_feedback', '')
        featured = request.POST.get('is_featured') == 'on'

        submission.stars_awarded = stars
        submission.teacher_feedback = feedback
        submission.is_featured = featured
        submission.status = 'approved' if stars > 0 else 'reviewed'
        submission.reviewed_at = timezone.now()
        submission.save()

        if stars > 0:
            try:
                submission.student.student_profile.add_stars(stars)
            except Exception:
                pass

        messages.success(request, '¡Revisión guardada! ⭐')
        return redirect('teacher_activity_detail', pk=submission.activity.pk)

    return render(request, 'teacher/tasks/review.html', {'submission': submission})


# ─── STUDENT VIEWS ────────────────────────────────────────────────────────────

@login_required
@student_required
def student_activities(request):
    published = Activity.objects.filter(
        status='published'
    ).filter(
        Q(assigned_to_all=True) | Q(assigned_students=request.user)
    ).distinct().select_related('category', 'teacher')

    submitted_ids = set(ActivitySubmission.objects.filter(
        student=request.user, status__in=['submitted', 'reviewed', 'approved']
    ).values_list('activity_id', flat=True))

    ctx = _student_sidebar_context(request.user)
    ctx.update({
        'activities': published,
        'submitted_ids': submitted_ids,
        'completed_count': len(submitted_ids),
        'total_count': published.count(),
    })
    return render(request, 'student/activities.html', ctx)


@login_required
@student_required
def student_activity_detail(request, pk):
    activity = get_object_or_404(Activity, pk=pk, status='published')
    submission = ActivitySubmission.objects.filter(
        activity=activity, student=request.user
    ).first()

    if request.method == 'POST':
        # Don't allow overwriting an already-approved submission.
        if submission and submission.status == 'approved':
            messages.warning(request, '¡Esta actividad ya fue aprobada por tu profe! 🌟')
            return redirect('student_activities')

        if not submission:
            submission = ActivitySubmission(activity=activity, student=request.user)

        submission.drawing_data = request.POST.get('drawing_data', '')
        submission.content = request.POST.get('notes', '')
        submission.status = 'submitted'
        submission.submitted_at = timezone.now()
        submission.save()

        # Stars are awarded by the teacher during review, not on bare submission.
        messages.success(request, '¡Actividad enviada! Tu profe la revisará pronto. 🚀')
        return redirect('student_activities')

    context = {'activity': activity, 'submission': submission}
    return render(request, 'student/activity_detail.html', context)
