from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import StudentProfile
from apps.classroom.models import Course

User = get_user_model()

STUDENTS = [
    # (apellido1, apellido2, nombre1, nombre2_or_None, birth_date)
    ("Orjuela",    "Segura",    "Samara",    None,        "2020-01-22"),
    ("Jaramillo",  "Rivas",     "Victoria",  None,        "2020-01-26"),
    ("Castaño",    "Hermida",   "Miguel",    "Angel",     "2020-02-16"),
    ("Arroyave",   "Londoño",   "Jacobo",    None,        "2020-03-11"),
    ("Valverde",   "Aguirre",   "Joaquin",   None,        "2020-03-20"),
    ("Gonzalez",   "Marquez",   "Travis",    None,        "2020-04-17"),
    ("Sanchez",    "Osorio",    "Simon",     None,        "2020-04-20"),
    ("Guerrero",   "Jimenez",   "Manuel",    "Alejandro", "2020-04-21"),
    ("Cardona",    "Contecha",  "David",     None,        "2020-04-24"),
    ("Vargas",     "Machado",   "Martina",   None,        "2020-04-28"),
    ("Lopez",      "Martinez",  "Santiago",  None,        "2020-05-19"),
    ("Gomez",      "Gomez",     "Any",       "Valentina", "2020-07-14"),
    ("Buritica",   "Giraldo",   "Angel",     "Steven",    "2020-07-22"),
    ("Gomez",      "Zuñiga",    "Maria",     "Salome",    "2020-07-27"),
    ("Hernandez",  "Zuñiga",    "Rafael",    None,        "2020-07-30"),
    ("Isaza",      "Espinosa",  "Ainhoa",    None,        "2020-08-19"),
    ("Martinez",   "Gaviria",   "Joel",      None,        "2020-09-01"),
    ("Marinez",    "Valencia",  "Alan",      "Joaquin",   "2020-09-10"),
    ("Cardenas",   "Rubio",     "Isabella",  None,        "2020-09-15"),
    ("Ayala",      "Posada",    "Emiliano",  None,        "2020-11-14"),
    ("Guaca",      "Hernandez", "Liam",      "David",     "2020-11-19"),
    ("Olaya",      "Narvaez",   "Gael",      None,        "2020-12-27"),
    ("Pajoy",      "Zambrano",  "Sara",      "Sofia",     "2020-09-11"),
]


class Command(BaseCommand):
    help = "Registra los 23 estudiantes de Transición A en la base de datos"

    def handle(self, *args, **options):
        # Buscar o crear el curso Transición A (requiere un docente existente)
        teacher = User.objects.filter(role='teacher').first()
        if not teacher:
            self.stderr.write("No hay ningún docente en la BD. Crea un docente primero.")
            return

        course, created = Course.objects.get_or_create(
            name="Transición A",
            defaults={"teacher": teacher, "description": "Grupo Transición A", "is_active": True},
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Curso 'Transición A' creado."))
        else:
            self.stdout.write(f"Curso existente: {course}")

        created_count = 0
        skipped_count = 0

        for apellido1, apellido2, nombre1, nombre2, birth in STUDENTS:
            username = f"{nombre1.lower()}_{apellido1.lower()}"
            # Normalizar caracteres especiales en el username
            username = username.replace("ñ", "n").replace("ó", "o").replace("é", "e")

            full_first = f"{nombre1} {nombre2}".strip() if nombre2 else nombre1
            full_last  = f"{apellido1} {apellido2}".strip()
            password   = f"{nombre1.lower()}123"

            if User.objects.filter(username=username).exists():
                self.stdout.write(f"  [OMITIDO] {username} ya existe.")
                skipped_count += 1
                continue

            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=full_first,
                last_name=full_last,
                role="student",
            )

            StudentProfile.objects.create(
                user=user,
                level="A",
                age=5,
                parent_name="",
                parent_email="sin-correo@artekids.edu",
            )

            course.students.add(user)
            self.stdout.write(
                self.style.SUCCESS(f"  [OK] {username} / {password}  — {full_first} {full_last}")
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nListo: {created_count} creados, {skipped_count} omitidos."
            )
        )
