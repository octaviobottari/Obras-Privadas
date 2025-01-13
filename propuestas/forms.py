from django.http import JsonResponse
from django import forms
from .models import Usuario, Propuesta, Comment
from datetime import date

API_BASE_URL = "https://apis.datos.gob.ar/georef/api/"

def fetch_provincias():
    from .views import fetch_provincias  # Lazy import
    return fetch_provincias()

class DateInput(forms.DateInput):
    input_type = 'date'

class RegistroForm(forms.ModelForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)
    fecha_nacimiento = forms.DateField(widget=DateInput(), input_formats=['%Y-%m-%d'], required=False)
    provincia = forms.ChoiceField(choices=[], required=False)
    
    class Meta:
        model = Usuario
        fields = ['username', 'nombre', 'apellido', 'email', 'fecha_nacimiento', 'dni', 'provincia']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['provincia'].choices = fetch_provincias()

    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento and fecha_nacimiento > date.today():
            raise forms.ValidationError("La fecha de nacimiento no puede ser en el futuro.")
        return fecha_nacimiento

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if dni and (not dni.isdigit() or len(dni) != 8):
            raise forms.ValidationError("El DNI debe contener 8 números.")
        return dni

    def clean_password2(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class EmpresaRegistroForm(forms.ModelForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control', 'style': 'width: 300px;'}))
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control', 'style': 'width: 300px;'}))

    class Meta:
        model = Usuario
        fields = ['username', 'nombre_empresa', 'nombre', 'apellido', 'cuit_empresa', 'email', 'password1', 'password2']
        labels = {
            'username': 'Nombre de Usuario',
            'nombre_empresa': 'Nombre de la Empresa',
            'nombre': 'Nombre del títular',
            'apellido': 'Apellido del títular',
            'cuit_empresa': 'Cuit de la Empresa',
            'email': 'Email del títular',
        }
        help_texts = {
            'username': None,  # This removes the default help text for the username field
        }

    def __init__(self, *args, **kwargs):
        super(EmpresaRegistroForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'



    def clean_password2(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.tipo_usuario = 'empresa'
        if commit:
            user.save()
        return user


class PropuestaForm(forms.ModelForm):
    class Meta:
        model = Propuesta
        fields = ['TITULO', 'FOTO_DE_PERFIL_DEL_PROYECTO', 'IDEA', 'PROVINCIA', 'PROPUESTA_PDF']
        labels = {
            'TITULO': 'Título de la propuesta',  # Shorter label for TITULO
            'FOTO_DE_PERFIL_DEL_PROYECTO': 'Foto portada',
            'IDEA': 'Descripción',     # Shorter label for IDEA
            'PROVINCIA': 'Provincia',  # Shorter label for PROVINCIA
            'PROPUESTA_PDF': 'Adjuntar formulario'  # Shorter label for PROPUESTA_PDF
        }

    def __init__(self, *args, **kwargs):
        super(PropuestaForm, self).__init__(*args, **kwargs)
        self.fields['TITULO'].widget.attrs.update({'class': 'form-control'})
        self.fields['IDEA'].widget = forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
        self.fields['PROVINCIA'].widget = forms.Select(choices=[
            ('Buenos Aires', 'Buenos Aires'),
            ('Ciudad Autónoma de Buenos Aires', 'Ciudad Autónoma de Buenos Aires'),
            ('Catamarca', 'Catamarca'),
            ('Chaco', 'Chaco'),
            ('Chubut', 'Chubut'),
            ('Córdoba', 'Córdoba'),
            ('Corrientes', 'Corrientes'),
            ('Entre Ríos', 'Entre Ríos'),
            ('Formosa', 'Formosa'),
            ('Jujuy', 'Jujuy'),
            ('La Pampa', 'La Pampa'),
            ('La Rioja', 'La Rioja'),
            ('Mendoza', 'Mendoza'),
            ('Misiones', 'Misiones'),
            ('Neuquén', 'Neuquén'),
            ('Río Negro', 'Río Negro'),
            ('Salta', 'Salta'),
            ('San Juan', 'San Juan'),
            ('San Luis', 'San Luis'),
            ('Santa Cruz', 'Santa Cruz'),
            ('Santa Fe', 'Santa Fe'),
            ('Santiago del Estero', 'Santiago del Estero'),
            ('Tierra del Fuego, Antártida e Islas del Atlántico Sur', 'Tierra del Fuego, Antártida e Islas del Atlántico Sur'),
            ('Tucumán', 'Tucumán'),
        ])
        self.fields['PROVINCIA'].widget.attrs.update({'class': 'form-control'})
        self.fields['FOTO_DE_PERFIL_DEL_PROYECTO'].widget = forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
        self.fields['PROPUESTA_PDF'].widget = forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'application/pdf'})

class PropuestaFormEmpresa(forms.ModelForm):
    class Meta:
        model = Propuesta
        fields = ['TITULO', 'FOTO_DE_PERFIL_DEL_PROYECTO', 'IDEA', 'PROVINCIA', 'PROPUESTA_PDF', 'FORMULARIO_FINANCIAMIENTO']
        labels = {
            'TITULO': 'Título de la propuesta',  # Shorter label for TITULO
            'FOTO_DE_PERFIL_DEL_PROYECTO': 'Foto portada',
            'IDEA': 'Descripción',     # Shorter label for IDEA
            'PROVINCIA': 'Provincia',  # Shorter label for PROVINCIA
            'PROPUESTA_PDF': 'Adjuntar formulario',  # Shorter label for PROPUESTA_PDF
            'FORMULARIO_FINANCIAMIENTO': 'Adjuntar formulario de Plan de Financiamiento'  # Custom label for FORMULARIO_FINANCIAMIENTO
        }

    def __init__(self, *args, **kwargs):
        super(PropuestaFormEmpresa, self).__init__(*args, **kwargs)
        self.fields['TITULO'].widget.attrs.update({'class': 'form-control'})
        self.fields['IDEA'].widget = forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
        self.fields['PROVINCIA'].widget = forms.Select(choices=[
            ('Buenos Aires', 'Buenos Aires'),
            ('Ciudad Autónoma de Buenos Aires', 'Ciudad Autónoma de Buenos Aires'),
            ('Catamarca', 'Catamarca'),
            ('Chaco', 'Chaco'),
            ('Chubut', 'Chubut'),
            ('Córdoba', 'Córdoba'),
            ('Corrientes', 'Corrientes'),
            ('Entre Ríos', 'Entre Ríos'),
            ('Formosa', 'Formosa'),
            ('Jujuy', 'Jujuy'),
            ('La Pampa', 'La Pampa'),
            ('La Rioja', 'La Rioja'),
            ('Mendoza', 'Mendoza'),
            ('Misiones', 'Misiones'),
            ('Neuquén', 'Neuquén'),
            ('Río Negro', 'Río Negro'),
            ('Salta', 'Salta'),
            ('San Juan', 'San Juan'),
            ('San Luis', 'San Luis'),
            ('Santa Cruz', 'Santa Cruz'),
            ('Santa Fe', 'Santa Fe'),
            ('Santiago del Estero', 'Santiago del Estero'),
            ('Tierra del Fuego, Antártida e Islas del Atlántico Sur', 'Tierra del Fuego, Antártida e Islas del Atlántico Sur'),
            ('Tucumán', 'Tucumán'),
        ])
        self.fields['PROVINCIA'].widget.attrs.update({'class': 'form-control'})
        self.fields['FOTO_DE_PERFIL_DEL_PROYECTO'].widget = forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
        self.fields['PROPUESTA_PDF'].widget = forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'application/pdf'})
        self.fields['FORMULARIO_FINANCIAMIENTO'].widget = forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'application/pdf'})



class FinanciarForm(forms.Form):
    archivo = forms.FileField(label="Subir Formulario de Financiamiento (PDF)", widget=forms.FileInput(attrs={'accept': 'application/pdf'}))

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']  # Ensure this matches the model
        labels = {
            'comment': 'Comentar'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configure the widget for the 'comment' field
        self.fields['comment'].widget = forms.Textarea(attrs={
            'class': 'form-control comment-textarea',
            'rows': 2,
        })
        # Ensure the 'comment' field is required
        self.fields['comment'].required = True 

class EmailUpdateForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['email']

class UserUpdateForm(forms.ModelForm):
    provincia = forms.ChoiceField(choices=[])

    class Meta:
        model = Usuario
        fields = ['provincia']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['provincia'].choices = fetch_provincias()


