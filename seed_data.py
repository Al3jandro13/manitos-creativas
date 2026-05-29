"""
Manitos Creativas — Seed initial data
Run: python seed_data.py
"""
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manitos_creativas.settings')
django.setup()

from apps.activities.models import ActivityCategory
from apps.games.models import Game
from apps.accounts.models import CustomUser, TeacherProfile, StudentProfile

# ── Activity Categories ──
CATEGORIES = [
    ('colorear',       '🎨', '#EC4899'),
    ('puntillismo',    '🔵', '#3B82F6'),
    ('rompecabezas',   '🧩', '#7C3AED'),
    ('cuento',         '📖', '#F97316'),
    ('dibujo_libre',   '✏️', '#10B981'),
    ('consonantes',    '🔤', '#FBBF24'),
    ('numeros',        '🔢', '#EF4444'),
    ('sumas',          '➕', '#059669'),
    ('restas',         '➖', '#DC2626'),
    ('lenguaje_senas', '🤟', '#8B5CF6'),
    ('exploracion',    '🔬', '#0891B2'),
    ('actividad_libre','🌟', '#D97706'),
]

created = 0
for name, icon, color in CATEGORIES:
    obj, was_created = ActivityCategory.objects.get_or_create(
        name=name,
        defaults={'icon': icon, 'color': color}
    )
    if was_created:
        created += 1
print(f'Categorías: {created} creadas, {len(CATEGORIES) - created} ya existían.')

# ── Games ──
GAMES = [
    ('puzzle',    'Rompecabezas',         '🧩', 5,  'Ordena las piezas para completar la imagen'),
    ('drawing',   'Dibujo Libre',          '✏️', 3,  'Dibuja libremente con los colores que quieras'),
    ('numbers',   'Números 1-100',         '🔢', 4,  'Explora los números del 1 al 100'),
    ('consonants','Consonantes',            '🔤', 4,  'Aprende las consonantes del alfabeto'),
    ('math_add',  'Sumas',                 '➕', 5,  'Practica sumas divertidas'),
    ('math_sub',  'Restas',                '➖', 5,  'Practica restas divertidas'),
    ('signs',     'Lenguaje de Señas',     '🤟', 6,  'Aprende señas básicas en LSC'),
    ('story',     'Cuento Interactivo',    '📖', 4,  'Toma decisiones en un cuento mágico'),
    ('snake',      'Serpiente',             '🐍', 5,  'Come manzanas y crece sin chocarte'),
    ('wordsearch', 'Sopa de Letras',        '🔠', 5,  'Encuentra las palabras escondidas en la sopa de letras'),
]

gcreated = 0
for gtype, name, icon, stars, desc in GAMES:
    obj, was_created = Game.objects.get_or_create(
        game_type=gtype,
        defaults={'name': name, 'stars_reward': stars,
                  'description': desc, 'is_active': True}
    )
    if was_created:
        gcreated += 1
print(f'Juegos: {gcreated} creados, {len(GAMES) - gcreated} ya existían.')
print('✅ Datos iniciales cargados correctamente.')

# ── Profesora Karen ──
teacher, t_created = CustomUser.objects.get_or_create(
    username='karen',
    defaults={
        'first_name': 'Karen Johana',
        'last_name': 'Ramirez Papamija',
        'role': 'teacher',
        'email': 'karen@manitos.edu',
    }
)
if t_created:
    teacher.set_password('karen1234')
    teacher.save()
    TeacherProfile.objects.get_or_create(user=teacher)
    print('👩‍🏫 Profesora Karen creada.')
else:
    print('👩‍🏫 Profesora Karen ya existía.')

# ── Estudiante Gabriella Carrillo ──
student, s_created = CustomUser.objects.get_or_create(
    username='gabriela.carrillo',
    defaults={
        'first_name': 'Gabriela',
        'last_name': 'Carrillo',
        'role': 'student',
        'email': 'gabriella@manitos.edu',
    }
)
if s_created:
    student.set_password('gabriella1234')
    student.save()
    StudentProfile.objects.get_or_create(user=student)
    print('🎒 Estudiante Gabriela Carrillo creada.')
else:
    print('🎒 Estudiante Gabriela Carrillo ya existía.')
