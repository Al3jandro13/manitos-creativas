from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
import json

from .models import ColoringImage, Game, GameSession, PuzzleImage
from apps.accounts.decorators import student_required, teacher_required
from apps.classroom.views import _student_sidebar_context
from apps.activities.models import Activity, ActivityCategory, ActivitySubmission


@login_required
@student_required
def games_home(request):
    games = Game.objects.filter(is_active=True)
    sessions = GameSession.objects.filter(student=request.user, is_completed=True)
    completed_ids = set(sessions.values_list('game_id', flat=True))

    ctx = _student_sidebar_context(request.user)
    ctx.update({
        'games': games,
        'completed_ids': completed_ids,
        'total_games': games.count(),
        'completed_count': len(completed_ids),
    })
    return render(request, 'student/games/home.html', ctx)


def _activity_ctx(request):
    """Return activity and existing submission if activity_id is in GET params."""
    from apps.activities.models import Activity, ActivitySubmission
    activity_id = request.GET.get('activity_id')
    activity = submission = None
    if activity_id:
        try:
            activity = Activity.objects.get(pk=activity_id, status='published')
            submission = ActivitySubmission.objects.filter(
                activity=activity, student=request.user
            ).first()
        except Activity.DoesNotExist:
            pass
    return {'activity': activity, 'submission': submission, 'activity_id': activity_id}


@login_required
@student_required
def game_puzzle(request):
    puzzle_images = PuzzleImage.objects.filter(is_active=True).select_related('teacher')
    ctx = _student_sidebar_context(request.user)
    ctx['puzzle_images'] = puzzle_images
    ctx.update(_activity_ctx(request))
    return render(request, 'student/games/puzzle.html', ctx)


@login_required
@student_required
def game_coloring(request):
    coloring_images = ColoringImage.objects.filter(is_active=True).select_related('teacher')
    ctx = _student_sidebar_context(request.user)
    ctx['coloring_images'] = coloring_images
    ctx.update(_activity_ctx(request))
    return render(request, 'student/games/coloring.html', ctx)


@login_required
@student_required
def game_drawing(request):
    ctx = _student_sidebar_context(request.user)
    ctx.update(_activity_ctx(request))
    return render(request, 'student/games/drawing.html', ctx)


@login_required
@student_required
def game_numbers(request):
    ctx = _student_sidebar_context(request.user)
    ctx.update(_activity_ctx(request))
    return render(request, 'student/games/numbers.html', ctx)


@login_required
@student_required
def game_consonants(request):
    ctx = _student_sidebar_context(request.user)
    ctx.update(_activity_ctx(request))
    return render(request, 'student/games/consonants.html', ctx)


@login_required
@student_required
def game_math(request):
    game_type = request.GET.get('type', 'add')
    ctx = _student_sidebar_context(request.user)
    ctx['game_type'] = game_type
    ctx.update(_activity_ctx(request))
    return render(request, 'student/games/math.html', ctx)


@login_required
@student_required
def game_puntillismo(request):
    ctx = _student_sidebar_context(request.user)
    ctx.update(_activity_ctx(request))
    return render(request, 'student/games/puntillismo.html', ctx)


@login_required
@student_required
def game_signs(request):
    ctx = _student_sidebar_context(request.user)
    ctx.update(_activity_ctx(request))
    return render(request, 'student/games/signs.html', ctx)


@login_required
@student_required
def game_story(request):
    ctx = _student_sidebar_context(request.user)
    ctx.update(_activity_ctx(request))
    return render(request, 'student/games/story.html', ctx)


@login_required
@student_required
def game_wordsearch(request):
    ctx = _student_sidebar_context(request.user)
    ctx.update(_activity_ctx(request))
    return render(request, 'student/games/wordsearch.html', ctx)


@login_required
@student_required
def game_snake(request):
    ctx = _student_sidebar_context(request.user)
    ctx.update(_activity_ctx(request))
    return render(request, 'student/games/snake.html', ctx)


@login_required
@student_required
def game_memory(request):
    ctx = _student_sidebar_context(request.user)
    ctx.update(_activity_ctx(request))
    return render(request, 'student/games/memory.html', ctx)


@login_required
@student_required
def game_counting(request):
    ctx = _student_sidebar_context(request.user)
    ctx.update(_activity_ctx(request))
    return render(request, 'student/games/counting.html', ctx)


