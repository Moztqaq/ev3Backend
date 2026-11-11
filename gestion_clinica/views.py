import calendar
import logging
import smtplib
from datetime import date, datetime, timedelta
from functools import wraps

from django.conf import settings
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .forms import (
    CitaForm,
    FichaMedicaForm,
    MascotaForm,
    TutorForm,
    VacunaControlForm,
    VeterinarioForm,
)
from .models import Cita, FichaMedica, Mascota, Tutor, VacunaControl, Veterinario
from .serializers import (
    CitaSerializer,
    FichaMedicaSerializer,
    MascotaSerializer,
    TutorSerializer,
    VacunaControlSerializer,
    VeterinarioSerializer,
)

logger = logging.getLogger(__name__)

ENTIDADES = {
    'tutores': {
        'titulo': 'Tutores',
        'form_nombre': 'tutor',
        'mensajes': ('El tutor se registró correctamente.', 'El tutor se actualizó correctamente.'),
        'modelo': Tutor,
        'formulario': TutorForm,
        'campos': (
            ('nombre', 'Nombre'),
            ('apellido', 'Apellido'),
            ('rut', 'RUT'),
            ('telefono', 'Teléfono'),
            ('correo', 'Correo electrónico'),
        ),
        'busqueda': ('nombre', 'apellido', 'rut', 'telefono', 'correo'),
    },
    'mascotas': {
        'titulo': 'Mascotas',
        'form_nombre': 'mascota',
        'mensajes': ('La mascota se registró correctamente.', 'La mascota se actualizó correctamente.'),
        'modelo': Mascota,
        'formulario': MascotaForm,
        'campos': (
            ('nombre', 'Nombre'),
            ('get_especie_display', 'Especie'),
            ('raza', 'Raza'),
            ('sexo', 'Sexo'),
            ('tutor', 'Tutor'),
        ),
        'busqueda': ('nombre', 'raza', 'tutor__nombre', 'tutor__apellido', 'tutor__rut'),
    },
    'citas': {
        'titulo': 'Citas',
        'form_nombre': 'cita',
        'mensajes': ('La cita se registró correctamente.', 'La cita se actualizó correctamente.'),
        'modelo': Cita,
        'formulario': CitaForm,
        'campos': (
            ('fecha', 'Fecha'),
            ('hora_inicio', 'Desde'),
            ('hora_fin', 'Hasta'),
            ('mascota', 'Mascota'),
            ('veterinario', 'Veterinario'),
            ('get_estado_display', 'Estado'),
        ),
        'busqueda': (
            'mascota__nombre',
            'mascota__tutor__nombre',
            'mascota__tutor__apellido',
            'veterinario__nombre',
            'veterinario__apellido',
            'motivo',
        ),
    },
    'fichas': {
        'titulo': 'Fichas médicas',
        'form_nombre': 'ficha médica',
        'mensajes': ('La ficha médica se registró correctamente.', 'La ficha médica se actualizó correctamente.'),
        'modelo': FichaMedica,
        'formulario': FichaMedicaForm,
        'campos': (
            ('fecha_atencion', 'Fecha de atención'),
            ('mascota', 'Mascota'),
            ('veterinario', 'Veterinario'),
            ('diagnostico', 'Diagnóstico'),
        ),
        'busqueda': ('mascota__nombre', 'diagnostico', 'motivo_consulta', 'veterinario__apellido'),
    },
    'recordatorios': {
        'titulo': 'Vacunas y controles',
        'form_nombre': 'vacuna o control',
        'mensajes': ('El control se registró correctamente.', 'El control se actualizó correctamente.'),
        'modelo': VacunaControl,
        'formulario': VacunaControlForm,
        'campos': (
            ('mascota', 'Mascota'),
            ('get_tipo_display', 'Tipo'),
            ('nombre_procedimiento', 'Procedimiento'),
            ('fecha_aplicacion', 'Fecha de aplicación'),
            ('fecha_proximo_control', 'Próximo control'),
        ),
        'busqueda': ('mascota__nombre', 'mascota__tutor__apellido', 'nombre_procedimiento'),
    },
    'veterinarios': {
        'titulo': 'Veterinarios',
        'form_nombre': 'veterinario',
        'mensajes': (
            'El veterinario se registró correctamente.',
            'El veterinario se actualizó correctamente.',
        ),
        'modelo': Veterinario,
        'formulario': VeterinarioForm,
        'campos': (
            ('nombre', 'Nombre'),
            ('apellido', 'Apellido'),
            ('rut', 'RUT'),
            ('licencia_medica', 'Licencia médica'),
            ('especialidad', 'Especialidad'),
        ),
        'busqueda': ('nombre', 'apellido', 'rut', 'licencia_medica', 'especialidad'),
    },
}


