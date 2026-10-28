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

# Examen adaptativo: se sube de nivel al acertar EXAMEN_ACIERTOS y termina al fallar EXAMEN_FALLOS en un mismo nivel.
EXAMEN_ACIERTOS = 4
EXAMEN_FALLOS = 2

# Práctica con dificultad creciente (quiz de vocabulario): sube con una racha de aciertos, baja con una de fallos.
QUIZ_RACHA_SUBE = 3
QUIZ_RACHA_BAJA = 2
QUIZ_PREGUNTAS = 20

NOMBRES_NIVEL = {
    1: 'Inicial', 2: 'Básico', 3: 'Elemental', 4: 'Pre-intermedio', 5: 'Intermedio',
    6: 'Intermedio alto', 7: 'Avanzado bajo', 8: 'Avanzado', 9: 'Superior', 10: 'Experto',
}
# Equivalencia aproximada con el Marco Común Europeo; los bloques no están calibrados con él.
CEFR_NIVEL = {1: 'A1', 2: 'A1', 3: 'A2', 4: 'A2', 5: 'B1', 6: 'B1', 7: 'B2', 8: 'B2', 9: 'C1', 10: 'C2'}


def niveles():
    return [{'numero': n, 'nombre': NOMBRES_NIVEL[n], 'cefr': CEFR_NIVEL[n]} for n in range(1, BLOQUES + 1)]


def normalizar(texto):
    return ' '.join(texto.lower().split())


# ---------------------------------------------------------------- test de nivel

def _agrupar_por_bloque():
    por_bloque = defaultdict(list)
    for p in Palabra.objects.oficiales().filter(nivel__isnull=False):
        por_bloque[p.nivel].append(p)
    return por_bloque


def _armar_pregunta(palabra, por_bloque):
    """Pregunta de opción múltiple (inglés → español) con distractores de los bloques vecinos."""
    bloque = palabra.nivel
    vecinas = por_bloque.get(bloque - 1, []) + por_bloque.get(bloque, []) + por_bloque.get(bloque + 1, [])
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
    return {
        'id': palabra.id,
        'ingles': palabra.ingles,
        'opciones': [{'id': o.id, 'espanol': o.espanol} for o in opciones],
    }


def construir_test():
    """Elige PREGUNTAS_POR_BLOQUE palabras por bloque, con opciones de bloques vecinos como distractores."""
    por_bloque = _agrupar_por_bloque()
    preguntas = []
    for bloque in range(1, BLOQUES + 1):
        palabras = por_bloque.get(bloque, [])
        for palabra in random.sample(palabras, min(PREGUNTAS_POR_BLOQUE, len(palabras))):
            preguntas.append(_armar_pregunta(palabra, por_bloque))
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


# ---------------------------------------------------------------- examen adaptativo

def _repetir_examen(historial):
    """Reconstruye el examen desde el historial de respuestas. El servidor corrige todo; el cliente solo manda ids.

    Se empieza en el nivel más bajo. En cada nivel se aprueba con EXAMEN_ACIERTOS aciertos y se reprueba con
    EXAMEN_FALLOS fallos; al reprobar, el examen termina y ese es el nivel del usuario.
    """
    entradas = [r for r in historial if isinstance(r, dict)]
    palabras = {
        p.id: p for p in Palabra.objects.oficiales().filter(
            id__in=[r['palabra_id'] for r in entradas if isinstance(r.get('palabra_id'), int)], nivel__isnull=False,
        )
    }
    espanol_de = dict(Palabra.objects.filter(
        id__in=[r['elegida_id'] for r in entradas if isinstance(r.get('elegida_id'), int)],
    ).values_list('id', 'espanol'))

    tamanos = dict(Palabra.objects.oficiales().filter(nivel__isnull=False).values_list('nivel').annotate(n=Count('id')))
    orden = sorted(tamanos)
    detalle = {n: {'aciertos': 0, 'total': 0, 'aprobado': False} for n in orden}
    errores, vistas = [], set()
    posicion, terminado = 0, not orden

    for r in entradas:
        if terminado:
            break
        nivel = orden[posicion]
        palabra = palabras.get(r.get('palabra_id'))
        if palabra is None or palabra.id in vistas or palabra.nivel != nivel:
            continue
        vistas.add(palabra.id)
        cuenta = detalle[nivel]
        cuenta['total'] += 1
        if r.get('elegida_id') == palabra.id:
            cuenta['aciertos'] += 1
        else:
            errores.append({
                'bloque': nivel, 'ingles': palabra.ingles, 'correcta': palabra.espanol,
                'elegida': espanol_de.get(r.get('elegida_id')),  # None = "No la sé"
            })
        if cuenta['aciertos'] >= EXAMEN_ACIERTOS:
            cuenta['aprobado'] = True
            posicion += 1
            terminado = posicion >= len(orden)
        elif cuenta['total'] - cuenta['aciertos'] >= EXAMEN_FALLOS:
            terminado = True

    return {
        'orden': orden, 'tamanos': tamanos, 'detalle': detalle, 'errores': errores, 'vistas': vistas,
        'posicion': posicion, 'nivel': orden[min(posicion, len(orden) - 1)] if orden else 0, 'terminado': terminado,
    }


