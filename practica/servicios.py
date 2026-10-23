"""Lógica de práctica separada de las vistas: nivel, dominio, selección de palabras, rachas y estadísticas."""
import random
import re
from collections import defaultdict
from datetime import timedelta
from difflib import SequenceMatcher

from django.conf import settings
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from usuarios.models import Perfil
from vocabulario.models import Frase, Palabra

from .models import Intento, PreguntaOral, RegistroOral

BLOQUES = 10
PREGUNTAS_POR_BLOQUE = 5
OPCIONES = 4
PROBABILIDAD_AZAR = 1 / OPCIONES
DOMINIO_BLOQUE = 0.8        # un bloque se considera dominado cuando se supera este porcentaje
ACIERTOS_PARA_DOMINAR = 3   # una palabra se domina con 3+ aciertos y 80%+ de precisión
PRECISION_PARA_DOMINAR = 0.8
PESO_DOMINADA = 0.2         # las palabras ya dominadas siguen apareciendo, pero poco


def normalizar(texto):
    return ' '.join(texto.lower().split())


# ---------------------------------------------------------------- test de nivel

def construir_test():
    """Elige PREGUNTAS_POR_BLOQUE palabras por bloque, con opciones de bloques vecinos como distractores."""
    por_bloque = defaultdict(list)
    for p in Palabra.objects.oficiales().filter(nivel__isnull=False):
        por_bloque[p.nivel].append(p)

    preguntas = []
    for bloque in range(1, BLOQUES + 1):
        palabras = por_bloque.get(bloque, [])
        for palabra in random.sample(palabras, min(PREGUNTAS_POR_BLOQUE, len(palabras))):
            vecinas = por_bloque.get(bloque - 1, []) + palabras + por_bloque.get(bloque + 1, [])
            vistos = {palabra.espanol}
            distractores = []
            random.shuffle(vecinas)
            for otra in vecinas:
                if otra.espanol not in vistos:
                    vistos.add(otra.espanol)
                    distractores.append(otra)
                if len(distractores) == OPCIONES - 1:
                    break
            opciones = distractores + [palabra]
            random.shuffle(opciones)
            preguntas.append({
                'id': palabra.id,
                'ingles': palabra.ingles,
                'opciones': [{'id': o.id, 'espanol': o.espanol} for o in opciones],
            })
    return preguntas


def evaluar_nivel(respuestas):
    """respuestas: lista de {palabra_id, elegida_id}. Se recalcula todo en el servidor.

    Por bloque se corrige el azar: dominio = (precisión - 25%) / 75%. Sumando dominio × tamaño del bloque se obtiene
    el vocabulario estimado. nivel_inicial es el primer bloque con dominio menor a 80%.
    """
    ids = [r.get('palabra_id') for r in respuestas if isinstance(r, dict)]
    palabras = {p.id: p for p in Palabra.objects.oficiales().filter(id__in=ids)}
    elegidas = Palabra.objects.filter(id__in=[r.get('elegida_id') for r in respuestas if isinstance(r, dict)])
    espanol_de = {p.id: p.espanol for p in elegidas}
    errores = []

    conteo = defaultdict(lambda: [0, 0])  # bloque -> [aciertos, total]
    vistas = set()
    for r in respuestas:
        if not isinstance(r, dict):
            continue
        pid = r.get('palabra_id')
        palabra = palabras.get(pid)
        bloque = palabra.nivel if palabra else None
        if bloque is None or pid in vistas:
            continue
        vistas.add(pid)
        conteo[bloque][1] += 1
        if r.get('elegida_id') == pid:
            conteo[bloque][0] += 1
        else:
            errores.append({
                'bloque': bloque,
                'ingles': palabra.ingles,
                'correcta': palabra.espanol,
                'elegida': espanol_de.get(r.get('elegida_id')),  # None = "No la sé"
            })

    tamanos = dict(
        Palabra.objects.oficiales().filter(nivel__isnull=False).values_list('nivel').annotate(n=Count('id'))
    )
    detalle, estimado, nivel_inicial = {}, 0.0, None
    for bloque in sorted(tamanos):
        aciertos, total = conteo.get(bloque, (0, 0))
        precision = aciertos / total if total else 0
        dominio = max(0.0, (precision - PROBABILIDAD_AZAR) / (1 - PROBABILIDAD_AZAR))
        detalle[str(bloque)] = {'aciertos': aciertos, 'total': total, 'dominio': round(dominio * 100)}
        estimado += dominio * tamanos[bloque]
        if nivel_inicial is None and dominio < DOMINIO_BLOQUE:
            nivel_inicial = bloque
    if nivel_inicial is None:
        nivel_inicial = max(tamanos, default=0) + 1  # domina todo el núcleo
    return {'vocab_estimado': round(estimado), 'nivel_inicial': nivel_inicial, 'detalle': detalle, 'errores': errores}