def staff_required(view):
    @wraps(view)
    @login_required
    def wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapped


class PetCareLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse('dashboard')
        if Tutor.objects.filter(usuario=self.request.user).exists():
            return reverse('portal_tutor')
        return reverse('acceso_no_disponible')


@login_required
def acceso_no_disponible(request):
    return render(request, 'registration/acceso_no_disponible.html', status=403)


def _formatear_valor(objeto, campo):
    valor = getattr(objeto, campo)
    if callable(valor):
        valor = valor()
    if valor is None:
        return '—'
    if isinstance(valor, datetime):
        return valor.strftime('%d/%m/%Y %H:%M')
    if isinstance(valor, date):
        return valor.strftime('%d/%m/%Y')
    if hasattr(valor, 'strftime'):
        return valor.strftime('%d/%m/%Y %H:%M') if campo == 'fecha_atencion' else valor.strftime('%H:%M')
    return str(valor)


@staff_required
def dashboard(request):
    hoy = timezone.localdate()
    limite_alerta = hoy + timedelta(days=7)
    citas_hoy = Cita.objects.filter(fecha=hoy).select_related(
        'mascota', 'mascota__tutor', 'veterinario',
    ).order_by('hora_inicio')
    alertas = VacunaControl.objects.filter(
        fecha_proximo_control__lte=limite_alerta,
    ).select_related('mascota').order_by('fecha_proximo_control')
    return render(request, 'dashboard.html', {
        'hoy': hoy,
        'citas_hoy': citas_hoy,
        'alertas': alertas,
        'total_mascotas': Mascota.objects.count(),
        'total_tutores': Tutor.objects.count(),
        'total_citas': Cita.objects.filter(fecha__gte=hoy, estado=Cita.Estado.PENDIENTE).count(),
    })


@staff_required
def registros(request, entidad):
    configuracion = ENTIDADES.get(entidad)
    if configuracion is None:
        raise Http404('La sección solicitada no existe.')

    modelo = configuracion['modelo']
    objetos = modelo.objects.all()
    if entidad == 'tutores':
        objetos = objetos.order_by('apellido', 'nombre')
    elif entidad == 'mascotas':
        objetos = objetos.select_related('tutor').order_by('nombre')
    elif entidad == 'citas':
        objetos = objetos.select_related('mascota', 'veterinario').order_by('-fecha', 'hora_inicio')
    elif entidad == 'fichas':
        objetos = objetos.select_related('mascota', 'veterinario').order_by('-fecha_atencion')
    elif entidad == 'veterinarios':
        objetos = objetos.order_by('apellido', 'nombre')
    else:
        objetos = objetos.select_related('mascota').order_by('fecha_proximo_control')

    busqueda = request.GET.get('q', '').strip()
    if busqueda:
        criterio = Q()
        for campo in configuracion['busqueda']:
            criterio |= Q(**{f'{campo}__icontains': busqueda})
        objetos = objetos.filter(criterio)

    estado = request.GET.get('estado', '').strip()
    if entidad == 'citas' and estado in Cita.Estado.values:
        objetos = objetos.filter(estado=estado)
    especie = request.GET.get('especie', '').strip()
    if entidad == 'mascotas' and especie in Mascota.Especie.values:
        objetos = objetos.filter(especie=especie)

    paginador = Paginator(objetos, 20)
    pagina = paginador.get_page(request.GET.get('page'))
    filas = []
    for objeto in pagina.object_list:
        filas.append({
            'id': objeto.pk,
            'celdas': [
                _formatear_valor(objeto, campo)
                for campo, _ in configuracion['campos']
            ],
            'mascota_url': (
                redirect('detalle_mascota', pk=objeto.pk).url
                if entidad == 'mascotas' else None
            ),
        })

    return render(request, 'gestion_clinica/listado.html', {
        'titulo': configuracion['titulo'],
        'columnas': [etiqueta for _, etiqueta in configuracion['campos']],
        'filas': filas,
        'entidad': entidad,
        'busqueda': busqueda,
        'pagina': pagina,
        'estados': Cita.Estado.choices if entidad == 'citas' else (),
        'estado_seleccionado': estado,
        'especies': Mascota.Especie.choices if entidad == 'mascotas' else (),
        'especie_seleccionada': especie,
    })


