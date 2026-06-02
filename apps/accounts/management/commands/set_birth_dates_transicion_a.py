from datetime import date
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

STUDENTS = [
    ('samara_orjuela',    date(2020, 1, 22)),
    ('victoria_jaramillo', date(2020, 1, 26)),
    ('miguel_castano',    date(2020, 2, 16)),
    ('jacobo_arroyave',   date(2020, 3, 11)),
    ('joaquin_valverde',  date(2020, 3, 20)),
    ('travis_gonzalez',   date(2020, 4, 17)),
    ('simon_sanchez',     date(2020, 4, 20)),
    ('manuel_guerrero',   date(2020, 4, 21)),
    ('david_cardona',     date(2020, 4, 24)),
    ('martina_vargas',    date(2020, 4, 28)),
    ('santiago_lopez',    date(2020, 5, 19)),
    ('any_gomez',         date(2020, 7, 14)),
    ('angel_buritica',    date(2020, 7, 22)),
    ('maria_gomez',       date(2020, 7, 27)),
    ('rafael_hernandez',  date(2020, 7, 30)),
    ('ainhoa_isaza',      date(2020, 8, 19)),
    ('joel_martinez',     date(2020, 9,  1)),
    ('alan_marinez',      date(2020, 9, 10)),
    ('isabella_cardenas', date(2020, 9, 15)),
    ('emiliano_ayala',    date(2020, 11, 14)),
    ('liam_guaca',        date(2020, 11, 19)),
    ('gael_olaya',        date(2020, 12, 27)),
    ('sara_pajoy',        date(2020, 9, 11)),
]


class Command(BaseCommand):
    help = 'Asigna fechas de nacimiento a los estudiantes de Transición A'

    def handle(self, *args, **options):
        updated = 0
        not_found = []

        for username, birth_date in STUDENTS:
            try:
                user = User.objects.get(username=username)
                profile = user.student_profile
                profile.birth_date = birth_date
                profile.save(update_fields=['birth_date'])
                self.stdout.write(f'  OK  {username} -> {birth_date}')
                updated += 1
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  --  {username}: usuario no encontrado'))
                not_found.append(username)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  !!  {username}: {e}'))
                not_found.append(username)

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Actualizados: {updated}/{len(STUDENTS)}'))
        if not_found:
            self.stdout.write(self.style.WARNING(f'No encontrados: {", ".join(not_found)}'))
