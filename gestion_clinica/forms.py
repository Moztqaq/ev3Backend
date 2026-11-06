from django import forms

from .models import Cita, FichaMedica, Mascota, Tutor


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs['class'] = css_class


class TutorForm(BootstrapModelForm):
    class Meta:
        model = Tutor
        fields = '__all__'


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
