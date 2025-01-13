# obras_privadas/main/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Ciudadano, Empresa, Propuesta

class CiudadanoRegisterForm(UserCreationForm):
    provincia = forms.CharField(max_length=100)
    municipio = forms.CharField(max_length=100)
    dni = forms.CharField(max_length=20)

    class Meta:
        model = Ciudadano
        fields = ['username', 'first_name', 'last_name', 'email', 'provincia', 'municipio', 'dni', 'password1', 'password2']

class EmpresaRegisterForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nombre', 'localidad', 'email_contacto', 'nombre_trabajador', 'apellido_trabajador', 'provincia_trabajador', 'municipio_trabajador', 'email_trabajador', 'dni_trabajador']

class PropuestaForm(forms.ModelForm):
    class Meta:
        model = Propuesta
        fields = ['titulo', 'foto_perfil', 'idea', 'provincia', 'municipio', 'abarca_otra_provincia', 'provincia2', 'documento']
