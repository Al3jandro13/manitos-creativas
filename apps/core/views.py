from django.shortcuts import render
from apps.classroom.models import FameBoardEntry, Announcement


def landing_view(request):
    fame_entries = FameBoardEntry.objects.filter(is_active=True).select_related('student', 'submission')[:6]
    context = {'fame_entries': fame_entries}
    return render(request, 'landing/index.html', context)
