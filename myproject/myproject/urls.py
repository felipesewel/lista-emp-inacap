"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from miapp import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login'), name='home'),  # Redirige a login inicialmente
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),  # La página home a la que se redirige tras login exitoso
    path('user/list/', views.user_list, name='user_list'),
    path('user/edit/', views.user_edit, name='user_edit'),
    path('user/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('user/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('empleados/', views.listar_trabajadores, name='listar_empleados'),
    path('empleados/', views.listar_trabajadores, name='listar_trabajadores'),
    path('empleados/editar/<int:pk>/', views.editar_trabajador, name='editar_trabajador'),
    path('empleados/contacto_emergencia/editar/<int:pk>/', views.editar_contacto_emergencia, name='editar_contacto_emergencia'),
    path('empleados/carga_familiar/editar/<int:pk>/', views.editar_carga_familiar, name='editar_carga_familiar'),
    path('cargas_familiares/editar/<int:pk>/', views.editar_carga_familiar, name='editar_carga_familiar'),
    path('contactos_emergencia/editar/<int:pk>/', views.editar_contacto_emergencia, name='editar_contacto_emergencia'),
    path('perfil/editar/', views.user_edit, name='user_edit'),
    path('empleados/eliminar/<int:pk>/', views.eliminar_trabajador, name='eliminar_trabajador'),
    path('empleados/agregar/', views.agregar_empleado, name='agregar_empleado'),
]


