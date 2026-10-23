from django.contrib import admin

from .models import Categoria, Frase, Palabra


@admin.register(Frase)
class FraseAdmin(admin.ModelAdmin):
    list_display = ('texto', 'traduccion', 'tema')
    list_filter = ('tema',)
    search_fields = ('texto', 'traduccion')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(Palabra)
class PalabraAdmin(admin.ModelAdmin):
    list_display = ('ingles', 'espanol', 'categoria', 'nivel', 'propietario')
    list_filter = ('categoria', 'nivel')
    search_fields = ('ingles', 'espanol')