def guardar_nivel(usuario, resultado):
    perfil = Perfil.de(usuario)
    perfil.vocab_estimado = resultado['vocab_estimado']
    perfil.nivel_inicial = resultado['nivel_inicial']
    perfil.detalle = resultado['detalle']
    perfil.errores = resultado['errores']
    perfil.test_fecha = timezone.now()
    perfil.save()
    return perfil


def etiqueta_nivel(vocab_estimado):
    if vocab_estimado < 200:
        return 'Principiante'
    if vocab_estimado < 450:
        return 'Básico'
    if vocab_estimado < 750:
        return 'Intermedio bajo'
    if vocab_estimado < 950:
        return 'Intermedio'
    return 'Dominas el núcleo'


# ---------------------------------------------------------------- dominio y progreso

def _aciertos_y_fallos(usuario):
    filas = (
        Intento.objects.filter(usuario=usuario, palabra__isnull=False)
        .values('palabra')
        .annotate(ok=Count('id', filter=Q(correcto=True)), mal=Count('id', filter=Q(correcto=False)))
    )
    return {f['palabra']: (f['ok'], f['mal']) for f in filas}


def _dominada(ok, mal):
    return ok >= ACIERTOS_PARA_DOMINAR and ok / (ok + mal) >= PRECISION_PARA_DOMINAR


def estado(usuario):
    """Cuántas palabras domina el usuario y en qué bloque está trabajando.

    Se cuentan como dominadas las del bloque por debajo de su nivel inicial (las dio por conocidas el test)
    más las que domine practicando.
    """
    perfil = Perfil.de(usuario)
    meta = getattr(settings, 'META_VOCABULARIO', 1000)
    stats = _aciertos_y_fallos(usuario)
    ids_dominadas = [pid for pid, (ok, mal) in stats.items() if _dominada(ok, mal)]

    oficiales = Palabra.objects.oficiales()
    asumidas = oficiales.filter(nivel__lt=perfil.nivel_inicial).count()
    por_practica = (
        Palabra.objects.visibles(usuario).filter(id__in=ids_dominadas)
        .exclude(nivel__lt=perfil.nivel_inicial)
        .exclude(categoria__es_tecnica=True)  # el vocabulario técnico se mide aparte
        .count()
    )
    tecnicas = oficiales.filter(categoria__es_tecnica=True)

    tamanos = dict(oficiales.filter(nivel__isnull=False).values_list('nivel').annotate(n=Count('id')))
    dominadas_por_bloque = dict(
        Palabra.objects.filter(id__in=ids_dominadas, nivel__isnull=False, propietario__isnull=True)
        .values_list('nivel').annotate(n=Count('id'))
    )
    bloque_activo = None
    for bloque in sorted(tamanos):
        if bloque < perfil.nivel_inicial:
            continue
        if dominadas_por_bloque.get(bloque, 0) / tamanos[bloque] < DOMINIO_BLOQUE:
            bloque_activo = bloque
            break

    total = asumidas + por_practica
    return {
        'perfil': perfil,
        'asumidas': asumidas,
        'por_practica': por_practica,
        'total': total,
        'meta': meta,
        'porcentaje_meta': min(100, round(100 * total / meta)),
        'desbloquea_en': round(meta * 0.9),
        'desbloqueado': total >= round(meta * 0.9),
        'bloque_activo': bloque_activo,
        'tecnicas_total': tecnicas.count(),
        'tecnicas_dominadas': tecnicas.filter(id__in=ids_dominadas).count(),
        'ultimo_bloque': max(tamanos, default=BLOQUES),
        'stats': stats,
        'ids_dominadas': set(ids_dominadas),
    }


# ---------------------------------------------------------------- selección de palabras

def elegir_palabras(usuario, categoria_slug=None, n=1):
    """Elige n palabras distintas, con más peso a las que se fallan y menos a las dominadas.

    Sin categoría se trabaja el bloque activo del usuario (más las palabras temáticas y propias).
    El vocabulario técnico solo aparece cuando se elige su categoría.
    """
    est = estado(usuario)
    candidatas = Palabra.objects.visibles(usuario)
    if categoria_slug:
        candidatas = candidatas.filter(categoria__slug=categoria_slug)
    else:
        tope = est['bloque_activo'] or est['ultimo_bloque']
        candidatas = candidatas.exclude(categoria__es_tecnica=True).filter(
            Q(nivel__isnull=True) | Q(nivel__gte=est['perfil'].nivel_inicial, nivel__lte=tope)
        )
    pool = list(candidatas)
    if not pool and not categoria_slug:
        pool = list(Palabra.objects.visibles(usuario))
    if not pool:
        return []

    pesos = []
    for p in pool:
        ok, mal = est['stats'].get(p.id, (0, 0))
        if p.id in est['ids_dominadas']:
            pesos.append(PESO_DOMINADA)
        else:
            pesos.append(max(1, 1 + 3 * mal - ok))

    elegidas = []
    pool = list(zip(pool, pesos))
    for _ in range(min(n, len(pool))):
        i = random.choices(range(len(pool)), weights=[w for _, w in pool], k=1)[0]
        elegidas.append(pool.pop(i)[0])
    return elegidas


