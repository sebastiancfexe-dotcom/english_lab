import math

from django.core.management.base import BaseCommand

from practica import datos_iniciales as d
from practica.datos_orales import PREGUNTAS_ORALES
from practica.models import PreguntaOral
from verbos.models import Verbo
from vocabulario.frases import FRASES_DEV, FRASES_DIARIO
from vocabulario.frecuentes import PALABRAS_FRECUENTES
from vocabulario.models import Categoria, Frase, Palabra
from vocabulario.tecnico import TECNICO

BLOQUES = 10


def filas(texto):
    return [linea.split('|') for linea in texto.splitlines() if linea.strip()]


class Command(BaseCommand):
    help = 'Carga (o actualiza) verbos, vocabulario temático y el núcleo por frecuencia. Se puede repetir sin duplicar.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--si-vacio', action='store_true',
            help='No hace nada si ya hay palabras. Útil al arrancar en Docker, para no pisar lo que editaste en el admin.',
        )

    def handle(self, *args, **options):
        if options['si_vacio'] and Palabra.objects.exists():
            self.stdout.write('Ya hay datos; no se carga nada.')
            return
        n_verbos = self._verbos()
        n_tematicas = self._tematicas()
        n_nucleo = self._nucleo()
        n_tecnicas = self._tecnicas()
        n_frases = self._frases()
        n_orales = self._orales()
        self.stdout.write(self.style.SUCCESS(
            f'{n_verbos} verbos, {n_tematicas} palabras temáticas, {n_nucleo} palabras en el núcleo por niveles, '
            f'{n_tecnicas} términos técnicos, {n_frases} frases y {n_orales} preguntas orales.'
        ))

    def _frases(self):
        """Frases de dictado: las propias con traducción + las oraciones de ejemplo del vocabulario técnico."""
        n = 0
        for tema, texto in (('dev', FRASES_DEV), ('diario', FRASES_DIARIO)):
            for ingles, espanol in filas(texto):
                Frase.objects.update_or_create(texto=ingles, defaults={'traduccion': espanol, 'tema': tema})
                n += 1
        ejemplos = (
            Palabra.objects.oficiales().filter(categoria__es_tecnica=True).exclude(ejemplo='')
            .values_list('ejemplo', flat=True)
        )
        for ejemplo in ejemplos:
            _, creada = Frase.objects.get_or_create(texto=ejemplo, defaults={'tema': 'dev'})
            n += 1
        return n

    def _orales(self):
        for tema, texto, traduccion, estructura, modelo, frases in PREGUNTAS_ORALES:
            PreguntaOral.objects.update_or_create(texto=texto, defaults={
                'tema': tema, 'traduccion': traduccion, 'estructura': estructura,
                'modelo': modelo, 'frases_utiles': frases,
            })
        return len(PREGUNTAS_ORALES)

    def _verbos(self):
        n = 0
        for inf, es, tercera, pasado, participio in filas(d.VERBOS_IRREGULARES):
            Verbo.objects.update_or_create(infinitivo=inf, defaults={
                'espanol': es, 'tercera_persona': tercera, 'pasado': pasado, 'participio': participio,
                'irregular': True, 'ejercitable': inf != 'be',
            })
            n += 1
        for inf, es, tercera, pasado in filas(d.VERBOS_REGULARES):
            Verbo.objects.update_or_create(infinitivo=inf, defaults={
                'espanol': es, 'tercera_persona': tercera, 'pasado': pasado, 'participio': pasado,
                'irregular': False, 'ejercitable': True,
            })
            n += 1
        return n

    def _tematicas(self):
        n = 0
        for nombre, slug, texto in d.VOCABULARIO:
            categoria, _ = Categoria.objects.update_or_create(slug=slug, defaults={'nombre': nombre})
            for ingles, espanol in filas(texto):
                Palabra.objects.update_or_create(
                    categoria=categoria, ingles=ingles, propietario=None, defaults={'espanol': espanol},
                )
                n += 1
        return n

    def _tecnicas(self):
        n = 0
        for nombre, slug, texto in TECNICO:
            categoria, _ = Categoria.objects.update_or_create(
                slug=slug, defaults={'nombre': nombre, 'es_tecnica': True},
            )
            for ingles, espanol, ejemplo in filas(texto):
                Palabra.objects.update_or_create(
                    categoria=categoria, ingles=ingles, propietario=None,
                    defaults={'espanol': espanol, 'ejemplo': ejemplo},
                )
                n += 1
        return n

    def _nucleo(self):
        """Reparte la lista por frecuencia en 10 bloques. Si la palabra ya existe, solo se le asigna el nivel."""
        vistos, lista = set(), []
        for ingles, espanol in filas(PALABRAS_FRECUENTES):
            if ingles.lower() not in vistos:
                vistos.add(ingles.lower())
                lista.append((ingles, espanol))

        tamano = math.ceil(len(lista) / BLOQUES)
        general, _ = Categoria.objects.update_or_create(slug='general', defaults={'nombre': 'General (frecuentes)'})
        for i, (ingles, espanol) in enumerate(lista):
            nivel = min(BLOQUES, i // tamano + 1)
            existente = (
                Palabra.objects.oficiales()
                .filter(ingles__iexact=ingles, categoria__es_tecnica=False)
                .first()
            )
            if existente:
                if existente.nivel != nivel:
                    existente.nivel = nivel
                    existente.save(update_fields=['nivel'])
            else:
                Palabra.objects.create(categoria=general, ingles=ingles, espanol=espanol, nivel=nivel)
        return len(lista)