@staff_required
def editar_registro(request, entidad, pk=None):
    configuracion = ENTIDADES.get(entidad)
    if configuracion is None:
        raise Http404('La sección solicitada no existe.')

    objeto = get_object_or_404(configuracion['modelo'], pk=pk) if pk else None
    formulario = configuracion['formulario'](
        request.POST if request.method == 'POST' else None,
        instance=objeto,
    )
    if request.method == 'POST' and formulario.is_valid():
        formulario.save()
        messages.success(request, configuracion['mensajes'][1 if objeto else 0])
        return redirect('mascotas' if entidad == 'mascotas' else entidad)
    return render(request, 'gestion_clinica/formulario.html', {
        'form': formulario,
        'titulo': f'{"Editar" if objeto else "Registrar"} {configuracion["form_nombre"]}',
        'volver_url': entidad,
    })


@staff_required
def calendario(request):
    hoy = timezone.localdate()
    try:
        anio = int(request.GET.get('anio', hoy.year))
        mes = int(request.GET.get('mes', hoy.month))
        primer_dia = date(anio, mes, 1)
    except (TypeError, ValueError):
        messages.error(request, 'El mes indicado no es válido; se muestra el actual.')
        primer_dia = hoy.replace(day=1)
        anio, mes = primer_dia.year, primer_dia.month

    anterior = (date(anio, mes, 1) - timedelta(days=1)).replace(day=1)
    if mes == 12:
        siguiente = date(anio + 1, 1, 1)
    else:
        siguiente = date(anio, mes + 1, 1)
    inicio = date(anio, mes, 1)
    fin = siguiente - timedelta(days=1)
    citas_por_fecha = {}
    citas = Cita.objects.filter(
        fecha__range=(inicio, fin),
    ).select_related('mascota', 'veterinario').order_by('hora_inicio')
    for cita in citas:
        citas_por_fecha.setdefault(cita.fecha.day, []).append(cita)

    semanas = [
        [
            {'dia': dia, 'citas': citas_por_fecha.get(dia, [])}
            for dia in semana
        ]
        for semana in calendar.Calendar(firstweekday=0).monthdayscalendar(anio, mes)
    ]
    return render(request, 'gestion_clinica/calendario.html', {
        'mes_nombre': (
            'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
            'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
        )[mes - 1].capitalize(),
        'anio': anio,
        'semanas': semanas,
        'anterior': anterior,
        'siguiente': siguiente,
        'hoy': hoy,
        'mes_actual': hoy.month == mes and hoy.year == anio,
        'dias_semana': ('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'),
    })


def _obtener_mascota_autorizada(request, pk):
    mascotas = Mascota.objects.select_related('tutor')
    if request.user.is_staff:
        return get_object_or_404(mascotas, pk=pk)
    return get_object_or_404(mascotas, pk=pk, tutor__usuario=request.user)


@login_required
def detalle_mascota(request, pk):
    mascota = _obtener_mascota_autorizada(request, pk)
    return render(request, 'gestion_clinica/detalle_mascota.html', {
        'mascota': mascota,
        'fichas': mascota.fichas_medicas.select_related('veterinario').order_by('-fecha_atencion'),
        'citas': mascota.citas.select_related('veterinario').order_by('-fecha', '-hora_inicio'),
        'controles': mascota.vacunas_controles.order_by('-fecha_aplicacion'),
    })


