from datetime import date, time, timedelta
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from .models import Cita, FichaMedica, Mascota, Tutor, VacunaControl, Veterinario
from .serializers import CitaSerializer


class CitaSerializerTests(TestCase):
    def setUp(self):
        tutor = Tutor.objects.create(
            nombre='Ana',
            apellido='Pérez',
            rut='11111111-1',
            telefono='123456789',
            correo='ana@example.com',
            direccion='Calle 1',
        )
        self.mascota = Mascota.objects.create(
            tutor=tutor,
            nombre='Luna',
            especie=Mascota.Especie.CANINO,
            raza='Mestiza',
            sexo=Mascota.Sexo.HEMBRA,
            fecha_nacimiento=date(2020, 1, 1),
            peso_kg='10.00',
        )
        self.veterinario = Veterinario.objects.create(
            nombre='Luis',
            apellido='Gómez',
            rut='22222222-2',
            licencia_medica='LIC-001',
            especialidad='General',
        )
        self.fecha = date(2026, 11, 6)
        Cita.objects.create(
            mascota=self.mascota,
            veterinario=self.veterinario,
            fecha=self.fecha,
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            motivo='Control',
        )

    def test_rejects_overlapping_appointment(self):
        serializer = CitaSerializer(data={
            'mascota': self.mascota.pk,
            'veterinario': self.veterinario.pk,
            'fecha': self.fecha,
            'hora_inicio': '09:30',
            'hora_fin': '10:30',
            'motivo': 'Consulta',
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('hora_inicio', serializer.errors)

    def test_allows_appointment_starting_when_another_ends(self):
        serializer = CitaSerializer(data={
            'mascota': self.mascota.pk,
            'veterinario': self.veterinario.pk,
            'fecha': self.fecha,
            'hora_inicio': '10:00',
            'hora_fin': '10:30',
            'motivo': 'Consulta',
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_rejects_end_time_not_after_start_time(self):
        serializer = CitaSerializer(data={
            'mascota': self.mascota.pk,
            'veterinario': self.veterinario.pk,
            'fecha': self.fecha,
            'hora_inicio': '10:30',
            'hora_fin': '10:00',
            'motivo': 'Consulta',
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('hora_fin', serializer.errors)


class AlertasPendientesTests(TestCase):
    def setUp(self):
        tutor = Tutor.objects.create(
            nombre='Ana',
            apellido='Pérez',
            rut='33333333-3',
            telefono='123456789',
            correo='ana@example.com',
            direccion='Calle 1',
        )
        self.mascota = Mascota.objects.create(
            tutor=tutor,
            nombre='Luna',
            especie=Mascota.Especie.CANINO,
            raza='Mestiza',
            sexo=Mascota.Sexo.HEMBRA,
            fecha_nacimiento=date(2020, 1, 1),
            peso_kg='10.00',
        )
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            username='clinic-admin',
            email='admin@example.com',
            password='Test-password-123!',
        )
        self.client.force_authenticate(self.user)

    def test_returns_controls_due_today_through_seven_days(self):
        hoy = timezone.localdate()
        fechas = [hoy - timedelta(days=1), hoy, hoy + timedelta(days=7), hoy + timedelta(days=8)]
        for indice, fecha in enumerate(fechas):
            VacunaControl.objects.create(
                mascota=self.mascota,
                tipo=VacunaControl.Tipo.CONTROL,
                nombre_procedimiento=f'Control {indice}',
                fecha_aplicacion=hoy,
                fecha_proximo_control=fecha,
            )

        response = self.client.get(reverse('vacunacontrol-alertas-pendientes'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {item['nombre_procedimiento'] for item in response.data},
            {'Control 1', 'Control 2'},
        )

    def test_api_does_not_expose_reminders_to_anonymous_visitors(self):
        response = APIClient().get(reverse('vacunacontrol-alertas-pendientes'))

        self.assertEqual(response.status_code, 403)


class PetCareTemplateViewsTests(TestCase):
    def setUp(self):
        self.tutor = Tutor.objects.create(
            nombre='Ana',
            apellido='Pérez',
            rut='44444444-4',
            telefono='123456789',
            correo='ana@example.com',
            direccion='Calle 1',
        )
        self.mascota = Mascota.objects.create(
            tutor=self.tutor,
            nombre='Luna',
            especie=Mascota.Especie.CANINO,
            raza='Mestiza',
            sexo=Mascota.Sexo.HEMBRA,
            fecha_nacimiento=date(2020, 1, 1),
            peso_kg='10.00',
        )
        self.veterinario = Veterinario.objects.create(
            nombre='Luis',
            apellido='Gómez',
            rut='55555555-5',
            licencia_medica='LIC-002',
            especialidad='General',
        )
        self.staff = get_user_model().objects.create_superuser(
            username='clinic-staff',
            email='staff@example.com',
            password='Test-password-123!',
        )
        self.client.force_login(self.staff)

    def test_dashboard_renders_daily_appointments_and_alerts(self):
        hoy = timezone.localdate()
        Cita.objects.create(
            mascota=self.mascota,
            veterinario=self.veterinario,
            fecha=hoy,
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
            motivo='Control anual',
        )
        VacunaControl.objects.create(
            mascota=self.mascota,
            tipo=VacunaControl.Tipo.VACUNA,
            nombre_procedimiento='Refuerzo',
            fecha_aplicacion=hoy,
            fecha_proximo_control=hoy - timedelta(days=1),
        )

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertContains(response, 'Citas del día')
        self.assertContains(response, 'Control anual')
        self.assertContains(response, 'Vencido')
        self.assertEqual(len(response.context['alertas']), 1)

    def test_registration_pages_create_mascota_and_cita(self):
        mascota_response = self.client.post(reverse('nueva_mascota'), {
            'tutor': self.tutor.pk,
            'nombre': 'Nube',
            'especie': Mascota.Especie.FELINO,
            'raza': 'Doméstico',
            'sexo': Mascota.Sexo.MACHO,
            'fecha_nacimiento': '2022-03-04',
            'peso_kg': '4.50',
        })
        self.assertRedirects(mascota_response, reverse('mascotas'))
        self.assertTrue(Mascota.objects.filter(nombre='Nube').exists())

        cita_response = self.client.post(reverse('nueva_cita'), {
            'mascota': self.mascota.pk,
            'veterinario': self.veterinario.pk,
            'fecha': '2026-11-07',
            'hora_inicio': '11:00',
            'hora_fin': '11:30',
            'motivo': 'Vacunación',
            'estado': Cita.Estado.PENDIENTE,
        })
        self.assertRedirects(cita_response, reverse('citas'))
        self.assertTrue(Cita.objects.filter(motivo='Vacunación').exists())

    def test_staff_can_register_and_edit_veterinarians(self):
        response = self.client.post(reverse('registro_nuevo', args=['veterinarios']), {
            'nombre': 'Daniela',
            'apellido': 'Pérez',
            'rut': '12345678-9',
            'licencia_medica': 'LIC-CLINIC-01',
            'especialidad': 'Medicina general',
        })

        self.assertRedirects(response, reverse('veterinarios'))
        veterinario = Veterinario.objects.get(rut='12345678-9')
        self.assertEqual(veterinario.nombre, 'Daniela')
        self.assertContains(self.client.get(reverse('veterinarios')), 'Daniela')

        response = self.client.post(
            reverse('registro_editar', args=['veterinarios', veterinario.pk]),
            {
                'nombre': 'Daniela',
                'apellido': 'Pérez',
                'rut': '12345678-9',
                'licencia_medica': 'LIC-CLINIC-01',
                'especialidad': 'Cirugía veterinaria',
            },
        )
        self.assertRedirects(response, reverse('veterinarios'))
        veterinario.refresh_from_db()
        self.assertEqual(veterinario.especialidad, 'Cirugía veterinaria')

    def test_demo_veterinarian_command_creates_five_profiles_idempotently(self):
        output = StringIO()

        call_command('seed_demo_veterinarios', stdout=output)
        call_command('seed_demo_veterinarios', stdout=output)

        self.assertEqual(Veterinario.objects.count(), 6)
        self.assertEqual(
            set(Veterinario.objects.exclude(pk=self.veterinario.pk).values_list('nombre', flat=True)),
            {'Nicolás', 'Matías', 'Sebastián', 'Camila', 'Valentina'},
        )
        self.assertIn('Perfiles demo creados: 0; ya existentes: 5.', output.getvalue())

    def test_navigation_list_pages_render(self):
        for route_name in (
            'tutores',
            'veterinarios',
            'mascotas',
            'citas',
            'fichas',
            'recordatorios',
        ):
            with self.subTest(route=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, 'gestion_clinica/listado.html')
        veterinarios = self.client.get(reverse('veterinarios'))
        self.assertContains(veterinarios, 'Especialidad')
        self.assertContains(veterinarios, 'Nuevo registro')
        reminders = self.client.get(reverse('recordatorios'))
        self.assertContains(reminders, 'Tipo')
        self.assertContains(reminders, 'Fecha de aplicación')
        self.assertContains(reminders, 'Próximo control')
        self.assertNotContains(reminders, 'Get Tipo Display')

    def test_anonymous_users_are_redirected_from_clinical_data(self):
        response = self.client_class().get(reverse('dashboard'))

        self.assertRedirects(response, f'{reverse("login")}?next={reverse("dashboard")}')

    def test_staff_visiting_login_is_sent_to_the_dashboard(self):
        response = self.client.get(reverse('login'))

        self.assertRedirects(response, reverse('dashboard'))

    def test_tutor_portal_only_shows_the_linked_tutors_pets(self):
        tutor_user = get_user_model().objects.create_user(
            username='tutor-ana',
            password='Test-password-123!',
        )
        self.tutor.usuario = tutor_user
        self.tutor.save(update_fields=['usuario'])
        self.client.force_login(tutor_user)

        response = self.client.get(reverse('portal_tutor'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.mascota.nombre)
        self.assertEqual(response.context['mascotas'].count(), 1)

        private_pet = self.client.get(reverse('detalle_mascota', args=[self.mascota.pk]))
        self.assertEqual(private_pet.status_code, 200)

    def test_tutor_cannot_open_another_tutors_pet(self):
        tutor_user = get_user_model().objects.create_user(
            username='tutor-otra',
            password='Test-password-123!',
        )
        self.client.force_login(tutor_user)

        response = self.client.get(reverse('detalle_mascota', args=[self.mascota.pk]))

        self.assertEqual(response.status_code, 404)

    def test_calendar_and_printable_medical_summary_render(self):
        response = self.client.get(reverse('calendario'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Calendario de citas')

        FichaMedica.objects.create(
            mascota=self.mascota,
            veterinario=self.veterinario,
            fecha_atencion=timezone.now(),
            motivo_consulta='Control anual',
            diagnostico='Buen estado general',
            tratamiento='Control preventivo',
        )
        print_response = self.client.get(
            reverse('imprimir_historial', args=[self.mascota.pk]),
        )
        self.assertEqual(print_response.status_code, 200)
        self.assertContains(print_response, 'Guardar como PDF')
        self.assertContains(print_response, 'Buen estado general')

    def test_staff_can_search_and_edit_records(self):
        response = self.client.get(reverse('mascotas'), {'q': self.mascota.nombre})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.mascota.nombre)

        response = self.client.post(
            reverse('registro_editar', args=['mascotas', self.mascota.pk]),
            {
                'tutor': self.tutor.pk,
                'nombre': 'Luna actualizada',
                'especie': Mascota.Especie.CANINO,
                'raza': 'Mestiza',
                'sexo': Mascota.Sexo.HEMBRA,
                'fecha_nacimiento': '2020-01-01',
                'peso_kg': '11.00',
            },
        )
        self.assertRedirects(response, reverse('mascotas'))
        self.mascota.refresh_from_db()
        self.assertEqual(self.mascota.nombre, 'Luna actualizada')

    @override_settings(EMAIL_CONFIGURED=False)
    def test_reminder_email_is_not_sent_without_smtp_configuration(self):
        recordatorio = VacunaControl.objects.create(
            mascota=self.mascota,
            tipo=VacunaControl.Tipo.CONTROL,
            nombre_procedimiento='Control anual',
            fecha_aplicacion=timezone.localdate(),
            fecha_proximo_control=timezone.localdate() + timedelta(days=7),
        )

        response = self.client.post(
            reverse('enviar_recordatorio', args=[recordatorio.pk]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No se envió el correo')
