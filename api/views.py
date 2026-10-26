import math
import random
from datetime import timedelta

from django.contrib.auth.forms import UserCreationForm
from django.core import signing
from django.db.models import Count, Prefetch, Q
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from practica import servicios
from practica.forms import PalabraPropiaForm
from practica.models import Intento, PreguntaOral, RegistroOral
from verbos.models import TIEMPOS, Verbo
from vocabulario.models import Categoria, Frase, Palabra

TARJETAS_POR_SESION = 20
DIAS_ACTIVIDAD = 30
SAL_EJERCICIO = 'ejercicio-verbo'
VIGENCIA_EJERCICIO = 60 * 60


# ---------------------------------------------------------------- serialización

def _perfil(perfil):
    return {
        'nivel_inicial': perfil.nivel_inicial,
        'vocab_estimado': perfil.vocab_estimado,
        'test_fecha': perfil.test_fecha,
        'detalle': perfil.detalle,
        'errores': perfil.errores,
    }


def _estado(est):
    """El estado de práctica sin los objetos internos (stats, ids) que solo usa el servidor."""
    publico = {k: v for k, v in est.items() if k not in ('perfil', 'stats', 'ids_dominadas')}
    publico['perfil'] = _perfil(est['perfil'])
    publico['etiqueta'] = servicios.etiqueta_nivel(est['perfil'].vocab_estimado)
    return publico


def _actividad(usuario):
    """Respuestas y aciertos por día de los últimos DIAS_ACTIVIDAD días, con ceros en los días sin práctica."""
    hoy = timezone.localdate()
    desde = hoy - timedelta(days=DIAS_ACTIVIDAD - 1)
    filas = (
        Intento.objects.filter(usuario=usuario, creado__date__gte=desde)
        .annotate(dia=TruncDate('creado'))
        .values('dia')
        .annotate(total=Count('id'), aciertos=Count('id', filter=Q(correcto=True)))
    )
    por_dia = {f['dia']: f for f in filas}
    dias = []
    for i in range(DIAS_ACTIVIDAD):
        dia = desde + timedelta(days=i)
        f = por_dia.get(dia)
        total = f['total'] if f else 0
        aciertos = f['aciertos'] if f else 0
        dias.append({'fecha': dia.isoformat(), 'total': total, 'aciertos': aciertos, 'fallos': total - aciertos})
    return dias


def _bloques(est):
    """Dominio de cada bloque del núcleo: lo asumido por el test de nivel cuenta como dominado."""
    nivel_inicial = est['perfil'].nivel_inicial
    oficiales = Palabra.objects.oficiales().filter(nivel__isnull=False)
    tamanos = dict(oficiales.values_list('nivel').annotate(n=Count('id')))
    practicadas = dict(oficiales.filter(id__in=est['ids_dominadas']).values_list('nivel').annotate(n=Count('id')))
    bloques = []
    for numero in sorted(tamanos):
        asumido = numero < nivel_inicial
        dominadas = tamanos[numero] if asumido else practicadas.get(numero, 0)
        bloques.append({
            'numero': numero, 'total': tamanos[numero], 'dominadas': dominadas, 'asumido': asumido,
            'porcentaje': round(100 * dominadas / tamanos[numero]),
        })
    return bloques


def _palabra(p):
    return {'id': p.id, 'ingles': p.ingles, 'espanol': p.espanol, 'ejemplo': p.ejemplo}


def _pregunta(p):
    return {
        'id': p.id, 'tema': p.tema, 'tema_display': p.get_tema_display(), 'texto': p.texto,
        'traduccion': p.traduccion, 'estructura': p.estructura, 'modelo': p.modelo,
        'frases_utiles': p.lista_frases(),
    }


def _categoria(c):
    return {'nombre': c.nombre, 'slug': c.slug}


def _opciones(choices):
    return [{'clave': c, 'nombre': n} for c, n in choices]


# ---------------------------------------------------------------- cuenta

@api_view(['GET'])
@permission_classes([AllowAny])
def salud(request):
    """Para los healthchecks de Docker y Render: responde sin login y sin tocar la base de datos."""
    return Response({'ok': True})


