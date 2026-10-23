from django.conf import settings
from django.db import models


class Perfil(models.Model):
    """Resultado del test de nivel. nivel_inicial es el primer bloque (1-10) que aún no domina."""

    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil')
    nivel_inicial = models.PositiveSmallIntegerField(default=1)
    vocab_estimado = models.PositiveIntegerField(default=0)
    test_fecha = models.DateTimeField(null=True, blank=True)
    detalle = models.JSONField(default=dict, blank=True)
    errores = models.JSONField(default=list, blank=True)  # palabras falladas en el último test

    def __str__(self):
        return f'Perfil de {self.usuario}'

    @classmethod
    def de(cls, usuario):
        perfil, _ = cls.objects.get_or_create(usuario=usuario)
        return perfil