@login_required
@student_required
def game_shapes(request):
    ctx = _student_sidebar_context(request.user)
    ctx.update(_activity_ctx(request))
    return render(request, 'student/games/shapes.html', ctx)


@login_required
@student_required
def game_place_value(request):
    ctx = _student_sidebar_context(request.user)
    ctx.update(_activity_ctx(request))
    return render(request, 'student/games/place_value.html', ctx)


@login_required
@student_required
def game_mixing(request):
    ctx = _student_sidebar_context(request.user)
    ctx.update(_activity_ctx(request))
    return render(request, 'student/games/mixing.html', ctx)


@login_required
@student_required
def game_train_syllables(request):
    ctx = _student_sidebar_context(request.user)
    ctx.update(_activity_ctx(request))
    return render(request, 'student/games/train_syllables.html', ctx)


@login_required
@student_required
def game_puppet(request):
    ctx = _student_sidebar_context(request.user)
    ctx.update(_activity_ctx(request))
    return render(request, 'student/games/puppet.html', ctx)


@login_required
@student_required
def game_crazy_face(request):
    ctx = _student_sidebar_context(request.user)
    ctx.update(_activity_ctx(request))
    return render(request, 'student/games/crazy_face.html', ctx)


@login_required
@student_required
def game_rocket(request):
    ctx = _student_sidebar_context(request.user)
    ctx.update(_activity_ctx(request))
    return render(request, 'student/games/rocket.html', ctx)


@login_required
@student_required
def game_rocket_coop(request):
    ctx = _student_sidebar_context(request.user)
    ctx.update(_activity_ctx(request))
    return render(request, 'student/games/rocket_coop.html', ctx)


@login_required
@student_required
def game_house(request):
    ctx = _student_sidebar_context(request.user)
    ctx.update(_activity_ctx(request))
    return render(request, 'student/games/house.html', ctx)


@login_required
@student_required
def game_shadows(request):
    ctx = _student_sidebar_context(request.user)
    ctx.update(_activity_ctx(request))
    return render(request, 'student/games/shadows.html', ctx)


@login_required
@teacher_required
def teacher_games_hub(request):
    from .models import PuzzleImage, ColoringImage
    context = {
        'puzzle_count': PuzzleImage.objects.filter(teacher=request.user).count(),
        'coloring_count': ColoringImage.objects.filter(teacher=request.user).count(),
    }
    return render(request, 'teacher/games_hub.html', context)


@login_required
@teacher_required
def coloring_images_list(request):
    images = ColoringImage.objects.filter(teacher=request.user).order_by('-created_at')
    return render(request, 'teacher/coloring_images.html', {'images': images})


@login_required
@teacher_required
@require_POST
def coloring_image_upload(request):
    title = request.POST.get('title', '').strip()
    image = request.FILES.get('image')
    if not title or not image:
        messages.error(request, 'El título y la imagen son requeridos.')
        return redirect('coloring_images_list')
    ColoringImage.objects.create(teacher=request.user, title=title, image=image)
    messages.success(request, f'¡Boceto "{title}" subido exitosamente!')
    return redirect('coloring_images_list')


@login_required
@teacher_required
@require_POST
def coloring_image_edit(request, pk):
    img = get_object_or_404(ColoringImage, pk=pk, teacher=request.user)
    title = request.POST.get('title', '').strip()
    if not title:
        messages.error(request, 'El título no puede estar vacío.')
        return redirect('coloring_images_list')
    img.title = title
    new_image = request.FILES.get('image')
    if new_image:
        img.image = new_image
    img.save()
    messages.success(request, f'Boceto "{title}" actualizado.')
    return redirect('coloring_images_list')


@login_required
@teacher_required
def coloring_image_delete(request, pk):
    image = get_object_or_404(ColoringImage, pk=pk, teacher=request.user)
    if request.method == 'POST':
        title = image.title
        image.delete()
        messages.success(request, f'Boceto "{title}" eliminado.')
    return redirect('coloring_images_list')


@login_required
@teacher_required
def puzzle_images_list(request):
    images = PuzzleImage.objects.filter(teacher=request.user).order_by('-created_at')
    return render(request, 'teacher/puzzle_images.html', {'images': images})


