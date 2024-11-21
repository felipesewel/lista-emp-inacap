from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import user_passes_test
from django.forms import modelformset_factory

from miapp.models import UserDetails
from .forms import TrabajadorFullEditForm, TrabajadorEditForm, ContactoEmergenciaForm, CargaFamiliarForm
from .models import Trabajador, ContactoEmergencia, CargaFamiliar
from .forms import LoginForm, UserRegistrationForm
from django.contrib import messages
from .forms import TrabajadorForm


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']  # Usar el RUT como nombre de usuario
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirigir a la página principal después de iniciar sesión
            else:
                messages.error(request, 'RUT o contraseña incorrectos.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
   logout(request)
   return redirect('login')

@login_required
def home(request):
   return render(request, 'home.html')

@login_required
def user_list(request):
   if request.user.userdetails.rol != 'admin':
       messages.error(request, 'You do not have permission to view this page')
       return redirect('home')
   users = User.objects.all()
   return render(request, 'user_list.html', {'users': users})

@login_required
def user_edit(request):
    trabajador = request.user.trabajador

    if request.method == 'POST':
        trabajador_form = TrabajadorEditForm(request.POST, instance=trabajador)
        contacto_form = ContactoEmergenciaForm(request.POST, instance=trabajador.contactos_emergencia.first(), prefix='contacto')
        carga_familiar_form = CargaFamiliarForm(request.POST, instance=trabajador.cargas_familiares.first(), prefix='carga')
        password_form = PasswordChangeForm(user=request.user, data=request.POST)  # Agregar formulario de cambio de contraseña

        if trabajador_form.is_valid() and contacto_form.is_valid() and carga_familiar_form.is_valid() and password_form.is_valid():
            trabajador_form.save()

            # Guardar Contacto de Emergencia
            contacto = contacto_form.save(commit=False)
            contacto.trabajador = trabajador
            contacto.save()

            # Guardar Carga Familiar
            carga_familiar = carga_familiar_form.save(commit=False)
            carga_familiar.trabajador = trabajador
            carga_familiar.save()

            # Guardar la nueva contraseña
            password_form.save()
            update_session_auth_hash(request, password_form.user)  # Mantener la sesión activa

            messages.success(request, 'Tu perfil ha sido actualizado con éxito.')
            return redirect('home')
    else:
        trabajador_form = TrabajadorEditForm(instance=trabajador)
        contacto_form = ContactoEmergenciaForm(instance=trabajador.contactos_emergencia.first(), prefix='contacto')
        carga_familiar_form = CargaFamiliarForm(instance=trabajador.cargas_familiares.first(), prefix='carga')
        password_form = PasswordChangeForm(user=request.user)  # Mostrar formulario de cambio de contraseña

    return render(request, 'user_edit.html', {
        'trabajador_form': trabajador_form,
        'contacto_form': contacto_form,
        'carga_familiar_form': carga_familiar_form,
        'password_form': password_form,  # Enviar formulario de contraseña a la plantilla
    })



@login_required
def editar_trabajador(request, pk):
    trabajador = get_object_or_404(Trabajador, pk=pk)
    if request.method == 'POST':
        form = TrabajadorFullEditForm(request.POST, instance=trabajador)
        if form.is_valid():
            form.save()
            return redirect('listar_empleados')
    else:
        form = TrabajadorFullEditForm(instance=trabajador)
    return render(request, 'editar_trabajador.html', {'form': form})

@login_required
def eliminar_trabajador(request, pk):
    trabajador = get_object_or_404(Trabajador, pk=pk)

    # Verificar si el trabajador que intenta eliminar es el mismo usuario autenticado
    if request.user == trabajador.user:
        messages.error(request, 'No puedes eliminar tu propia cuenta.')
        return redirect('listar_empleados')

    if request.method == 'POST':
        trabajador.delete()
        messages.success(request, 'Trabajador eliminado con éxito.')
        return redirect('listar_empleados')
    
    return render(request, 'eliminar_trabajador.html', {'trabajador': trabajador})

@login_required
def editar_contacto_emergencia(request, pk):
    trabajador = get_object_or_404(Trabajador, pk=pk)
    contacto, created = ContactoEmergencia.objects.get_or_create(trabajador=trabajador)

    if request.method == 'POST':
        form = ContactoEmergenciaForm(request.POST, instance=contacto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contacto de emergencia actualizado con éxito.')
            return redirect('listar_trabajadores')
    else:
        form = ContactoEmergenciaForm(instance=contacto)

    return render(request, 'editar_contacto_emergencia.html', {'form': form, 'trabajador': trabajador})



@login_required
def editar_carga_familiar(request, pk):
    trabajador = get_object_or_404(Trabajador, pk=pk)
    carga, created = CargaFamiliar.objects.get_or_create(trabajador=trabajador)

    if request.method == 'POST':
        form = CargaFamiliarForm(request.POST, instance=carga)
        if form.is_valid():
            form.save()
            messages.success(request, 'Carga familiar actualizada con éxito.')
            return redirect('listar_trabajadores')
    else:
        form = CargaFamiliarForm(instance=carga)

    return render(request, 'editar_carga_familiar.html', {'form': form, 'trabajador': trabajador})

@login_required
def user_delete(request, user_id):
   if request.user.userdetails.rol != 'admin':
       messages.error(request, 'You do not have permission to delete users')
       return redirect('home')

   user = get_object_or_404(User, id=user_id)
   if request.method == 'POST':
       user.delete()
       messages.success(request, 'User deleted successfully')
       return redirect('user_list')

   return render(request, 'user_delete.html', {'user': user})

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Crear el usuario pero no lo guarda en la base de datos aún
            new_user = form.save(commit=False)
            # Establecer la contraseña
            new_user.set_password(form.cleaned_data['password'])
            # Guardar el usuario en la base de datos
            new_user.save()

            # Crear el detalle adicional del usuario
            UserDetails.objects.create(user=new_user)

            messages.success(request, 'El usuario se ha registrado exitosamente.')
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

def is_admin(user):
    return user.is_staff


@user_passes_test(is_admin)
@login_required
def listar_trabajadores(request):
    trabajadores = Trabajador.objects.all()
    return render(request, 'listar_trabajadores.html', {'trabajadores': trabajadores})


@login_required
def filtrar_trabajadores(request):
    trabajadores = Trabajador.objects.all()

    sexo = request.GET.get('sexo')
    cargo = request.GET.get('cargo')
    area = request.GET.get('area')

    if sexo:
        trabajadores = trabajadores.filter(sexo=sexo)
    if cargo:
        trabajadores = trabajadores.filter(cargo=cargo)
    if area:
        trabajadores = trabajadores.filter(area=area)

    return render(request, 'filtrar_trabajadores.html', {'trabajadores': trabajadores})

@user_passes_test(is_admin)
@login_required
def agregar_empleado(request):
    if request.method == 'POST':
        trabajador_form = TrabajadorForm(request.POST)
        if trabajador_form.is_valid():
            trabajador_form.save()
            messages.success(request, 'Empleado agregado con éxito.')
            return redirect('listar_empleados')
    else:
        trabajador_form = TrabajadorForm()

    return render(request, 'agregar_empleado.html', {'trabajador_form': trabajador_form})

@user_passes_test(is_admin)
@login_required
def listar_trabajadores(request):
    trabajadores = Trabajador.objects.all()
    return render(request, 'listar_trabajadores.html', {'trabajadores': trabajadores})

@login_required
def home(request):
    trabajador = request.user.trabajador  # Relación OneToOne entre User y Trabajador
    return render(request, 'home.html', {
        'nombre_empleado': trabajador.nombre,
        'cargo': trabajador.cargo,
    })

