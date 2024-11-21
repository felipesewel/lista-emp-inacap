from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserDetails
from .models import Book

class UserDetailsInline(admin.StackedInline):
   model = UserDetails
   can_delete = False
   verbose_name_plural = 'Detalles de Usuario'

class CustomUserAdmin(UserAdmin):
   inlines = (UserDetailsInline,)
   list_display = ('username', 'email', 'first_name', 'last_name', 'get_rol', 'get_fono')
   list_filter = UserAdmin.list_filter + ('userdetails__rol',)

   def get_rol(self, obj):
       return obj.userdetails.rol if hasattr(obj, 'userdetails') else ''
   get_rol.short_description = 'Rol'

   def get_fono(self, obj):
       return obj.userdetails.fono if hasattr(obj, 'userdetails') else ''
   get_fono.short_description = 'Teléfono'

# Desregistrar el UserAdmin original
admin.site.unregister(User)
# Registrar nuestro CustomUserAdmin
admin.site.register(User, CustomUserAdmin)

@admin.register(UserDetails)
class UserDetailsAdmin(admin.ModelAdmin):
   list_display = ('user', 'rol', 'fecha_nacimiento', 'fono', 'numero_doc', 'dv', 'pasaporte')
   list_filter = ('rol',)
   search_fields = ('user__username', 'user__email', 'fono', 'numero_doc')

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_date', 'isbn')
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('published_date',)
