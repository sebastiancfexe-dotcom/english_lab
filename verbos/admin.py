from django.contrib import admin

from .models import Verbo


@admin.register(Verbo)
class VerboAdmin(admin.ModelAdmin):
    list_display = ('infinitivo', 'espanol', 'tercera_persona', 'pasado', 'participio', 'irregular', 'ejercitable')
    list_filter = ('irregular', 'ejercitable')
    search_fields = ('infinitivo', 'espanol')