@login_required
def imprimir_historial(request, pk):
    mascota = _obtener_mascota_autorizada(request, pk)
    return render(request, 'gestion_clinica/imprimir_historial.html', {
        'mascota': mascota,
        'fichas': mascota.fichas_medicas.select_related('veterinario').order_by('-fecha_atencion'),
        'controles': mascota.vacunas_controles.order_by('-fecha_aplicacion'),
        'fecha_emision': timezone.localdate(),
    })


@login_required
def portal_tutor(request):
    tutor = get_object_or_404(Tutor, usuario=request.user)
    mascotas = tutor.mascotas.all().order_by('nombre')
    return render(request, 'gestion_clinica/portal_tutor.html', {
        'tutor': tutor,
        'mascotas': mascotas,
    })


@staff_required
@require_POST
def enviar_recordatorio(request, pk):
    recordatorio = get_object_or_404(
        VacunaControl.objects.select_related('mascota', 'mascota__tutor'),
        pk=pk,
    )
    tutor = recordatorio.mascota.tutor
    if not settings.EMAIL_CONFIGURED:
        messages.error(request, 'No se envió el correo: primero configura SMTP en el archivo .env.')
        return redirect('recordatorios')
    if not tutor.correo:
        messages.error(request, 'No se envió el correo: el tutor no tiene correo registrado.')
        return redirect('recordatorios')

    fecha = (
        recordatorio.fecha_proximo_control.strftime('%d/%m/%Y')
        if recordatorio.fecha_proximo_control else 'por confirmar'
    )
    asunto = f'Recordatorio de {recordatorio.nombre_procedimiento} para {recordatorio.mascota.nombre}'
    cuerpo = (
        f'Hola {tutor.nombre},\n\n'
        f'Te recordamos el próximo control de {recordatorio.mascota.nombre}: '
        f'{recordatorio.nombre_procedimiento} ({fecha}).\n\n'
        'Contacta a la clínica para coordinar la atención.\n'
    )
    try:
        send_mail(asunto, cuerpo, settings.DEFAULT_FROM_EMAIL, [tutor.correo], fail_silently=False)
    except (OSError, smtplib.SMTPException):
        logger.exception('No se pudo enviar un recordatorio por correo para el registro %s.', pk)
        messages.error(request, 'No se pudo enviar el correo. Revisa la configuración y los registros del servidor.')
    else:
        messages.success(request, f'Recordatorio enviado a {tutor.correo}.')
    return redirect('recordatorios')


class TutorViewSet(viewsets.ModelViewSet):
    queryset = Tutor.objects.all()
    serializer_class = TutorSerializer
    permission_classes = [IsAdminUser]


class MascotaViewSet(viewsets.ModelViewSet):
    queryset = Mascota.objects.all()
    serializer_class = MascotaSerializer
    permission_classes = [IsAdminUser]


class VeterinarioViewSet(viewsets.ModelViewSet):
    queryset = Veterinario.objects.all()
    serializer_class = VeterinarioSerializer
    permission_classes = [IsAdminUser]


class CitaViewSet(viewsets.ModelViewSet):
    queryset = Cita.objects.all()
    serializer_class = CitaSerializer
    permission_classes = [IsAdminUser]


class FichaMedicaViewSet(viewsets.ModelViewSet):
    queryset = FichaMedica.objects.all()
    serializer_class = FichaMedicaSerializer
    permission_classes = [IsAdminUser]


class VacunaControlViewSet(viewsets.ModelViewSet):
    queryset = VacunaControl.objects.all()
    serializer_class = VacunaControlSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get'])
    def alertas_pendientes(self, request):
        hoy = timezone.localdate()
        limite = hoy + timedelta(days=7)
        alertas = self.get_queryset().filter(
            fecha_proximo_control__range=(hoy, limite),
        ).order_by('fecha_proximo_control')
        serializer = self.get_serializer(
            alertas,
            many=True,
            context={'request': request},
        )
        return Response(serializer.data)
