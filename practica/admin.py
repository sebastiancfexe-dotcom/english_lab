from django.contrib import admin

from .models import Intento, PreguntaOral, RegistroOral


@admin.register(Intento)
class IntentoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'palabra', 'verbo', 'frase', 'tiempo', 'puntaje', 'correcto', 'creado')
    list_filter = ('tipo', 'correcto')


@admin.register(PreguntaOral)
class PreguntaOralAdmin(admin.ModelAdmin):
    list_display = ('texto', 'tema')
    list_filter = ('tema',)
    search_fields = ('texto',)


@admin.register(RegistroOral)
class RegistroOralAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'pregunta', 'autoevaluacion', 'duracion_seg', 'creado')
    list_filter = ('autoevaluacion',)
