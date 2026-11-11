from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Tutor(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='perfil_tutor',
    )
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, unique=True)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()
    direccion = models.TextField()
    fecha_registro = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.nombre} {self.apellido} ({self.rut})'


class Mascota(models.Model):
    class Especie(models.TextChoices):
        CANINO = 'canino', 'Canino'
        FELINO = 'felino', 'Felino'
        EXOTICO = 'exotico', 'Exótico'
        OTRO = 'otro', 'Otro'

    class Sexo(models.TextChoices):
        MACHO = 'macho', 'Macho'
        HEMBRA = 'hembra', 'Hembra'

    tutor = models.ForeignKey(
        Tutor,
        on_delete=models.CASCADE,
        related_name='mascotas',
    )
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=10, choices=Especie.choices)
    raza = models.CharField(max_length=100)
    sexo = models.CharField(max_length=10, choices=Sexo.choices)
    fecha_nacimiento = models.DateField()
    peso_kg = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f'{self.nombre} ({self.get_especie_display()})'


class Veterinario(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='perfil_veterinario',
    )
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, unique=True)
    licencia_medica = models.CharField(max_length=50, unique=True)
    especialidad = models.CharField(max_length=100)

    def __str__(self):
        return f'Dr./Dra. {self.nombre} {self.apellido}'


class Cita(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        REALIZADA = 'realizada', 'Realizada'
        CANCELADA = 'cancelada', 'Cancelada'

    mascota = models.ForeignKey(
        Mascota,
        on_delete=models.CASCADE,
        related_name='citas',
    )
    veterinario = models.ForeignKey(
        Veterinario,
        on_delete=models.CASCADE,
        related_name='citas',
    )
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    motivo = models.TextField()
    estado = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )

    def clean(self):
        super().clean()
        if not all((self.veterinario_id, self.fecha, self.hora_inicio, self.hora_fin)):
            return

        errors = {}
        if self.hora_fin <= self.hora_inicio:
            errors['hora_fin'] = 'La hora de fin debe ser posterior a la hora de inicio.'

        if self.estado != self.Estado.CANCELADA:
            citas_solapadas = Cita.objects.filter(
                veterinario_id=self.veterinario_id,
                fecha=self.fecha,
                hora_inicio__lt=self.hora_fin,
                hora_fin__gt=self.hora_inicio,
            ).exclude(estado=self.Estado.CANCELADA)
            if self.pk:
                citas_solapadas = citas_solapadas.exclude(pk=self.pk)
            if citas_solapadas.exists():
                errors['hora_inicio'] = (
                    'El veterinario ya tiene una cita que se solapa en esa fecha y horario.'
                )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f'Cita de {self.mascota} con {self.veterinario} el {self.fecha}'


class FichaMedica(models.Model):
    mascota = models.ForeignKey(
        Mascota,
        on_delete=models.CASCADE,
        related_name='fichas_medicas',
    )
    veterinario = models.ForeignKey(
        Veterinario,
        on_delete=models.CASCADE,
        related_name='fichas_medicas',
    )
    cita = models.OneToOneField(
        Cita,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ficha_medica',
    )
    fecha_atencion = models.DateTimeField(default=timezone.now)
    motivo_consulta = models.TextField()
    diagnostico = models.TextField()
    tratamiento = models.TextField()
    receta_medica = models.TextField(blank=True)
    examenes_clinicos = models.TextField(blank=True)

    def __str__(self):
        return f'Ficha médica de {self.mascota} ({self.fecha_atencion:%Y-%m-%d})'


class VacunaControl(models.Model):
    class Tipo(models.TextChoices):
        VACUNA = 'vacuna', 'Vacuna'
        DESPARASITACION = 'desparasitacion', 'Desparasitación'
        CONTROL = 'control', 'Control'

    mascota = models.ForeignKey(
        Mascota,
        on_delete=models.CASCADE,
        related_name='vacunas_controles',
    )
    tipo = models.CharField(max_length=15, choices=Tipo.choices)
    nombre_procedimiento = models.CharField(max_length=150)
    fecha_aplicacion = models.DateField()
    fecha_proximo_control = models.DateField(null=True, blank=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f'{self.get_tipo_display()}: {self.nombre_procedimiento} - {self.mascota}'
