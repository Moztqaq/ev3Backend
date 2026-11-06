from datetime import date, time, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from .models import Cita, Mascota, Tutor, VacunaControl, Veterinario
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

    def test_navigation_list_pages_render(self):
        for route_name in ('tutores', 'mascotas', 'citas', 'fichas', 'recordatorios'):
            with self.subTest(route=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, 'gestion_clinica/listado.html')