def elegir_palabra(usuario, categoria_slug=None):
    elegidas = elegir_palabras(usuario, categoria_slug, 1)
    return elegidas[0] if elegidas else None


# ---------------------------------------------------------------- dictado de frases

UMBRAL_FRASE = 90  # % de palabras correctas para dar la frase por buena


def _palabras(texto):
    texto = texto.lower().replace('’', "'")
    return re.findall(r"[a-z0-9]+(?:'[a-z]+)?", texto)


def comparar_frase(esperada, respuesta):
    """Compara palabra por palabra, sin importar mayúsculas ni puntuación.

    Devuelve el puntaje (0-100) y las palabras esperadas marcadas como ok o mal. Las palabras de más
    también restan: el puntaje divide entre el mayor de los dos largos.
    """
    esp, resp = _palabras(esperada), _palabras(respuesta)
    marcas = ['mal'] * len(esp)
    for tag, i1, i2, _, _ in SequenceMatcher(None, esp, resp, autojunk=False).get_opcodes():
        if tag == 'equal':
            marcas[i1:i2] = ['ok'] * (i2 - i1)
    aciertos = marcas.count('ok')
    largo = max(len(esp), len(resp))
    puntaje = round(100 * aciertos / largo) if largo else 0
    return {
        'puntaje': puntaje,
        'correcto': puntaje >= UMBRAL_FRASE,
        'palabras': [{'texto': p, 'estado': m} for p, m in zip(esp, marcas)],
    }


def elegir_frase(usuario, tema=None):
    """Elige una frase al azar; pesa más las falladas y menos las ya dominadas."""
    frases = Frase.objects.all()
    if tema:
        frases = frases.filter(tema=tema)
    frases = list(frases)
    if not frases:
        return None
    filas = (
        Intento.objects.filter(usuario=usuario, frase__in=frases)
        .values('frase')
        .annotate(ok=Count('id', filter=Q(correcto=True)), mal=Count('id', filter=Q(correcto=False)))
    )
    por_frase = {f['frase']: (f['ok'], f['mal']) for f in filas}
    pesos = []
    for f in frases:
        ok, mal = por_frase.get(f.id, (0, 0))
        pesos.append(max(0.3, 1 + 2 * mal - ok))
    return random.choices(frases, weights=pesos, k=1)[0]


# ---------------------------------------------------------------- práctica oral

def elegir_pregunta(usuario, tema=None, excluir=None):
    """Elige entre las preguntas que el usuario menos ha practicado (al azar si hay empate)."""
    preguntas = PreguntaOral.objects.all()
    if tema:
        preguntas = preguntas.filter(tema=tema)
    if excluir is not None:
        preguntas = preguntas.exclude(pk=excluir)
    cantidades = dict(
        RegistroOral.objects.filter(usuario=usuario).values_list('pregunta').annotate(n=Count('id'))
    )
    preguntas = list(preguntas)
    if not preguntas:
        return None
    minimo = min(cantidades.get(p.id, 0) for p in preguntas)
    return random.choice([p for p in preguntas if cantidades.get(p.id, 0) == minimo])


def resumen_oral(usuario):
    registros = RegistroOral.objects.filter(usuario=usuario)
    total = registros.count()
    if not total:
        return {'total': 0}
    recientes = list(registros[:5].values_list('autoevaluacion', flat=True))
    anteriores = list(registros[5:10].values_list('autoevaluacion', flat=True))
    return {
        'total': total,
        'minutos': round(sum(registros.values_list('duracion_seg', flat=True)) / 60),
        'dias': registros.annotate(dia=TruncDate('creado')).values('dia').distinct().count(),
        'promedio': round(sum(recientes) / len(recientes), 1),
        'promedio_anterior': round(sum(anteriores) / len(anteriores), 1) if anteriores else None,
    }


# ---------------------------------------------------------------- rachas y resumen

def racha(usuario):
    """Días consecutivos con práctica (de cualquier tipo), contando hasta hoy (o ayer si hoy aún no practicó)."""
    dias = set(
        Intento.objects.filter(usuario=usuario)
        .annotate(dia=TruncDate('creado'))
        .values_list('dia', flat=True)
        .distinct()
    ) | set(
        RegistroOral.objects.filter(usuario=usuario)
        .annotate(dia=TruncDate('creado'))
        .values_list('dia', flat=True)
        .distinct()
    )
    dia = timezone.localdate()
    if dia not in dias:
        dia -= timedelta(days=1)
    total = 0
    while dia in dias:
        total += 1
        dia -= timedelta(days=1)
    return total


def resumen(usuario):
    intentos = Intento.objects.filter(usuario=usuario)
    total = intentos.count()
    aciertos = intentos.filter(correcto=True).count()
    hoy = intentos.filter(creado__date=timezone.localdate()).count()
    return {
        'total': total,
        'aciertos': aciertos,
        'porcentaje': round(100 * aciertos / total) if total else 0,
        'hoy': hoy,
        'racha': racha(usuario),
    }