@api_view(['POST'])
@permission_classes([AllowAny])
def registro(request):
    form = UserCreationForm(request.data)
    if not form.is_valid():
        return Response({'errores': form.errors.get_json_data()}, status=status.HTTP_400_BAD_REQUEST)
    token = RefreshToken.for_user(form.save())
    return Response({'access': str(token.access_token), 'refresh': str(token)}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def yo(request):
    return Response({'username': request.user.username, 'is_staff': request.user.is_staff})


# ---------------------------------------------------------------- inicio y nivel

@api_view(['GET'])
def inicio(request):
    est = servicios.estado(request.user)
    return Response({
        'resumen': servicios.resumen(request.user),
        'estado': _estado(est),
        'actividad': _actividad(request.user),
        'bloques': _bloques(est),
        'resumen_oral': servicios.resumen_oral(request.user),
        'categorias': [_categoria(c) for c in Categoria.objects.filter(es_tecnica=False)],
        'categorias_tech': [_categoria(c) for c in Categoria.objects.filter(es_tecnica=True)],
        'tiempos': _opciones(TIEMPOS),
    })


@api_view(['GET'])
def nivel_intro(request):
    est = servicios.estado(request.user)
    return Response({
        'perfil': _perfil(est['perfil']),
        'preguntas_total': servicios.BLOQUES * servicios.PREGUNTAS_POR_BLOQUE,
    })


@api_view(['GET', 'POST'])
def nivel_test(request):
    if request.method == 'POST':
        respuestas = request.data.get('respuestas')
        if not isinstance(respuestas, list) or not respuestas:
            return Response({'ok': False}, status=status.HTTP_400_BAD_REQUEST)
        servicios.guardar_nivel(request.user, servicios.evaluar_nivel(respuestas))
        return Response({'ok': True})
    return Response({'preguntas': servicios.construir_test()})


@api_view(['GET'])
def nivel_resultado(request):
    est = servicios.estado(request.user)
    perfil = est['perfil']
    if perfil.test_fecha is None:
        return Response({'detail': 'Aún no haces el test.'}, status=status.HTTP_404_NOT_FOUND)
    bloques = [{'numero': int(n), **d} for n, d in sorted(perfil.detalle.items(), key=lambda kv: int(kv[0]))]
    return Response({
        'estado': _estado(est),
        'bloques': bloques,
        'errores': perfil.errores,
        'completo': perfil.nivel_inicial > est['ultimo_bloque'],
    })


@api_view(['GET'])
def consejos(request):
    est = servicios.estado(request.user)
    faltan = max(0, est['meta'] - est['total'])
    return Response({
        'estado': _estado(est),
        'faltan': faltan,
        'plan': [{'por_dia': n, 'dias': math.ceil(faltan / n)} for n in (5, 10, 15)],
    })


# ---------------------------------------------------------------- palabras propias

@api_view(['GET', 'POST'])
def mis_palabras(request):
    est = servicios.estado(request.user)
    puede_agregar = est['desbloqueado'] or request.user.is_staff

    if request.method == 'POST':
        if not puede_agregar:
            return Response({'detail': 'Aún no se desbloquea esta función.'}, status=status.HTTP_403_FORBIDDEN)
        form = PalabraPropiaForm(request.data, usuario=request.user)
        if not form.is_valid():
            return Response({'errores': form.errors.get_json_data()}, status=status.HTTP_400_BAD_REQUEST)
        categoria, _ = Categoria.objects.get_or_create(slug='mis-palabras', defaults={'nombre': 'Mis palabras'})
        palabra = form.save(commit=False)
        palabra.propietario = request.user
        palabra.categoria = categoria
        palabra.save()
        return Response(_palabra(palabra), status=status.HTTP_201_CREATED)

    return Response({
        'estado': _estado(est),
        'puede_agregar': puede_agregar,
        'palabras': [_palabra(p) for p in Palabra.objects.filter(propietario=request.user).order_by('-id')],
    })


@api_view(['DELETE'])
def borrar_palabra(request, pk):
    get_object_or_404(Palabra, pk=pk, propietario=request.user).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------- práctica

@api_view(['GET'])
def tarjetas(request):
    categoria = request.query_params.get('categoria') or None
    palabras = servicios.elegir_palabras(request.user, categoria, TARJETAS_POR_SESION)
    random.shuffle(palabras)
    return Response({'palabras': [_palabra(p) for p in palabras]})


@api_view(['POST'])
def registrar_tarjeta(request):
    palabra = Palabra.objects.visibles(request.user).filter(pk=request.data.get('palabra_id')).first()
    if palabra is None:
        return Response({'ok': False}, status=status.HTTP_404_NOT_FOUND)
    Intento.objects.create(
        usuario=request.user, tipo='tarjeta', palabra=palabra, correcto=bool(request.data.get('correcto')),
    )
    return Response({'ok': True})


@api_view(['GET', 'POST'])
def quiz_vocab(request):
    """modo=traducir (español → inglés) o modo=dictado (audio → inglés).

    GET devuelve una palabra; POST recibe {palabra_id, modo, respuesta} y corrige. En modo dictado el GET incluye
    el inglés porque el navegador lo necesita para pronunciarlo.
    """
    if request.method == 'POST':
        palabra = Palabra.objects.visibles(request.user).filter(pk=request.data.get('palabra_id')).first()
        if palabra is None:
            return Response({'ok': False}, status=status.HTTP_404_NOT_FOUND)
        respuesta = str(request.data.get('respuesta', ''))
        correcto = servicios.normalizar(respuesta) == servicios.normalizar(palabra.ingles)
        Intento.objects.create(
            usuario=request.user, tipo='dictado' if request.data.get('modo') == 'dictado' else 'vocab',
            palabra=palabra, respuesta=respuesta[:120], correcto=correcto,
        )
        return Response({'correcto': correcto, 'palabra': _palabra(palabra)})

    palabra = servicios.elegir_palabra(request.user, request.query_params.get('categoria') or None)
    if palabra is None:
        return Response({'vacio': True})
    if request.query_params.get('modo') == 'dictado':
        return Response({'palabra': {'id': palabra.id, 'ingles': palabra.ingles}})
    return Response({'palabra': {'id': palabra.id, 'espanol': palabra.espanol}})


@api_view(['GET', 'POST'])
def quiz_verbos(request):
    """GET devuelve un ejercicio con un `ticket` firmado que guarda las respuestas válidas; POST lo devuelve."""
    if request.method == 'POST':
        try:
            actual = signing.loads(request.data.get('ticket', ''), salt=SAL_EJERCICIO, max_age=VIGENCIA_EJERCICIO)
        except signing.BadSignature:
            return Response({'detail': 'Ejercicio inválido o vencido.'}, status=status.HTTP_400_BAD_REQUEST)
        verbo = get_object_or_404(Verbo, pk=actual['verbo_id'])
        respuesta = str(request.data.get('respuesta', ''))
        validas = actual['respuestas']
        correcto = servicios.normalizar(respuesta) in [servicios.normalizar(v) for v in validas]
        Intento.objects.create(
            usuario=request.user, tipo='verbo', verbo=verbo, tiempo=actual['tiempo'],
            respuesta=respuesta[:120], correcto=correcto,
        )
        return Response({
            'correcto': correcto, 'correcta': validas[0], 'enunciado': actual['enunciado'], 'pista': actual['pista'],
            'verbo': {'infinitivo': verbo.infinitivo, 'espanol': verbo.espanol},
        })

    tiempo = request.query_params.get('tiempo') or 'pasado'
    if tiempo not in dict(TIEMPOS):
        tiempo = 'pasado'
    verbos = list(Verbo.objects.filter(ejercitable=True))
    if not verbos:
        return Response({'vacio': True})
    verbo = random.choice(verbos)
    ej = verbo.ejercicio(tiempo)
    ticket = signing.dumps({
        'verbo_id': verbo.id, 'tiempo': tiempo, 'respuestas': ej['respuestas'],
        'enunciado': ej['enunciado'], 'pista': ej['pista'],
    }, salt=SAL_EJERCICIO)
    return Response({
        'tiempo': tiempo, 'ticket': ticket, 'enunciado': ej['enunciado'], 'pista': ej['pista'],
        'verbo': {'infinitivo': verbo.infinitivo, 'espanol': verbo.espanol},
    })


@api_view(['GET', 'POST'])
def dictado_frases(request):
    """GET devuelve una frase (el navegador la necesita para pronunciarla); POST recibe {frase_id, respuesta}."""
    if request.method == 'POST':
        frase = Frase.objects.filter(pk=request.data.get('frase_id')).first()
        if frase is None:
            return Response({'ok': False}, status=status.HTTP_404_NOT_FOUND)
        respuesta = str(request.data.get('respuesta', ''))
        comparacion = servicios.comparar_frase(frase.texto, respuesta)
        Intento.objects.create(
            usuario=request.user, tipo='frase', frase=frase, respuesta=respuesta[:250],
            puntaje=comparacion['puntaje'], correcto=comparacion['correcto'],
        )
        return Response({**comparacion, 'frase': {'texto': frase.texto, 'traduccion': frase.traduccion}})

    tema = request.query_params.get('tema') or ''
    if tema not in dict(Frase.TEMAS):
        tema = ''
    frase = servicios.elegir_frase(request.user, tema or None)
    return Response({
        'temas': _opciones(Frase.TEMAS),
        'tema': tema,
        'frase': {'id': frase.id, 'texto': frase.texto} if frase else None,
    })


# ---------------------------------------------------------------- práctica oral

@api_view(['GET'])
def oral(request):
    """Elige una pregunta. `excluir` evita repetir la anterior al pedir «otra»; la pregunta del día la recuerda el cliente."""
    tema = request.query_params.get('tema', '')
    if tema not in dict(PreguntaOral.TEMAS):
        tema = ''
    excluir = request.query_params.get('excluir')
    excluir = int(excluir) if excluir and excluir.isdigit() else None
    pregunta = servicios.elegir_pregunta(request.user, tema or None, excluir=excluir)
    if pregunta is None:  # solo hay una pregunta en ese tema
        pregunta = servicios.elegir_pregunta(request.user, tema or None)
    return Response({
        'tema': tema,
        'temas': _opciones(PreguntaOral.TEMAS),
        'pregunta': _pregunta(pregunta) if pregunta else None,
        'hoy_hecho': _hecha_hoy(request.user, pregunta),
        'resumen_oral': servicios.resumen_oral(request.user),
    })


@api_view(['GET'])
def oral_pregunta(request, pk):
    """Recupera la pregunta del día que el cliente ya tenía guardada."""
    pregunta = get_object_or_404(PreguntaOral, pk=pk)
    return Response({
        'temas': _opciones(PreguntaOral.TEMAS),
        'pregunta': _pregunta(pregunta),
        'hoy_hecho': _hecha_hoy(request.user, pregunta),
        'resumen_oral': servicios.resumen_oral(request.user),
    })


def _hecha_hoy(usuario, pregunta):
    if pregunta is None:
        return False
    return RegistroOral.objects.filter(
        usuario=usuario, pregunta=pregunta, creado__date=timezone.localdate(),
    ).exists()


@api_view(['POST'])
def oral_registrar(request):
    pregunta = get_object_or_404(PreguntaOral, pk=request.data.get('pregunta_id'))
    try:
        nota = int(request.data.get('autoevaluacion', ''))
        duracion = max(0, min(int(request.data.get('duracion') or 0), 3600))
    except (TypeError, ValueError):
        nota, duracion = 0, 0
    if not 1 <= nota <= 5:
        return Response({'detail': 'Elige una calificación de 1 a 5.'}, status=status.HTTP_400_BAD_REQUEST)
    RegistroOral.objects.create(
        usuario=request.user, pregunta=pregunta, duracion_seg=duracion,
        autoevaluacion=nota, notas=str(request.data.get('notas', ''))[:300],
    )
    return Response({'ok': True}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def oral_historial(request):
    registros = RegistroOral.objects.filter(usuario=request.user).select_related('pregunta')[:30]
    return Response({
        'registros': [{
            'id': r.id, 'pregunta': r.pregunta.texto, 'tema_display': r.pregunta.get_tema_display(),
            'duracion_seg': r.duracion_seg, 'autoevaluacion': r.autoevaluacion, 'notas': r.notas, 'creado': r.creado,
        } for r in registros],
        'resumen_oral': servicios.resumen_oral(request.user),
    })


# ---------------------------------------------------------------- progreso y listas

@api_view(['GET'])
def progreso(request):
    usuario = request.user
    fallos_palabras = (
        Palabra.objects.filter(intento__usuario=usuario)
        .annotate(mal=Count('intento', filter=Q(intento__usuario=usuario, intento__correcto=False)))
        .filter(mal__gt=0).order_by('-mal')[:10]
    )
    fallos_verbos = (
        Verbo.objects.filter(intento__usuario=usuario)
        .annotate(mal=Count('intento', filter=Q(intento__usuario=usuario, intento__correcto=False)))
        .filter(mal__gt=0).order_by('-mal')[:10]
    )
    por_tipo = []
    for clave, nombre in Intento.TIPOS:
        qs = Intento.objects.filter(usuario=usuario, tipo=clave)
        total = qs.count()
        if total:
            aciertos = qs.filter(correcto=True).count()
            por_tipo.append({'nombre': nombre, 'total': total, 'porcentaje': round(100 * aciertos / total)})
    est = servicios.estado(usuario)
    return Response({
        'resumen': servicios.resumen(usuario),
        'estado': _estado(est),
        'actividad': _actividad(usuario),
        'bloques': _bloques(est),
        'resumen_oral': servicios.resumen_oral(usuario),
        'fallos_palabras': [{'ingles': p.ingles, 'espanol': p.espanol, 'mal': p.mal} for p in fallos_palabras],
        'fallos_verbos': [{
            'infinitivo': v.infinitivo, 'pasado': v.pasado, 'participio': v.participio, 'mal': v.mal,
        } for v in fallos_verbos],
        'por_tipo': por_tipo,
    })


@api_view(['GET'])
def vocabulario(request):
    visibles = Palabra.objects.visibles(request.user)
    categorias = Categoria.objects.prefetch_related(Prefetch('palabras', queryset=visibles, to_attr='visibles'))
    return Response({'categorias': [
        {**_categoria(c), 'palabras': [_palabra(p) for p in c.visibles]} for c in categorias if c.visibles
    ]})


@api_view(['GET'])
def verbos(request):
    return Response({'verbos': [{
        'infinitivo': v.infinitivo, 'espanol': v.espanol, 'tercera_persona': v.tercera_persona,
        'pasado': v.pasado, 'participio': v.participio, 'irregular': v.irregular,
    } for v in Verbo.objects.all()]})
