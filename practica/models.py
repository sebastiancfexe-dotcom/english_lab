from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from verbos.models import TIEMPOS, Verbo
from vocabulario.models import Frase, Palabra


class Intento(models.Model):
    TIPOS = [
        ('tarjeta', 'Tarjeta'),
        ('vocab', 'Quiz de vocabulario'),
        ('dictado', 'Dictado de palabras'),
        ('frase', 'Dictado de frases'),
        ('verbo', 'Quiz de verbos'),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='intentos')
    tipo = models.CharField(max_length=10, choices=TIPOS)
    palabra = models.ForeignKey(Palabra, null=True, blank=True, on_delete=models.CASCADE)
    verbo = models.ForeignKey(Verbo, null=True, blank=True, on_delete=models.CASCADE)
    frase = models.ForeignKey(Frase, null=True, blank=True, on_delete=models.CASCADE)
    tiempo = models.CharField(max_length=10, choices=TIEMPOS, blank=True)
    respuesta = models.CharField(max_length=250, blank=True)
    puntaje = models.PositiveSmallIntegerField(null=True, blank=True, help_text='Solo dictado de frases (0-100).')
    correcto = models.BooleanField()
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado']
        indexes = [models.Index(fields=['usuario', 'creado'])]

    def __str__(self):
        return f'{self.usuario} {self.tipo} {"ok" if self.correcto else "fallo"}'


class PreguntaOral(models.Model):
    TEMAS = [('entrevista', 'Entrevista'), ('tecnica', 'Técnica'), ('reunion', 'Reuniones')]

    tema = models.CharField(max_length=12, choices=TEMAS, db_index=True)
    texto = models.CharField(max_length=250, unique=True)
    traduccion = models.CharField(max_length=250, blank=True)
    estructura = models.CharField(max_length=250, blank=True, help_text='Cómo armar la respuesta.')
    modelo = models.TextField(blank=True, help_text='Respuesta de ejemplo en inglés.')
    frases_utiles = models.TextField(blank=True, help_text='Separadas por |')

    class Meta:
        ordering = ['tema', 'id']

    def __str__(self):
        return self.texto

    def lista_frases(self):
        return [f.strip() for f in self.frases_utiles.split('|') if f.strip()]


class RegistroOral(models.Model):
    """Una sesión de práctica oral. El audio no se guarda: queda solo en el navegador."""

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='registros_orales')
    pregunta = models.ForeignKey(PreguntaOral, on_delete=models.CASCADE, related_name='registros')
    duracion_seg = models.PositiveIntegerField(default=0)
    autoevaluacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], help_text='1 = muy difícil, 5 = muy fluido.',
    )
    notas = models.CharField(max_length=300, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado']
        indexes = [models.Index(fields=['usuario', 'creado'])]

    def __str__(self):
        return f'{self.usuario} · {self.pregunta} · {self.autoevaluacion}/5'
