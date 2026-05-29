from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import GradeRecord, WeeklyReport
from apps.accounts.decorators import teacher_required
from apps.accounts.models import CustomUser


@login_required
@teacher_required
def grades_view(request):
    students = CustomUser.objects.filter(role='student').select_related('student_profile')
    selected_student_id = request.GET.get('student')
    selected_student = None
    grades = []

    if selected_student_id:
        selected_student = get_object_or_404(CustomUser, id=selected_student_id, role='student')
        grades = GradeRecord.objects.filter(
            student=selected_student, teacher=request.user
        ).order_by('-created_at')

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        student = get_object_or_404(CustomUser, id=student_id, role='student')
        try:
            grade = float(request.POST.get('grade', 0))
        except (ValueError, TypeError):
            messages.error(request, 'El valor de la nota es inválido.')
            return redirect('grades')
        GradeRecord.objects.create(
            student=student,
            teacher=request.user,
            subject=request.POST.get('subject', ''),
            period=request.POST.get('period', ''),
            grade=grade,
            performance=request.POST.get('performance', 'B'),
            observations=request.POST.get('observations', ''),
            emotional_progress=request.POST.get('emotional_progress', ''),
        )
        messages.success(request, '✅ Nota guardada correctamente.')
        return redirect(f"{reverse('grades')}?student={student_id}")

    context = {
        'students': students,
        'selected_student': selected_student,
        'grades': grades,
    }
    return render(request, 'teacher/grades.html', context)


@login_required
@teacher_required
def weekly_reports_view(request):
    students = CustomUser.objects.filter(role='student').select_related('student_profile')

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        student = get_object_or_404(CustomUser, id=student_id, role='student')
        try:
            creativity_score = int(request.POST.get('creativity_score', 5))
            behavior_score = int(request.POST.get('behavior_score', 5))
            progress_score = int(request.POST.get('progress_score', 5))
            participation_score = int(request.POST.get('participation_score', 5))
            attendance_score = int(request.POST.get('attendance_score', 5))
        except (ValueError, TypeError):
            messages.error(request, 'Los puntajes deben ser números enteros.')
            return redirect('weekly_reports')
        WeeklyReport.objects.create(
            student=student,
            teacher=request.user,
            week_start=request.POST.get('week_start'),
            week_end=request.POST.get('week_end'),
            creativity_score=creativity_score,
            behavior_score=behavior_score,
            progress_score=progress_score,
            participation_score=participation_score,
            attendance_score=attendance_score,
            observations=request.POST.get('observations', ''),
            achievements=request.POST.get('achievements', ''),
            recommendations=request.POST.get('recommendations', ''),
        )
        messages.success(request, '📊 Reporte semanal guardado.')
        return redirect('weekly_reports')

    reports = WeeklyReport.objects.filter(teacher=request.user).select_related('student')
    context = {'students': students, 'reports': reports[:20]}
    return render(request, 'teacher/reports.html', context)
