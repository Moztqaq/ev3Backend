from copy import copy

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Cita, FichaMedica, Mascota, Tutor, VacunaControl, Veterinario


class TutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tutor
        fields = '__all__'


class MascotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mascota
        fields = '__all__'


class VeterinarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veterinario
        fields = '__all__'


class CitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cita
        fields = '__all__'

    def validate(self, attrs):
        cita = copy(self.instance) if self.instance is not None else Cita()
        for field, value in attrs.items():
            setattr(cita, field, value)

        try:
            cita.clean()
        except DjangoValidationError as exc:
            if hasattr(exc, 'message_dict'):
                raise ValidationError(exc.message_dict) from exc
            raise ValidationError({'non_field_errors': exc.messages}) from exc

        return attrs


class FichaMedicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FichaMedica
        fields = '__all__'


class VacunaControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = VacunaControl
        fields = '__all__'
