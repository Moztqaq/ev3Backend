from django.core.management.base import BaseCommand

from gestion_clinica.models import Veterinario


VETERINARIOS_DEMO = (
    {
        'nombre': 'Nicolás',
        'apellido': 'Herrera',
        'rut': 'RUT-DEMO-001',
        'licencia_medica': 'LIC-DEMO-001',
        'especialidad': 'Medicina general',
    },
    {
        'nombre': 'Matías',
        'apellido': 'Fuentes',
        'rut': 'RUT-DEMO-002',
        'licencia_medica': 'LIC-DEMO-002',
        'especialidad': 'Cirugía veterinaria',
    },
    {
        'nombre': 'Sebastián',
        'apellido': 'Rojas',
        'rut': 'RUT-DEMO-003',
        'licencia_medica': 'LIC-DEMO-003',
        'especialidad': 'Medicina interna',
    },
    {
        'nombre': 'Camila',
        'apellido': 'Soto',
        'rut': 'RUT-DEMO-004',
        'licencia_medica': 'LIC-DEMO-004',
        'especialidad': 'Dermatología veterinaria',
    },
    {
        'nombre': 'Valentina',
        'apellido': 'Muñoz',
        'rut': 'RUT-DEMO-005',
        'licencia_medica': 'LIC-DEMO-005',
        'especialidad': 'Medicina felina',
    },
)


class Command(BaseCommand):
    help = 'Crea perfiles ficticios de demostración para veterinarios.'

    def handle(self, *args, **options):
        creados = 0
        existentes = 0
        for datos in VETERINARIOS_DEMO:
            _, creado = Veterinario.objects.get_or_create(
                rut=datos['rut'],
                defaults=datos,
            )
            if creado:
                creados += 1
            else:
                existentes += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Perfiles demo creados: {creados}; ya existentes: {existentes}. '
                'RUT y licencias son identificadores ficticios.'
            )
        )
