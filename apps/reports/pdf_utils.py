"""
PDF generation utilities for formal school documents.
Header matches Colegio San Francisco de Asís official format.
"""
import io
import os
from datetime import date

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

# --- Institutional colours (from the official header) ---
GREEN_DARK  = colors.HexColor('#1B5E20')   # dark green for main title row
GREEN_MID   = colors.HexColor('#388E3C')   # medium green accents
WHITE       = colors.white
BLACK       = colors.black
LIGHT_GRAY  = colors.HexColor('#F5F5F5')

# School data
SCHOOL_NAME    = 'COLEGIO SAN FRANCISCO DE ASÍS'
SCHOOL_SUBTITLE = 'Orden de Hermanos Menores Capuchinos'
SCHOOL_AREA    = 'Gestión de Educación y Formación'
SCHOOL_PROC    = 'Procedimiento de Acompañamiento Académico'
SCHOOL_VERSION = 'Versión: 1'
SCHOOL_CITY    = 'Santiago de Cali'


def _logo_image(height=2.0 * cm):
    """Returns an Image flowable for the school logo, resized to reduce PDF size."""
    from django.conf import settings
    from PIL import Image as PILImage

    images_dir = os.path.join(settings.BASE_DIR, 'static', 'images')
    for fname in ('school_logo.png', 'school_logo.webp', 'school_logo.jpg', 'logo.png'):
        candidate = os.path.join(images_dir, fname)
        if os.path.isfile(candidate):
            logo_path = candidate
            break
    else:
        return None

    # Resize the logo to a small thumbnail to keep PDF size lean
    pil_img = PILImage.open(logo_path).convert('RGBA')
    target_px = int(height * 3.78)  # ~96 dpi equivalent
    pil_img.thumbnail((target_px * 2, target_px * 2), PILImage.LANCZOS)

    buf = io.BytesIO()
    pil_img.save(buf, format='PNG', optimize=True)
    buf.seek(0)

    img = Image(buf)
    ratio = img.imageWidth / img.imageHeight
    img.drawHeight = height
    img.drawWidth  = height * ratio
    return img


def _signature_image(height=2.2 * cm):
    """Returns an Image flowable for the teacher's handwritten signature."""
    from django.conf import settings
    from PIL import Image as PILImage

    sig_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'firma_karen.png')
    if not os.path.isfile(sig_path):
        return None

    pil_img = PILImage.open(sig_path).convert('RGBA')

    # Place on transparent canvas — keeps any white background from the scan
    buf = io.BytesIO()
    pil_img.save(buf, format='PNG', optimize=True)
    buf.seek(0)

    img = Image(buf)
    ratio = img.imageWidth / img.imageHeight
    img.drawHeight = height
    img.drawWidth  = height * ratio
    return img


def _build_header_table(doc_type_label, doc_number, page_number, total_pages, doc_date):
    """
    Builds the official institutional header as a ReportLab Table.

    Layout (3 columns):
      Col 0 — logo (spans 4 rows)
      Col 1 — school name / area / procedure / doc title
      Col 2 — version / page / date (spans 3 rows), empty on row 3
    """
    logo = _logo_image(height=2.0 * cm)
    logo_cell = logo if logo else Paragraph('', ParagraphStyle('empty'))

    s_title = ParagraphStyle(
        'hdr_title',
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=WHITE,
        alignment=TA_CENTER,
        leading=13,
        spaceAfter=0,
    )
    s_subtitle = ParagraphStyle(
        'hdr_sub',
        fontName='Helvetica',
        fontSize=8,
        textColor=WHITE,
        alignment=TA_CENTER,
        leading=11,
    )
    s_area = ParagraphStyle(
        'hdr_area',
        fontName='Helvetica-Bold',
        fontSize=8,
        textColor=BLACK,
        alignment=TA_CENTER,
        leading=11,
    )
    s_meta = ParagraphStyle(
        'hdr_meta',
        fontName='Helvetica',
        fontSize=7.5,
        textColor=BLACK,
        alignment=TA_CENTER,
        leading=10,
    )
    s_doc = ParagraphStyle(
        'hdr_doc',
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=BLACK,
        alignment=TA_CENTER,
        leading=12,
    )

    title_cell = [
        Paragraph(SCHOOL_NAME, s_title),
        Paragraph(SCHOOL_SUBTITLE, s_subtitle),
    ]

    meta_cell = Paragraph(
        f'{SCHOOL_VERSION}<br/>Página {page_number} de {total_pages}<br/>{doc_date}',
        s_meta,
    )
    doc_label = f'{doc_type_label} {doc_number}'.strip()

    col_widths = [2.2 * cm, 12.5 * cm, 3.3 * cm]

    data = [
        [logo_cell,           title_cell,                              meta_cell],
        ['',                  Paragraph(SCHOOL_AREA,  s_area),         ''],
        ['',                  Paragraph(SCHOOL_PROC,  s_area),         ''],
        ['',                  Paragraph(doc_label,    s_doc),          ''],
    ]

    style = TableStyle([
        # Global
        ('GRID',        (0, 0), (-1, -1), 0.5, BLACK),
        ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),

        # Logo cell spans all 4 rows
        ('SPAN',        (0, 0), (0, 3)),

        # Meta cell spans rows 0-2
        ('SPAN',        (2, 0), (2, 2)),

        # Green background for title row
        ('BACKGROUND',  (1, 0), (1, 0), GREEN_DARK),
        ('BACKGROUND',  (0, 0), (0, 3), LIGHT_GRAY),

        # Row heights
        ('ROWBACKGROUNDS', (1, 1), (1, 3), [WHITE]),
        ('TOPPADDING',  (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),

        # Bold border on outer frame
        ('BOX',         (0, 0), (-1, -1), 1, BLACK),
    ])

    table = Table(data, colWidths=col_widths, rowHeights=[1.2 * cm, 0.65 * cm, 0.65 * cm, 0.65 * cm])
    table.setStyle(style)
    return table


