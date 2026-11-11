from django import forms

from .models import Cita, FichaMedica, Mascota, Tutor, VacunaControl, Veterinario


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs['class'] = css_class


class TutorForm(BootstrapModelForm):
    class Meta:
        model = Tutor
        fields = ('usuario', 'nombre', 'apellido', 'rut', 'telefono', 'correo', 'direccion')


class MascotaForm(BootstrapModelForm):
    class Meta:
        model = Mascota
        fields = '__all__'


class CitaForm(BootstrapModelForm):
    class Meta:
        model = Cita
        fields = '__all__'


class FichaMedicaForm(BootstrapModelForm):
    class Meta:
        model = FichaMedica
        fields = '__all__'


class VacunaControlForm(BootstrapModelForm):
    class Meta:
        model = VacunaControl
        fields = '__all__'


class VeterinarioForm(BootstrapModelForm):
    class Meta:
        model = Veterinario
        fields = ('nombre', 'apellido', 'rut', 'licencia_medica', 'especialidad')
