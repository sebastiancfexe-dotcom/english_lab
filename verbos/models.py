import random

from django.db import models

TIEMPOS = [('presente', 'Presente'), ('pasado', 'Pasado'), ('futuro', 'Futuro')]

SUJETOS = ['I', 'You', 'We', 'They', 'He', 'She']
TERCERA_PERSONA = {'He', 'She'}


class Verbo(models.Model):
    infinitivo = models.CharField(max_length=40, unique=True)
    espanol = models.CharField(max_length=80)
    tercera_persona = models.CharField(max_length=40)
    pasado = models.CharField(max_length=40)
    participio = models.CharField(max_length=40)
    irregular = models.BooleanField(default=False)
    ejercitable = models.BooleanField(
        default=True,
        help_text='Desmarcar para verbos que no encajan en las plantillas (ej. be).',
    )

    class Meta:
        ordering = ['infinitivo']

    def __str__(self):
        return f'{self.infinitivo} ({self.espanol})'

    def ejercicio(self, tiempo):
        """Arma una oración con hueco para el tiempo pedido.

        Devuelve el enunciado, la lista de respuestas válidas y una pista.
        """
        sujeto = random.choice(SUJETOS)
        s = sujeto if sujeto == 'I' else sujeto.lower()
        inf = self.infinitivo

        if tiempo == 'presente':
            forma = self.tercera_persona if sujeto in TERCERA_PERSONA else inf
            return {
                'enunciado': f'Every day, {s} ___ ({inf}).',
                'respuestas': [forma],
                'pista': 'presente simple',
            }
        if tiempo == 'pasado':
            return {
                'enunciado': f'Yesterday, {s} ___ ({inf}).',
                'respuestas': [self.pasado],
                'pista': 'pasado simple',
            }
        if random.random() < 0.5:
            return {
                'enunciado': f'Tomorrow, {s} ___ ({inf}).',
                'respuestas': [f'will {inf}'],
                'pista': 'futuro con will',
            }
        be = 'am' if sujeto == 'I' else 'is' if sujeto in TERCERA_PERSONA else 'are'
        return {
            'enunciado': f'Tomorrow, {s} ___ ({inf}).',
            'respuestas': [f'{be} going to {inf}'],
            'pista': 'futuro con going to',
        }