def generate_document_pdf(document):
    """
    Generates a PDF for the given GeneratedDocument instance.
    Returns bytes of the PDF.
    """
    buffer = io.BytesIO()
    today  = date.today()
    doc_date = today.strftime('%d/%m/%Y')

    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        leftMargin=2.5 * cm,
        rightMargin=2.0 * cm,
        topMargin=1.5 * cm,
        bottomMargin=2.0 * cm,
        title=document.title,
        author=document.teacher.get_full_name() or document.teacher.username,
    )

    styles = getSampleStyleSheet()

    s_body = ParagraphStyle(
        'body',
        fontName='Helvetica',
        fontSize=10,
        leading=16,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    )
    s_bold = ParagraphStyle(
        'bold',
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        spaceAfter=4,
    )
    s_center = ParagraphStyle(
        'center',
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    s_right = ParagraphStyle(
        'right',
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        alignment=TA_RIGHT,
        spaceAfter=4,
    )
    s_signature = ParagraphStyle(
        'signature',
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        alignment=TA_CENTER,
    )
    s_small = ParagraphStyle(
        'small',
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#555555'),
    )

    teacher_name = document.teacher.get_full_name() or document.teacher.username

    elements = []

    # --- Header ---
    header = _build_header_table(
        doc_type_label=document.get_doc_type_display(),
        doc_number=document.doc_number,
        page_number=1,
        total_pages=1,
        doc_date=doc_date,
    )
    elements.append(header)
    elements.append(Spacer(1, 0.6 * cm))

    # --- Date & city ---
    elements.append(Paragraph(
        f'{SCHOOL_CITY}, {today.strftime("%d de %B de %Y")}',
        s_right,
    ))
    elements.append(Spacer(1, 0.3 * cm))

    # --- Recipient ---
    if document.recipient:
        elements.append(Paragraph(f'Señor(a) / Señores:', s_bold))
        elements.append(Paragraph(document.recipient, s_body))
        elements.append(Spacer(1, 0.3 * cm))

    # --- Subject line ---
    elements.append(Paragraph(
        f'<b>Asunto:</b> {document.title}',
        s_body,
    ))
    elements.append(Spacer(1, 0.5 * cm))

    # --- Body content (split by newlines to preserve paragraphs) ---
    for line in document.content.split('\n'):
        stripped = line.strip()
        if stripped:
            elements.append(Paragraph(stripped, s_body))
        else:
            elements.append(Spacer(1, 0.3 * cm))

    elements.append(Spacer(1, 1.2 * cm))

    # --- Signature block ---
    elements.append(Paragraph('Atentamente,', s_body))
    elements.append(Spacer(1, 0.4 * cm))

    sig_img = _signature_image(height=2.2 * cm)
    if sig_img:
        sig_img.hAlign = 'CENTER'
        elements.append(sig_img)
    else:
        elements.append(Spacer(1, 1.5 * cm))

    sig_line = '_' * 35
    elements.append(Paragraph(sig_line, s_center))
    elements.append(Paragraph(f'<b>{teacher_name}</b>', s_signature))
    elements.append(Paragraph('Docente', s_small))
    elements.append(Paragraph(SCHOOL_NAME, s_small))

    doc.build(elements)
    return buffer.getvalue()
