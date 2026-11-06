from django.contrib import admin

from .models import Cita, FichaMedica, Mascota, Tutor, VacunaControl, Veterinario


class MascotaInline(admin.TabularInline):
    model = Mascota
    extra = 0


class VacunaControlInline(admin.TabularInline):
    model = VacunaControl
    extra = 0


@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'rut', 'telefono', 'correo', 'fecha_registro')
    list_filter = ('fecha_registro',)
    search_fields = ('nombre', 'apellido', 'rut', 'telefono', 'correo')
    inlines = (MascotaInline,)


@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especie', 'raza', 'sexo', 'tutor', 'peso_kg')
    list_filter = ('especie', 'sexo', 'raza')
    search_fields = ('nombre', 'raza', 'tutor__nombre', 'tutor__apellido', 'tutor__rut')
    inlines = (VacunaControlInline,)


@admin.register(Veterinario)
class VeterinarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'rut', 'licencia_medica', 'especialidad', 'usuario')
    list_filter = ('especialidad',)
    search_fields = ('nombre', 'apellido', 'rut', 'licencia_medica', 'especialidad')


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'hora_inicio', 'hora_fin', 'mascota', 'veterinario', 'estado')
    list_filter = ('estado', 'fecha', 'veterinario')
    search_fields = (
        'mascota__nombre',
        'mascota__tutor__nombre',
        'mascota__tutor__apellido',
        'veterinario__nombre',
        'veterinario__apellido',
        'motivo',
    )
    date_hierarchy = 'fecha'


@admin.register(FichaMedica)
class FichaMedicaAdmin(admin.ModelAdmin):
    list_display = ('mascota', 'veterinario', 'cita', 'fecha_atencion', 'diagnostico')
    list_filter = ('fecha_atencion', 'veterinario')
    search_fields = (
        'mascota__nombre',
        'veterinario__nombre',
        'veterinario__apellido',
        'motivo_consulta',
        'diagnostico',
        'tratamiento',
    )
    date_hierarchy = 'fecha_atencion'


@admin.register(VacunaControl)
class VacunaControlAdmin(admin.ModelAdmin):
    list_display = ('mascota', 'tipo', 'nombre_procedimiento', 'fecha_aplicacion', 'fecha_proximo_control')
    list_filter = ('tipo', 'fecha_aplicacion', 'fecha_proximo_control')
    search_fields = ('mascota__nombre', 'nombre_procedimiento', 'observaciones')
    date_hierarchy = 'fecha_aplicacion'
