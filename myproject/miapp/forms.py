import re
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserDetails
from .models import Trabajador, ContactoEmergencia, CargaFamiliar
from datetime import date
from django.contrib.auth.forms import PasswordChangeForm
from django.forms import modelformset_factory

# Formulario de inicio de sesión
class LoginForm(forms.Form):
    username = forms.CharField(label="RUT", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    # Validación personalizada para el RUT
    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        # Patrón para validar el formato "XXXXXXXX-X"
        pattern = r'^\d{8}-[\dkK]$'
        if not re.match(pattern, rut):
            raise ValidationError('El formato del RUT es inválido. El formato correcto es XXXXXXXX-X (8 números seguidos por un guion y finalizado con una "K" o un número).')
        return rut

def validar_telefono_chile(telefono):
    if not re.match(r'^\+56\d{9}$', telefono):  # Validar formato +56 seguido de 9 dígitos
        raise ValidationError('El formato del teléfono es inválido. Debe ser "+56XXXXXXXXX" y contener solo números (Ejemplo: +56912345678).')

def validar_rut_internacional(rut):
    # Validar formato: 7-9 dígitos seguidos de un guion y un dígito verificador
    if not re.match(r'^\d{7,9}-[0-9Kk]$', rut):
        raise ValidationError('El RUT debe tener el formato "12345678-K" con 7, 8 o 9 dígitos seguidos de un guion.')


class TrabajadorEditForm(forms.ModelForm): #EDITAR PERFIL
    class Meta:
        model = Trabajador
        fields = ['direccion', 'telefono']
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        validar_telefono_chile(telefono)  # Validar el formato
        return telefono

class CustomPasswordChangeForm(PasswordChangeForm):
    pass  # Usar la lógica de cambio de contraseña predeterminada de Django

class TrabajadorFullEditForm(forms.ModelForm): #EDITAR ADMIN
    class Meta:
        model = Trabajador
        fields = ['rut', 'nombre', 'sexo', 'direccion', 'telefono', 'cargo', 'fecha_ingreso', 'area', 'departamento']
        widgets = {
            'rut': forms.TextInput(attrs={'placeholder': '12345678-K', 'maxlength':'12'}),
            'telefono': forms.TextInput(attrs={'placeholder': '+56912345678', 'maxlength':'12'}),
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
        }
    # Validación personalizada para evitar fechas futuras
    def clean_fecha_ingreso(self):
        fecha_ingreso = self.cleaned_data.get('fecha_ingreso')
        if fecha_ingreso > date.today():
            raise ValidationError("La fecha de ingreso no puede ser una fecha futura.")
        return fecha_ingreso
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        validar_telefono_chile(telefono)  # Validar el formato
        return telefono
    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        validar_rut_internacional(rut)  # Validar el formato del RUT
        return rut
# Formulario de Contacto de Emergencia
class ContactoEmergenciaForm(forms.ModelForm):
    class Meta:
        model = ContactoEmergencia
        fields = ['nombre', 'relacion', 'telefono']
        widgets = {
            'telefono': forms.TextInput(attrs={'placeholder': '+56912345678', 'maxlength':'12'}),
        }
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        validar_telefono_chile(telefono)  # Validar el formato
        return telefono
    
class CargaFamiliarForm(forms.ModelForm):
    class Meta:
        model = CargaFamiliar
        fields = ['nombre', 'parentesco', 'sexo', 'rut']
        widgets = {
            'rut': forms.TextInput(attrs={'placeholder': '12345678-K', 'maxlength':'12'}),
        }
    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        validar_rut_internacional(rut)  # Validar el formato del RUT
        return rut

# Formulario para editar detalles adicionales del usuario
class UserDetailsForm(forms.ModelForm):
   class Meta:
       model = UserDetails
       fields = ['rol', 'fecha_nacimiento', 'fono', 'numero_doc', 'dv', 'pasaporte']


# Formulario de registro
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repite la contraseña', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    # Validación para confirmar que ambas contraseñas coinciden
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cd['password2']

# Formulario de Trabajador
class TrabajadorForm(forms.ModelForm):
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': 'Ingrese una contraseña'}),
        help_text="La contraseña debe tener al menos 8 caracteres."
    )
    is_admin = forms.BooleanField(
        label="¿Es administrador?",
        required=False,
        initial=False,
        help_text="Seleccione si este empleado tendrá permisos de administrador."
    )
    class Meta:
        model = Trabajador
        fields = ['rut', 'nombre', 'sexo', 'direccion', 'telefono', 'cargo', 'fecha_ingreso', 'area', 'departamento']
        widgets = {
            'rut': forms.TextInput(attrs={'placeholder': '12345678-K', 'maxlength':'12'}),
            'telefono': forms.TextInput(attrs={'placeholder': '+56912345678', 'maxlength':'12'}),
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
        }


    def save(self, commit=True):
        trabajador = super().save(commit=False)
        user = User(
            username=self.cleaned_data['rut'],  # Usamos el RUT como username
        )
        user.set_password(self.cleaned_data['password'])

        # Configurar permisos
        if self.cleaned_data['is_admin']:
            user.is_staff = True

        if commit:
            user.save()
            trabajador.user = user  # Vincular al usuario
            trabajador.save()
        return trabajador
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        validar_telefono_chile(telefono)  # Validar el formato
        return telefono

    # Validar que la fecha de ingreso no sea futura
    def clean_fecha_ingreso(self):
        fecha_ingreso = self.cleaned_data.get('fecha_ingreso')
        if fecha_ingreso and fecha_ingreso > date.today():
            raise ValidationError('La fecha de ingreso no puede ser una fecha futura.')
        return fecha_ingreso

    # Validación personalizada para el RUT
    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        validar_rut_internacional(rut)  # Validar el formato del RUT
        return rut