from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserDetails(models.Model):
   ROL_CHOICES = [
       ('cliente', 'Cliente'),
       ('admin', 'Admin'),
   ]
   user = models.OneToOneField(User, on_delete=models.CASCADE)
   rol = models.CharField(max_length=10, choices=ROL_CHOICES, default='cliente')
   fecha_nacimiento = models.DateField(null=True, blank=True)
   fono = models.CharField(max_length=20, blank=True)
   numero_doc = models.CharField(max_length=12, blank=True)
   dv = models.CharField(max_length=1, blank=True)
   pasaporte = models.CharField(max_length=1, blank=True)


class Trabajador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # Relación con usuario
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=255)
    sexo = models.CharField(max_length=10, choices=[('Masculino', 'Masculino'), ('Femenino', 'Femenino')])
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=12)
    cargo = models.CharField(max_length=100)
    fecha_ingreso = models.DateField()
    area = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

class ContactoEmergencia(models.Model):
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE, related_name='contactos_emergencia')
    nombre = models.CharField(max_length=255)
    relacion = models.CharField(max_length=100)
    telefono = models.CharField(max_length=12)

    def __str__(self):
        return f'{self.nombre} - {self.relacion}'


class CargaFamiliar(models.Model):
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE, related_name='cargas_familiares')
    nombre = models.CharField(max_length=255)
    parentesco = models.CharField(max_length=100)
    sexo = models.CharField(max_length=10, choices=[('Masculino', 'Masculino'), ('Femenino', 'Femenino')])
    rut = models.CharField(max_length=12)

    def __str__(self):
        return f'{self.nombre} - {self.parentesco}'

###
###DESACTUALIZADO VVVV
###

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField()
    published_date = models.DateField()
    isbn = models.CharField(max_length=13, unique=True)

    def __str__(self):
        return self.title   
    
class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # Calificación de 1 a 5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('book', 'user')  # Un usuario solo puede dejar una reseña por libro

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.rating})"