def _resultado_examen(estado):
    """Un nivel aprobado cuenta completo en el vocabulario estimado; el que se reprobó, según su precisión sin azar."""
    detalle, estimado, nivel_inicial = {}, 0.0, None
    for nivel in estado['orden']:
        cuenta = estado['detalle'][nivel]
        precision = cuenta['aciertos'] / cuenta['total'] if cuenta['total'] else 0
        dominio = max(0.0, (precision - PROBABILIDAD_AZAR) / (1 - PROBABILIDAD_AZAR))
        detalle[str(nivel)] = {
            'aciertos': cuenta['aciertos'], 'total': cuenta['total'],
            'dominio': round(dominio * 100), 'aprobado': cuenta['aprobado'],
        }
        estimado += estado['tamanos'][nivel] if cuenta['aprobado'] else dominio * estado['tamanos'][nivel]
        if nivel_inicial is None and not cuenta['aprobado']:
            nivel_inicial = nivel
    if nivel_inicial is None:
        nivel_inicial = max(estado['orden'], default=0) + 1  # aprobó todo el núcleo
    return {
        'vocab_estimado': round(estimado), 'nivel_inicial': nivel_inicial,
        'detalle': detalle, 'errores': estado['errores'],
    }


def paso_examen(historial):
    """Dado el historial devuelve la siguiente pregunta con su progreso, o el resultado si el examen terminó."""
    estado = _repetir_examen(historial)
    nivel = estado['nivel']
    por_bloque = _agrupar_por_bloque()
    candidatas = [p for p in por_bloque.get(nivel, []) if p.id not in estado['vistas']]
    # Si el nivel se quedó sin palabras sin decidirse, el examen se cierra ahí.
    if estado['terminado'] or not candidatas:
        return {'terminado': True, 'resultado': _resultado_examen(estado)}

    cuenta = estado['detalle'][nivel]
    return {
        'terminado': False,
        'pregunta': _armar_pregunta(random.choice(candidatas), por_bloque),
        'progreso': {
            'nivel': nivel,
            'niveles': niveles(),
            'aprobados': estado['posicion'],
            'aciertos_nivel': cuenta['aciertos'],
            'fallos_nivel': cuenta['total'] - cuenta['aciertos'],
            'necesarios': EXAMEN_ACIERTOS,
            'max_fallos': EXAMEN_FALLOS,
            'respondidas': len(estado['vistas']),
            'avance': round(100 * (estado['posicion'] + cuenta['aciertos'] / EXAMEN_ACIERTOS) / len(estado['orden'])),
        },
    }


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

def elegir_palabras(usuario, categoria_slug=None, n=1, nivel=None):
    """Elige n palabras distintas, con más peso a las que se fallan y menos a las dominadas.

    Sin categoría se trabaja el bloque activo del usuario (más las palabras temáticas y propias).
    El vocabulario técnico solo aparece cuando se elige su categoría. Con `nivel` solo salen palabras de ese bloque.
    """
    est = estado(usuario)
    candidatas = Palabra.objects.visibles(usuario)
    if categoria_slug:
        candidatas = candidatas.filter(categoria__slug=categoria_slug)
    elif nivel:
        candidatas = candidatas.filter(nivel=nivel, propietario__isnull=True).exclude(categoria__es_tecnica=True)
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


def elegir_palabra(usuario, categoria_slug=None, nivel=None):
    elegidas = elegir_palabras(usuario, categoria_slug, 1, nivel)
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