@login_required
@teacher_required
@require_POST
def puzzle_image_upload(request):
    title = request.POST.get('title', '').strip()
    image = request.FILES.get('image')
    if not title or not image:
        messages.error(request, 'El título y la imagen son requeridos.')
        return redirect('puzzle_images_list')
    PuzzleImage.objects.create(teacher=request.user, title=title, image=image)
    messages.success(request, f'¡Imagen "{title}" subida exitosamente!')
    return redirect('puzzle_images_list')


@login_required
@teacher_required
@require_POST
def puzzle_image_edit(request, pk):
    img = get_object_or_404(PuzzleImage, pk=pk, teacher=request.user)
    title = request.POST.get('title', '').strip()
    if not title:
        messages.error(request, 'El título no puede estar vacío.')
        return redirect('puzzle_images_list')
    img.title = title
    new_image = request.FILES.get('image')
    if new_image:
        img.image = new_image
    img.save()
    messages.success(request, f'Imagen "{title}" actualizada.')
    return redirect('puzzle_images_list')


@login_required
@teacher_required
def puzzle_image_delete(request, pk):
    image = get_object_or_404(PuzzleImage, pk=pk, teacher=request.user)
    if request.method == 'POST':
        title = image.title
        image.delete()
        messages.success(request, f'Imagen "{title}" eliminada.')
    return redirect('puzzle_images_list')


@require_POST
@login_required
def save_game_score(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)

    try:
        score = int(data.get('score', 0))
        stars_client = int(data.get('stars_earned', data.get('stars', 0)))
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'Valores numéricos inválidos'}, status=400)

    game_type = data.get('game_type', '')
    try:
        game = Game.objects.get(game_type=game_type)
    except Game.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Juego no reconocido'}, status=400)

    stars = min(stars_client, game.stars_reward)

    GameSession.objects.create(
        student=request.user,
        game=game,
        score=score,
        stars_earned=stars,
        is_completed=True,
        completed_at=timezone.now(),
    )

    if stars > 0:
        try:
            request.user.student_profile.add_stars(stars)
        except Exception:
            pass

    # Save ActivitySubmission — prefer explicit activity_id, fall back to category match
    activity_id = data.get('activity_id')
    drawing_data = data.get('drawing_data', '')

    activity = None
    if activity_id:
        try:
            activity = Activity.objects.get(pk=activity_id, status='published')
        except Activity.DoesNotExist:
            pass

    if not activity:
        GAME_TO_CATEGORY = {
            'puzzle': 'rompecabezas',
            'coloring': 'colorear',
            'drawing': 'dibujo_libre',
            'puntillismo': 'puntillismo',
            'consonants': 'consonantes',
            'numbers': 'numeros',
            'math_add': 'sumas',
            'math_sub': 'restas',
            'snake': 'serpiente',
            'wordsearch': 'sopa_letras',
            'story': 'cuento',
            'memory': 'memoria',
            'counting': 'contar_objetos',
            'shapes': 'figuras',
            'place_value': 'valor_posicional',
            'mixing': 'colorear',
            'train_syllables': 'consonantes',
            'puppet': 'dibujo_libre',
            'crazy_face': 'cara_loca',
            'rocket': 'exploracion',
            'rocket_coop': 'exploracion',
            'house': 'constructor',
            'shadows': 'sombras',
        }
        category_name = GAME_TO_CATEGORY.get(game_type)
        if category_name:
            activity = Activity.objects.filter(
                status='published',
                category__name=category_name,
            ).filter(
                models.Q(assigned_to_all=True) | models.Q(assigned_students=request.user)
            ).first()

    if activity:
        try:
            content = f'Puntaje: {score} | Estrellas: {stars}'
            sub, _ = ActivitySubmission.objects.get_or_create(
                activity=activity, student=request.user,
            )
            if sub.status != 'approved':
                sub.content = content
                if drawing_data:
                    sub.drawing_data = drawing_data
                sub.status = 'submitted'
                sub.submitted_at = timezone.now()
                sub.save(update_fields=['content', 'drawing_data', 'status', 'submitted_at'])
        except Exception:
            pass

    total = 0
    try:
        total = request.user.student_profile.total_stars
    except Exception:
        pass

    return JsonResponse({'success': True, 'stars_earned': stars, 'total_stars': total})
