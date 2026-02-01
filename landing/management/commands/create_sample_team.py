from django.core.management.base import BaseCommand
from landing.models import TeamMember


class Command(BaseCommand):
    help = 'Crea miembros del equipo de ejemplo para testing'

    def handle(self, *args, **kwargs):
        # Datos de ejemplo
        sample_members = [
            {
                'nombre': 'María García',
                'puesto': 'duena',
                'cv_info': 'Fundadora de PatosGym. Más de 15 años de experiencia en fitness y gestión deportiva. Campeona nacional de powerlifting 2019.',
                'orden': 1
            },
            {
                'nombre': 'Carlos Rodríguez',
                'puesto': 'dueno',
                'cv_info': 'Co-fundador y especialista en nutrición deportiva. Certificado ISSA. Ha trabajado con atletas de alto rendimiento.',
                'orden': 2
            },
            {
                'nombre': 'Laura Martínez',
                'puesto': 'profesora_musculacion',
                'puesto_secundario': 'personal_trainer',
                'cv_info': 'Personal Trainer certificada con especialización en rehabilitación post-lesión. 8 años de experiencia.',
                'orden': 3
            },
            {
                'nombre': 'Diego Fernández',
                'puesto': 'profesor_musculacion',
                'cv_info': 'Profesor de musculación con énfasis en hipertrofia y fuerza. Ex-competidor de bodybuilding.',
                'orden': 4
            },
            {
                'nombre': 'Ana López',
                'puesto': 'personal_trainer',
                'cv_info': 'Especialista en entrenamiento funcional y CrossFit. Certificación internacional CrossFit Level 2.',
                'orden': 5
            },
            {
                'nombre': 'Javier Sánchez',
                'puesto': 'profesor_musculacion',
                'cv_info': 'Instructor de musculación enfocado en principiantes. Graduado en Educación Física.',
                'orden': 6
            },
            {
                'nombre': 'Sofía Torres',
                'puesto': 'profesora_musculacion',
                'puesto_secundario': 'personal_trainer',
                'cv_info': 'Entrenadora personal especializada en pérdida de peso y tonificación femenina. 5 años de experiencia.',
                'orden': 7
            },
            {
                'nombre': 'Miguel Ángel Ruiz',
                'puesto': 'personal_trainer',
                'cv_info': 'PT con especialización en atletas master (+40 años). Certificado en programación deportiva.',
                'orden': 8
            },
        ]

        created_count = 0
        for member_data in sample_members:
            # Verificar si ya existe para no duplicar
            if not TeamMember.objects.filter(nombre=member_data['nombre']).exists():
                TeamMember.objects.create(**member_data)
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Creado: {member_data["nombre"]}'))
            else:
                self.stdout.write(self.style.WARNING(f'- Ya existe: {member_data["nombre"]}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Total creados: {created_count} miembros'))
        self.stdout.write(self.style.SUCCESS(f'📊 Total en DB: {TeamMember.objects.count()} miembros'))
