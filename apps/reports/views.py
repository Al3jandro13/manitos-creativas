import json
import os

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import GeneratedDocument
from .pdf_utils import generate_document_pdf


def _teacher_required(view_fn):
    """Decorator: login + teacher role required."""
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_teacher:
            return redirect('student_dashboard')
        return view_fn(request, *args, **kwargs)
    wrapper.__name__ = view_fn.__name__
    return wrapper


@_teacher_required
def documents_list(request):
    docs = GeneratedDocument.objects.filter(teacher=request.user)
    return render(request, 'teacher/documents/list.html', {
        'documents': docs,
        'active_page': 'documents',
    })


@_teacher_required
def generate_document(request):
    if request.method == 'POST':
        doc_type   = request.POST.get('doc_type', 'circular')
        title      = request.POST.get('title', '').strip()
        doc_number = request.POST.get('doc_number', '').strip()
        recipient  = request.POST.get('recipient', '').strip()
        content    = request.POST.get('content', '').strip()

        if not title or not content:
            return render(request, 'teacher/documents/generate.html', {
                'error': 'El título y el contenido son obligatorios.',
                'form_data': request.POST,
                'doc_types': GeneratedDocument.DOCUMENT_TYPES,
                'active_page': 'documents',
            })

        doc = GeneratedDocument.objects.create(
            teacher=request.user,
            doc_type=doc_type,
            title=title,
            doc_number=doc_number,
            recipient=recipient,
            content=content,
        )

        pdf_bytes = generate_document_pdf(doc)
        filename  = f'documento_{doc.pk}.pdf'
        from django.core.files.base import ContentFile
        doc.pdf_file.save(filename, ContentFile(pdf_bytes), save=True)

        return redirect('documents_list')

    return render(request, 'teacher/documents/generate.html', {
        'doc_types': GeneratedDocument.DOCUMENT_TYPES,
        'active_page': 'documents',
    })


@_teacher_required
def download_document(request, pk):
    doc       = get_object_or_404(GeneratedDocument, pk=pk, teacher=request.user)
    pdf_bytes = generate_document_pdf(doc)
    safe_title = doc.title.replace(' ', '_')[:40]
    filename   = f'{doc.get_doc_type_display()}_{safe_title}.pdf'
    response   = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@_teacher_required
def preview_document(request, pk):
    doc       = get_object_or_404(GeneratedDocument, pk=pk, teacher=request.user)
    pdf_bytes = generate_document_pdf(doc)
    response  = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="preview.pdf"'
    return response


@require_POST
@_teacher_required
def delete_document(request, pk):
    doc = get_object_or_404(GeneratedDocument, pk=pk, teacher=request.user)
    if doc.pdf_file:
        try:
            path = doc.pdf_file.path
            if os.path.isfile(path):
                os.remove(path)
        except Exception:
            pass
    doc.delete()
    return redirect('documents_list')


@login_required
def ai_generate_document_text(request):
    """AJAX: generates document body text using Claude AI."""
    if not request.user.is_teacher:
        return JsonResponse({'error': 'No autorizado'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    doc_type  = data.get('doc_type', 'circular')
    title     = data.get('title', '').strip()
    recipient = data.get('recipient', '').strip()
    prompt    = data.get('prompt', '').strip()

    if not prompt:
        return JsonResponse({'error': 'Describe el contenido del documento.'}, status=400)

    from django.conf import settings
    api_key = getattr(settings, 'ANTHROPIC_API_KEY', '') or ''
    if not api_key:
        return JsonResponse({'error': 'API key de IA no configurada.'}, status=500)

    teacher_name = request.user.get_full_name() or request.user.username
    doc_label    = dict(GeneratedDocument.DOCUMENT_TYPES).get(doc_type, doc_type.capitalize())

    system_prompt = (
        "Eres una asistente experta en redacción de documentos institucionales para el "
        "Colegio San Francisco de Asís, en Santiago de Cali, Colombia. "
        f"Redactas documentos formales en nombre de la docente {teacher_name}. "
        "Tus textos son claros, formales, cálidos y en español colombiano. "
        "SOLO devuelves el cuerpo del documento (sin encabezado, sin saludo inicial, "
        "sin firma, sin fecha — esos los pone el sistema automáticamente). "
        "Usa párrafos bien estructurados. No uses markdown, solo texto plano con saltos de línea."
    )

    user_msg = (
        f"Tipo de documento: {doc_label}\n"
        f"Asunto/Título: {title}\n"
        f"Dirigido a: {recipient}\n\n"
        f"Instrucción: {prompt}"
    )

    try:
        import anthropic
        client   = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model='claude-sonnet-4-6',
            max_tokens=1200,
            system=system_prompt,
            messages=[{'role': 'user', 'content': user_msg}],
        )
        generated = response.content[0].text.strip()
        return JsonResponse({'content': generated})
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)
