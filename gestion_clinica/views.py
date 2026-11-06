from datetime import timedelta

from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .forms import CitaForm, MascotaForm
from .models import Cita, FichaMedica, Mascota, Tutor, VacunaControl, Veterinario
from .serializers import (
    CitaSerializer,
    FichaMedicaSerializer,
    MascotaSerializer,
    TutorSerializer,
    VacunaControlSerializer,
    VeterinarioSerializer,
)


def dashboard(request):
    hoy = timezone.localdate()
    limite_alerta = hoy + timedelta(days=7)
    citas_hoy = Cita.objects.filter(fecha=hoy).select_related(
        'mascota',
        'veterinario',
    ).order_by('hora_inicio')
    alertas = VacunaControl.objects.filter(
        fecha_proximo_control__lte=limite_alerta,
    ).select_related('mascota').order_by('fecha_proximo_control')
    return render(request, 'dashboard.html', {
        'hoy': hoy,
        'citas_hoy': citas_hoy,
        'alertas': alertas,
    })


def nueva_cita(request):
    form = CitaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'La cita médica se registró correctamente.')
        return redirect('citas')
    return render(request, 'gestion_clinica/formulario.html', {
        'form': form,
        'titulo': 'Registrar cita médica',
        'volver_url': 'citas',
    })


def nueva_mascota(request):
    form = MascotaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'La mascota se registró correctamente.')
        return redirect('mascotas')
    return render(request, 'gestion_clinica/formulario.html', {
        'form': form,
        'titulo': 'Registrar mascota',
        'volver_url': 'mascotas',
    })


def registros(request, entidad):
    configuraciones = {
        'tutores': (
            'Tutores',
            Tutor.objects.order_by('apellido', 'nombre'),
            ('nombre', 'apellido', 'rut', 'telefono', 'correo'),
        ),
        'mascotas': (
            'Mascotas',
            Mascota.objects.select_related('tutor').order_by('nombre'),
            ('nombre', 'get_especie_display', 'raza', 'sexo', 'tutor'),
        ),
        'citas': (
            'Citas',
            Cita.objects.select_related('mascota', 'veterinario').order_by('-fecha', 'hora_inicio'),
            ('fecha', 'hora_inicio', 'hora_fin', 'mascota', 'veterinario', 'get_estado_display'),
        ),
        'fichas': (
            'Fichas Médicas',
            FichaMedica.objects.select_related('mascota', 'veterinario').order_by('-fecha_atencion'),
            ('fecha_atencion', 'mascota', 'veterinario', 'diagnostico'),
        ),
        'recordatorios': (
            'Recordatorios',
            VacunaControl.objects.select_related('mascota').order_by('fecha_proximo_control'),
            ('mascota', 'get_tipo_display', 'nombre_procedimiento', 'fecha_aplicacion', 'fecha_proximo_control'),
        ),
    }
    titulo, objetos, campos = configuraciones[entidad]
    encabezados = [campo.replace('_', ' ').title() for campo in campos]
    filas = [
        [
            str(valor() if callable(valor) else valor)
            for valor in (getattr(objeto, campo) for campo in campos)
        ]
        for objeto in objetos
    ]
    return render(request, 'gestion_clinica/listado.html', {
        'titulo': titulo,
        'encabezados': encabezados,
        'filas': filas,
        'entidad': entidad,
    })


class TutorViewSet(viewsets.ModelViewSet):
    queryset = Tutor.objects.all()
    serializer_class = TutorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class MascotaViewSet(viewsets.ModelViewSet):
    queryset = Mascota.objects.all()
    serializer_class = MascotaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class VeterinarioViewSet(viewsets.ModelViewSet):
    queryset = Veterinario.objects.all()
    serializer_class = VeterinarioSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CitaViewSet(viewsets.ModelViewSet):
    queryset = Cita.objects.all()
    serializer_class = CitaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class FichaMedicaViewSet(viewsets.ModelViewSet):
    queryset = FichaMedica.objects.all()
    serializer_class = FichaMedicaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class VacunaControlViewSet(viewsets.ModelViewSet):
    queryset = VacunaControl.objects.all()
    serializer_class = VacunaControlSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['get'])
    def alertas_pendientes(self, request):
        hoy = timezone.localdate()
        limite = hoy + timedelta(days=7)
        alertas = self.get_queryset().filter(
            fecha_proximo_control__range=(hoy, limite),
        ).order_by('fecha_proximo_control')
        serializer = self.get_serializer(alertas, many=True)
        return Response(serializer.data)
