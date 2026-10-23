from django.conf import settings
from django.db import models
from django.db.models import Q


class Categoria(models.Model):
    nombre = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(unique=True)
    es_tecnica = models.BooleanField(
        default=False,
        help_text='Vocabulario técnico (software). No entra en la práctica por bloques ni en la meta de 1000.',
    )

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Frase(models.Model):
    """Oración completa para dictado."""

    TEMAS = [('dev', 'Desarrollo de software'), ('diario', 'Día a día')]

    texto = models.CharField(max_length=250, unique=True)
    traduccion = models.CharField(max_length=250, blank=True)
    tema = models.CharField(max_length=10, choices=TEMAS, default='diario', db_index=True)

    class Meta:
        ordering = ['tema', 'id']

    def __str__(self):
        return self.texto


class PalabraQuerySet(models.QuerySet):
    def oficiales(self):
        return self.filter(propietario__isnull=True)

    def visibles(self, usuario):
        """Palabras oficiales más las que agregó este usuario."""
        return self.filter(Q(propietario__isnull=True) | Q(propietario=usuario))


class Palabra(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='palabras')
    ingles = models.CharField(max_length=80)
    espanol = models.CharField(max_length=80)
    ejemplo = models.CharField(max_length=200, blank=True)
    nivel = models.PositiveSmallIntegerField(
        null=True, blank=True, db_index=True,
        help_text='Bloque de dificultad 1-10 del núcleo de ~1000 palabras. Vacío = palabra temática o propia.',
    )
    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE,
        related_name='palabras_propias', help_text='Vacío = palabra oficial, visible para todos.',
    )

    objects = PalabraQuerySet.as_manager()

    class Meta:
        ordering = ['ingles']
        constraints = [
            models.UniqueConstraint(
                fields=['categoria', 'ingles'], condition=Q(propietario__isnull=True),
                name='palabra_oficial_unica_por_categoria',
            ),
            models.UniqueConstraint(
                fields=['propietario', 'ingles'], condition=Q(propietario__isnull=False),
                name='palabra_propia_unica_por_usuario',
            ),
        ]

    def __str__(self):
        return f'{self.ingles} = {self.espanol}'
