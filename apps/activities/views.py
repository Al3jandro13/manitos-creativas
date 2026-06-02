from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from .models import Activity, ActivityCategory, ActivitySubmission, CoopActivity, CoopSubmission
from apps.accounts.decorators import teacher_required, student_required
from apps.accounts.models import CustomUser
from apps.classroom.models import FameBoardEntry
from apps.classroom.views import _student_sidebar_context
from apps.games.models import ColoringImage, PuzzleImage


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
        'categories': ActivityCategory.objects.filter(
            name__in=[c[0] for c in ActivityCategory.CATEGORY_CHOICES]
        ),
        'total': stats['total'],
        'published': stats['published'],
        'draft': stats['draft'],
    }
    return render(request, 'teacher/tasks/list.html', context)


@login_required
@teacher_required
def teacher_activity_create(request):
    valid_names = [c[0] for c in ActivityCategory.CATEGORY_CHOICES]
    categories = ActivityCategory.objects.filter(name__in=valid_names)
    students = CustomUser.objects.filter(role='student').select_related('student_profile')

    if request.method == 'POST':
        data = request.POST
        try:
            category = get_object_or_404(ActivityCategory, id=data['category'])
            reward_stars = int(data.get('reward_stars', 3))
            activity = Activity.objects.create(
                title=data['title'],
                description=data['description'],
                category=category,
                teacher=request.user,
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
            return redirect('activities_list')
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
def teacher_activity_edit(request, pk):
    activity = get_object_or_404(Activity, pk=pk, teacher=request.user)
    if request.method == 'POST':
        valid_names = [c[0] for c in ActivityCategory.CATEGORY_CHOICES]
        try:
            category = get_object_or_404(ActivityCategory, id=request.POST['category'])
            activity.title = request.POST.get('title', activity.title)
            activity.description = request.POST.get('description', activity.description)
            activity.category = category
            activity.status = request.POST.get('status', activity.status)
            activity.reward_stars = int(request.POST.get('reward_stars', activity.reward_stars))
            activity.instructions = request.POST.get('instructions', activity.instructions)
            due_date = request.POST.get('due_date', '')
            activity.due_date = due_date if due_date else None
            if request.FILES.get('image'):
                activity.image = request.FILES['image']
            activity.save()
            messages.success(request, f'Actividad "{activity.title}" actualizada. ✏️')
        except Exception as e:
            messages.error(request, f'Error al actualizar: {e}')
    return redirect('activities_list')


@login_required
@teacher_required
@require_POST
def teacher_activity_delete(request, pk):
    activity = get_object_or_404(Activity, pk=pk, teacher=request.user)
    title = activity.title
    activity.delete()
    messages.success(request, f'Actividad "{title}" eliminada.')
    return redirect('activities_list')


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
        medal_type = request.POST.get('medal_type', 'star')

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

        if featured:
            FameBoardEntry.objects.update_or_create(
                submission=submission,
                defaults={
                    'student': submission.student,
                    'teacher': request.user,
                    'title': request.POST.get('fame_title') or f'¡Excelente trabajo en {submission.activity.title}!',
                    'description': feedback,
                    'medal_type': medal_type,
                    'is_active': True,
                },
            )
        else:
            FameBoardEntry.objects.filter(submission=submission).delete()

        back = request.POST.get('back', '')
        messages.success(request, '¡Revisión guardada! ⭐')
        if back == 'overview':
            return redirect('submissions_overview')
        return redirect('teacher_activity_detail', pk=submission.activity.pk)

    return render(request, 'teacher/tasks/review.html', {'submission': submission})


@login_required
@teacher_required
def submissions_overview(request):
    qs = ActivitySubmission.objects.filter(
        activity__teacher=request.user
    ).select_related('student', 'activity__category').order_by('-submitted_at')

    activity_filter = request.GET.get('activity', '')
    status_filter = request.GET.get('status', '')
    if activity_filter:
        qs = qs.filter(activity_id=activity_filter)
    if status_filter:
        qs = qs.filter(status=status_filter)

    activities = Activity.objects.filter(teacher=request.user).order_by('title')
    featured_submission_ids = set(
        FameBoardEntry.objects.filter(
            teacher=request.user, submission__isnull=False
        ).values_list('submission_id', flat=True)
    )

    context = {
        'submissions': qs,
        'activities': activities,
        'activity_filter': activity_filter,
        'status_filter': status_filter,
        'featured_ids': featured_submission_ids,
    }
    return render(request, 'teacher/tasks/submissions_overview.html', context)


@login_required
@teacher_required
@require_POST
def quick_feature_submission(request, submission_id):
    submission = get_object_or_404(ActivitySubmission, id=submission_id,
                                   activity__teacher=request.user)
    existing = FameBoardEntry.objects.filter(submission=submission).first()
    if existing:
        existing.delete()
        submission.is_featured = False
    else:
        FameBoardEntry.objects.create(
            submission=submission,
            student=submission.student,
            teacher=request.user,
            title=f'¡Excelente trabajo en {submission.activity.title}!',
            description=submission.teacher_feedback or '',
            medal_type='star',
            is_active=True,
        )
        submission.is_featured = True
    submission.save(update_fields=['is_featured'])
    return redirect('submissions_overview')


# ─── STUDENT VIEWS ────────────────────────────────────────────────────────────

@login_required
@student_required
def student_activities(request):
    published = Activity.objects.filter(
        status='published'
    ).filter(
        Q(assigned_to_all=True) | Q(assigned_students=request.user)
    ).distinct().select_related('category', 'teacher')

    submissions = ActivitySubmission.objects.filter(
        student=request.user, status__in=['submitted', 'reviewed', 'approved']
    )
    submission_map = {s.activity_id: s for s in submissions}

    ctx = _student_sidebar_context(request.user)
    ctx.update({
        'activities': published,
        'submitted_ids': set(submission_map.keys()),
        'submission_map': submission_map,
        'completed_count': len(submission_map),
        'total_count': published.count(),
    })
    return render(request, 'student/activities.html', ctx)


CATEGORY_GAME_URL = {
    'colorear':     ('game_coloring', {}),
    'puntillismo':  ('game_puntillismo', {}),
    'dibujo_libre': ('game_drawing', {}),
    'rompecabezas': ('game_puzzle', {}),
    'cuento':       ('game_story', {}),
    'consonantes':  ('game_consonants', {}),
    'numeros':      ('game_numbers', {}),
    'sumas':        ('game_math', {'type': 'add'}),
    'restas':       ('game_math', {'type': 'sub'}),
    'serpiente':    ('game_snake', {}),
    'sopa_letras':  ('game_wordsearch', {}),
    'memoria':      ('game_memory', {}),
    'contar_objetos': ('game_counting', {}),
    'figuras':      ('game_shapes', {}),
}


@login_required
@student_required
def student_activity_detail(request, pk):
    from django.urls import reverse
    activity = get_object_or_404(Activity, pk=pk, status='published')

    mapping = CATEGORY_GAME_URL.get(activity.category.name)
    if mapping:
        url_name, extra_params = mapping
        params = {'activity_id': pk, **extra_params}
        query = '&'.join(f'{k}={v}' for k, v in params.items())
        return redirect(f'{reverse(url_name)}?{query}')

    # Fallback for unmapped categories: generic canvas page
    submission = ActivitySubmission.objects.filter(
        activity=activity, student=request.user
    ).first()
    context = {
        'activity': activity,
        'submission': submission,
        'colors': ['#7C3AED','#EC4899','#FBBF24','#10B981','#3B82F6','#F97316','#1E1B4B','#EF4444','#FFFFFF'],
    }
    return render(request, 'student/activity_detail.html', context)


@login_required
@student_required
@require_POST
def student_delete_submission(request, pk):
    submission = get_object_or_404(ActivitySubmission, pk=pk, student=request.user)
    if submission.status == 'approved':
        messages.warning(request, 'No puedes eliminar una entrega ya aprobada.')
        return redirect('student_activities')
    submission.delete()
    messages.success(request, 'Entrega eliminada.')
    return redirect('student_activities')


# ─── COOP (ACTIVIDADES EN PAREJAS) ────────────────────────────────────────────

@login_required
@teacher_required
def coop_list(request):
    coops = CoopActivity.objects.filter(teacher=request.user).select_related(
        'category', 'student1', 'student2'
    ).prefetch_related('submissions')

    in_progress_count = 0
    completed_count = 0
    for coop in coops:
        subs = list(coop.submissions.all())
        all_done = len(subs) == 2 and all(
            s.status in ('submitted', 'reviewed', 'approved') for s in subs
        )
        if all_done:
            completed_count += 1
        elif any(s.status in ('in_progress', 'submitted') for s in subs):
            in_progress_count += 1

    return render(request, 'teacher/coop/list.html', {
        'coops': coops,
        'total': coops.count(),
        'in_progress': in_progress_count,
        'completed': completed_count,
    })


@login_required
@teacher_required
def coop_create(request):
    categories = ActivityCategory.objects.filter(
        name__in=[c[0] for c in ActivityCategory.CATEGORY_CHOICES]
    )
    students = CustomUser.objects.filter(role='student').select_related('student_profile')
    coloring_images = ColoringImage.objects.filter(is_active=True).order_by('-created_at')
    puzzle_images = PuzzleImage.objects.filter(is_active=True).order_by('-created_at')

    if request.method == 'POST':
        try:
            category = get_object_or_404(ActivityCategory, id=request.POST['category'])
            student1 = get_object_or_404(CustomUser, id=request.POST['student1'], role='student')
            student2 = get_object_or_404(CustomUser, id=request.POST['student2'], role='student')
            if student1 == student2:
                messages.error(request, 'Los dos estudiantes deben ser diferentes.')
            else:
                coloring_image = None
                puzzle_image = None
                puzzle_rows, puzzle_cols = 2, 4

                if category.name == 'colorear' and request.POST.get('coloring_image'):
                    coloring_image = ColoringImage.objects.filter(
                        id=request.POST['coloring_image'], is_active=True
                    ).first()
                elif category.name == 'rompecabezas' and request.POST.get('puzzle_image'):
                    puzzle_image = PuzzleImage.objects.filter(
                        id=request.POST['puzzle_image'], is_active=True
                    ).first()
                    try:
                        puzzle_rows = max(2, min(4, int(request.POST.get('puzzle_rows', 2))))
                        puzzle_cols = max(2, min(6, int(request.POST.get('puzzle_cols', 4))))
                        if puzzle_cols % 2 != 0:
                            puzzle_cols += 1  # garantiza divisibilidad por 2
                    except (ValueError, TypeError):
                        pass

                coop = CoopActivity.objects.create(
                    title=request.POST['title'],
                    description=request.POST.get('description', ''),
                    category=category,
                    teacher=request.user,
                    student1=student1,
                    student2=student2,
                    instructions=request.POST.get('instructions', ''),
                    reward_stars=int(request.POST.get('reward_stars', 5)),
                    coloring_image=coloring_image,
                    puzzle_image=puzzle_image,
                    puzzle_rows=puzzle_rows,
                    puzzle_cols=puzzle_cols,
                )
                CoopSubmission.objects.create(
                    coop_activity=coop, student=student1, step=1, status='in_progress',
                )
                CoopSubmission.objects.create(
                    coop_activity=coop, student=student2, step=2, status='waiting',
                )
                messages.success(request, f'¡Actividad en pareja "{coop.title}" creada! 🎉')
                return redirect('coop_list')
        except (ValueError, TypeError) as e:
            messages.error(request, f'Datos inválidos: {e}')
        except Exception as e:
            messages.error(request, f'Error al crear: {e}')

    return render(request, 'teacher/coop/create.html', {
        'categories': categories,
        'students': students,
        'coloring_images': coloring_images,
        'puzzle_images': puzzle_images,
    })


@login_required
@teacher_required
def coop_detail(request, pk):
    coop = get_object_or_404(CoopActivity, pk=pk, teacher=request.user)
    subs = {s.step: s for s in coop.submissions.select_related('student').all()}
    sub1 = subs.get(1)
    sub2 = subs.get(2)
    can_review = (
        sub1 and sub2 and
        sub1.status in ('submitted', 'reviewed', 'approved') and
        sub2.status in ('submitted', 'reviewed', 'approved')
    )
    return render(request, 'teacher/coop/detail.html', {
        'coop': coop,
        'sub1': sub1,
        'sub2': sub2,
        'can_review': can_review,
    })


@login_required
@teacher_required
def coop_edit(request, pk):
    coop = get_object_or_404(CoopActivity, pk=pk, teacher=request.user)
    categories = ActivityCategory.objects.filter(
        name__in=[c[0] for c in ActivityCategory.CATEGORY_CHOICES]
    )
    students = CustomUser.objects.filter(role='student').select_related('student_profile')
    coloring_images = ColoringImage.objects.filter(is_active=True).order_by('-created_at')
    puzzle_images = PuzzleImage.objects.filter(is_active=True).order_by('-created_at')

    if request.method == 'POST':
        try:
            category = get_object_or_404(ActivityCategory, id=request.POST['category'])
            student1 = get_object_or_404(CustomUser, id=request.POST['student1'], role='student')
            student2 = get_object_or_404(CustomUser, id=request.POST['student2'], role='student')

            if student1 == student2:
                messages.error(request, 'Los dos estudiantes deben ser diferentes.')
            else:
                # Si cambiaron los estudiantes, actualizar las submissions
                pair_changed = (student1 != coop.student1) or (student2 != coop.student2)

                coop.title = request.POST['title']
                coop.description = request.POST.get('description', '')
                coop.category = category
                coop.student1 = student1
                coop.student2 = student2
                coop.instructions = request.POST.get('instructions', '')
                coop.reward_stars = int(request.POST.get('reward_stars', 5))
                coop.status = request.POST.get('status', coop.status)

                if category.name == 'colorear' and request.POST.get('coloring_image'):
                    coop.coloring_image = ColoringImage.objects.filter(
                        id=request.POST['coloring_image'], is_active=True
                    ).first()
                else:
                    coop.coloring_image = None

                if category.name == 'rompecabezas' and request.POST.get('puzzle_image'):
                    coop.puzzle_image = PuzzleImage.objects.filter(
                        id=request.POST['puzzle_image'], is_active=True
                    ).first()
                    try:
                        coop.puzzle_rows = max(2, min(4, int(request.POST.get('puzzle_rows', 2))))
                        cols = max(2, min(6, int(request.POST.get('puzzle_cols', 4))))
                        coop.puzzle_cols = cols + (cols % 2)
                    except (ValueError, TypeError):
                        pass
                else:
                    coop.puzzle_image = None
                coop.save()

                # Si la pareja cambió, recrear las submissions
                if pair_changed:
                    coop.submissions.all().delete()
                    CoopSubmission.objects.create(
                        coop_activity=coop, student=student1, step=1, status='in_progress',
                    )
                    CoopSubmission.objects.create(
                        coop_activity=coop, student=student2, step=2, status='waiting',
                    )

                messages.success(request, f'¡Actividad "{coop.title}" actualizada! ✏️')
                return redirect('coop_detail', pk=coop.pk)
        except (ValueError, TypeError) as e:
            messages.error(request, f'Datos inválidos: {e}')
        except Exception as e:
            messages.error(request, f'Error al actualizar: {e}')

    return render(request, 'teacher/coop/edit.html', {
        'coop': coop,
        'categories': categories,
        'students': students,
        'coloring_images': coloring_images,
        'puzzle_images': puzzle_images,
    })


@login_required
@teacher_required
@require_POST
def coop_delete(request, pk):
    coop = get_object_or_404(CoopActivity, pk=pk, teacher=request.user)
    title = coop.title
    coop.delete()  # cascade: borra automáticamente las CoopSubmission asociadas
    messages.success(request, f'Actividad "{title}" eliminada. 🗑️')
    return redirect('coop_list')


@login_required
@teacher_required
def coop_review(request, coop_pk):
    coop = get_object_or_404(CoopActivity, pk=coop_pk, teacher=request.user)
    subs = {s.step: s for s in coop.submissions.select_related('student').all()}
    sub1 = subs.get(1)
    sub2 = subs.get(2)

    if request.method == 'POST':
        feedback = request.POST.get('teacher_feedback', '')
        try:
            stars1 = max(0, min(5, int(request.POST.get('stars1', 0))))
            stars2 = max(0, min(5, int(request.POST.get('stars2', 0))))
        except (ValueError, TypeError):
            stars1, stars2 = 0, 0

        for sub, stars in [(sub1, stars1), (sub2, stars2)]:
            if sub:
                sub.teacher_feedback = feedback
                sub.stars_awarded = stars
                sub.status = 'approved' if stars > 0 else 'reviewed'
                sub.reviewed_at = timezone.now()
                sub.save()
                if stars > 0:
                    try:
                        sub.student.student_profile.add_stars(stars)
                    except Exception:
                        pass

        messages.success(request, '¡Revisión guardada! ⭐')
        return redirect('coop_detail', pk=coop_pk)

    return render(request, 'teacher/coop/review.html', {
        'coop': coop,
        'sub1': sub1,
        'sub2': sub2,
    })


@login_required
@student_required
def student_coop_list(request):
    coops = CoopActivity.objects.filter(
        Q(student1=request.user) | Q(student2=request.user),
        status='published',
    ).select_related('category', 'student1', 'student2')

    my_subs = {
        s.coop_activity_id: s
        for s in CoopSubmission.objects.filter(student=request.user)
    }

    coop_data = [(coop, my_subs.get(coop.id)) for coop in coops]

    ctx = _student_sidebar_context(request.user)
    ctx.update({'coop_data': coop_data})
    return render(request, 'student/coop/list.html', ctx)


@login_required
@student_required
def student_coop_work(request, pk):
    coop = get_object_or_404(
        CoopActivity.objects.filter(
            Q(student1=request.user) | Q(student2=request.user)
        ),
        pk=pk,
        status='published',
    )

    my_sub = get_object_or_404(CoopSubmission, coop_activity=coop, student=request.user)
    partner = coop.student1 if request.user == coop.student2 else coop.student2
    partner_sub = CoopSubmission.objects.filter(coop_activity=coop, student=partner).first()

    if request.method == 'POST' and my_sub.status == 'in_progress':
        my_sub.drawing_data = request.POST.get('drawing_data', '')
        my_sub.status = 'submitted'
        my_sub.submitted_at = timezone.now()
        my_sub.save()

        if my_sub.step == 1 and partner_sub and partner_sub.status == 'waiting':
            partner_sub.status = 'in_progress'
            partner_sub.save()

        messages.success(request, '¡Tu parte fue enviada! 🌟')
        return redirect('student_coop_list')

    can_work = my_sub.status == 'in_progress'
    waiting_for_partner = my_sub.step == 2 and my_sub.status == 'waiting'
    already_submitted = my_sub.status in ('submitted', 'reviewed', 'approved')

    ctx = _student_sidebar_context(request.user)
    ctx.update({
        'coop': coop,
        'my_sub': my_sub,
        'partner': partner,
        'partner_sub': partner_sub,
        'can_work': can_work,
        'waiting_for_partner': waiting_for_partner,
        'already_submitted': already_submitted,
    })

    # Routing por categoría
    if coop.category.name == 'rompecabezas':
        half_cols = coop.puzzle_cols // 2
        ctx['total_my_pieces'] = coop.puzzle_rows * half_cols
        return render(request, 'student/coop/puzzle_work.html', ctx)

    if coop.category.name == 'sopa_letras_coop':
        # Palabras del compañero para mostrar en paso 2
        import json
        total_words = 12  # fijo (mismo que el template usa)
        half_count = 6
        ctx['half_count']   = half_count
        ctx['second_count'] = total_words - half_count
        ctx['total_words']  = total_words
        return render(request, 'student/coop/wordsearch_work.html', ctx)

    if coop.category.name == 'cuento_coop':
        return render(request, 'student/coop/story_work.html', ctx)

    # mural_coop + dibujo_libre + puntillismo + colorear → lienzo dividido
    return render(request, 'student/coop/work.html', ctx)
