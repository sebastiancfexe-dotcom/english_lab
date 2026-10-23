import json
import math
import random

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from verbos.models import TIEMPOS, Verbo
from vocabulario.models import Categoria, Frase, Palabra

from . import servicios
from .forms import PalabraPropiaForm
from .models import Intento, PreguntaOral, RegistroOral

TARJETAS_POR_SESION = 20


@login_required
def inicio(request):
    est = servicios.estado(request.user)
    return render(request, 'practica/inicio.html', {
        'resumen': servicios.resumen(request.user),
        'estado': est,
        'perfil': est['perfil'],
        'etiqueta': servicios.etiqueta_nivel(est['perfil'].vocab_estimado),
        'categorias': Categoria.objects.filter(es_tecnica=False),
        'categorias_tech': Categoria.objects.filter(es_tecnica=True),
        'tiempos': TIEMPOS,
    })


# ---------------------------------------------------------------- test de nivel

@login_required
def nivel_intro(request):
    perfil = servicios.estado(request.user)['perfil']
    return render(request, 'practica/nivel_intro.html', {
        'perfil': perfil,
        'preguntas_total': servicios.BLOQUES * servicios.PREGUNTAS_POR_BLOQUE,
    })


@login_required
def nivel_test(request):
    if request.method == 'POST':
        try:
            respuestas = json.loads(request.body or '{}').get('respuestas', [])
        except (ValueError, AttributeError):
            return JsonResponse({'ok': False}, status=400)
        if not isinstance(respuestas, list) or not respuestas:
            return JsonResponse({'ok': False}, status=400)
        servicios.guardar_nivel(request.user, servicios.evaluar_nivel(respuestas))
        return JsonResponse({'ok': True, 'siguiente': reverse('nivel_resultado')})

    preguntas = servicios.construir_test()
    return render(request, 'practica/nivel_test.html', {'preguntas': preguntas})


@login_required
def nivel_resultado(request):
    est = servicios.estado(request.user)
    perfil = est['perfil']
    if perfil.test_fecha is None:
        return redirect('nivel_intro')
    bloques = [
        {'numero': int(n), **d} for n, d in sorted(perfil.detalle.items(), key=lambda kv: int(kv[0]))
    ]
    return render(request, 'practica/nivel_resultado.html', {
        'estado': est,
        'perfil': perfil,
        'etiqueta': servicios.etiqueta_nivel(perfil.vocab_estimado),
        'bloques': bloques,
        'errores': perfil.errores,
        'completo': perfil.nivel_inicial > est['ultimo_bloque'],
    })


# ---------------------------------------------------------------- consejos y palabras propias

@login_required
def consejos(request):
    est = servicios.estado(request.user)
    faltan = max(0, est['meta'] - est['total'])
    plan = [{'por_dia': n, 'dias': math.ceil(faltan / n)} for n in (5, 10, 15)]
    return render(request, 'practica/consejos.html', {
        'estado': est,
        'perfil': est['perfil'],
        'etiqueta': servicios.etiqueta_nivel(est['perfil'].vocab_estimado),
        'faltan': faltan,
        'plan': plan,
    })


@login_required
def mis_palabras(request):
    est = servicios.estado(request.user)
    puede_agregar = est['desbloqueado'] or request.user.is_staff
    form = PalabraPropiaForm(request.POST or None, usuario=request.user)

    if request.method == 'POST':
        if not puede_agregar:
            messages.error(request, 'Aún no se desbloquea esta función.')
            return redirect('mis_palabras')
        if form.is_valid():
            categoria, _ = Categoria.objects.get_or_create(slug='mis-palabras', defaults={'nombre': 'Mis palabras'})
            palabra = form.save(commit=False)
            palabra.propietario = request.user
            palabra.categoria = categoria
            palabra.save()
            messages.success(request, f'«{palabra.ingles}» agregada.')
            return redirect('mis_palabras')

    return render(request, 'practica/mis_palabras.html', {
        'estado': est,
        'puede_agregar': puede_agregar,
        'form': form,
        'palabras': Palabra.objects.filter(propietario=request.user).order_by('-id'),
    })


@login_required
@require_POST
def borrar_palabra(request, pk):
    get_object_or_404(Palabra, pk=pk, propietario=request.user).delete()
    return redirect('mis_palabras')


# ---------------------------------------------------------------- práctica

@login_required
def tarjetas(request):
    slug = request.GET.get('categoria')
    palabras = servicios.elegir_palabras(request.user, slug or None, TARJETAS_POR_SESION)
    datos = [{'id': p.id, 'ingles': p.ingles, 'espanol': p.espanol, 'ejemplo': p.ejemplo} for p in palabras]
    random.shuffle(datos)
    return render(request, 'practica/tarjetas.html', {'palabras': datos, 'categoria': slug})


@login_required
@require_POST
def registrar_tarjeta(request):
    cuerpo = json.loads(request.body or '{}')
    palabra = Palabra.objects.visibles(request.user).filter(pk=cuerpo.get('palabra_id')).first()
    if palabra is None:
        return JsonResponse({'ok': False}, status=404)
    Intento.objects.create(
        usuario=request.user, tipo='tarjeta', palabra=palabra, correcto=bool(cuerpo.get('correcto')),
    )
    return JsonResponse({'ok': True})


@login_required
def quiz_vocab(request):
    """Quiz de vocabulario. modo=traducir (español → inglés) o modo=dictado (audio → inglés)."""
    modo = request.GET.get('modo') or request.POST.get('modo') or 'traducir'
    slug = request.GET.get('categoria') or request.POST.get('categoria') or ''
    contexto = {'modo': modo, 'categoria': slug}

    if request.method == 'POST':
        palabra = Palabra.objects.visibles(request.user).filter(pk=request.session.get('palabra_actual')).first()
        if palabra is not None:
            respuesta = request.POST.get('respuesta', '')
            correcto = servicios.normalizar(respuesta) == servicios.normalizar(palabra.ingles)
            Intento.objects.create(
                usuario=request.user,
                tipo='dictado' if modo == 'dictado' else 'vocab',
                palabra=palabra,
                respuesta=respuesta[:120],
                correcto=correcto,
            )
            contexto.update(palabra=palabra, correcto=correcto, respuesta=respuesta, resuelto=True)
            return render(request, 'practica/quiz_vocab.html', contexto)

    palabra = servicios.elegir_palabra(request.user, slug or None)
    if palabra is None:
        return render(request, 'practica/quiz_vocab.html', {**contexto, 'vacio': True})
    request.session['palabra_actual'] = palabra.id
    contexto['palabra'] = palabra
    return render(request, 'practica/quiz_vocab.html', contexto)


@login_required
def dictado_frases(request):
    """Escuchas una frase completa y la escribes. Se compara palabra por palabra."""
    tema = request.GET.get('tema') or request.POST.get('tema') or ''
    if tema not in dict(Frase.TEMAS):
        tema = ''
    contexto = {'tema': tema, 'temas': Frase.TEMAS}

    if request.method == 'POST':
        frase = Frase.objects.filter(pk=request.session.get('frase_actual')).first()
        if frase is not None:
            respuesta = request.POST.get('respuesta', '')
            comparacion = servicios.comparar_frase(frase.texto, respuesta)
            Intento.objects.create(
                usuario=request.user, tipo='frase', frase=frase, respuesta=respuesta[:250],
                puntaje=comparacion['puntaje'], correcto=comparacion['correcto'],
            )
            contexto.update(frase=frase, resuelto=True, respuesta=respuesta, **comparacion)
            return render(request, 'practica/dictado_frases.html', contexto)

    frase = servicios.elegir_frase(request.user, tema or None)
    if frase is None:
        return render(request, 'practica/dictado_frases.html', {**contexto, 'vacio': True})
    request.session['frase_actual'] = frase.id
    contexto['frase'] = frase
    return render(request, 'practica/dictado_frases.html', contexto)


@login_required
def oral(request):
    """Una pregunta por día para responder en voz alta. El audio se queda en el navegador."""
    tema = request.GET.get('tema', '')
    if tema not in dict(PreguntaOral.TEMAS):
        tema = ''
    hoy = timezone.localdate().isoformat()
    guardada = request.session.get('oral_dia') or {}
    pregunta = None
    if guardada.get('fecha') == hoy and guardada.get('tema') == tema and 'otra' not in request.GET:
        pregunta = PreguntaOral.objects.filter(pk=guardada.get('id')).first()
    if pregunta is None:
        pregunta = servicios.elegir_pregunta(request.user, tema or None, excluir=guardada.get('id'))
        if pregunta is None:  # solo hay una pregunta en ese tema
            pregunta = servicios.elegir_pregunta(request.user, tema or None)
        if pregunta is not None:
            request.session['oral_dia'] = {'fecha': hoy, 'id': pregunta.id, 'tema': tema}

    hoy_hecho = RegistroOral.objects.filter(
        usuario=request.user, pregunta=pregunta, creado__date=timezone.localdate(),
    ).exists() if pregunta else False
    return render(request, 'practica/oral.html', {
        'pregunta': pregunta, 'tema': tema, 'temas': PreguntaOral.TEMAS, 'hoy_hecho': hoy_hecho,
        'resumen_oral': servicios.resumen_oral(request.user),
    })


@login_required
@require_POST
def oral_registrar(request):
    pregunta = get_object_or_404(PreguntaOral, pk=request.POST.get('pregunta_id'))
    try:
        nota = int(request.POST.get('autoevaluacion', ''))
        duracion = max(0, min(int(request.POST.get('duracion') or 0), 3600))
    except ValueError:
        nota, duracion = 0, 0
    if not 1 <= nota <= 5:
        messages.error(request, 'Elige una calificación de 1 a 5.')
        return redirect('oral')
    RegistroOral.objects.create(
        usuario=request.user, pregunta=pregunta, duracion_seg=duracion,
        autoevaluacion=nota, notas=request.POST.get('notas', '')[:300],
    )
    messages.success(request, 'Práctica registrada. ¡Buen trabajo!')
    return redirect('oral_historial')


@login_required
def oral_historial(request):
    return render(request, 'practica/oral_historial.html', {
        'registros': RegistroOral.objects.filter(usuario=request.user).select_related('pregunta')[:30],
        'resumen_oral': servicios.resumen_oral(request.user),
    })


@login_required
def quiz_verbos(request):
    tiempo = request.GET.get('tiempo') or request.POST.get('tiempo') or 'pasado'
    if tiempo not in dict(TIEMPOS):
        tiempo = 'pasado'
    contexto = {'tiempo': tiempo, 'tiempos': TIEMPOS}

    if request.method == 'POST':
        actual = request.session.get('ejercicio_actual')
        verbo = Verbo.objects.filter(pk=actual['verbo_id']).first() if actual else None
        if verbo is not None:
            respuesta = request.POST.get('respuesta', '')
            validas = actual['respuestas']
            correcto = servicios.normalizar(respuesta) in [servicios.normalizar(v) for v in validas]
            Intento.objects.create(
                usuario=request.user, tipo='verbo', verbo=verbo, tiempo=actual['tiempo'],
                respuesta=respuesta[:120], correcto=correcto,
            )
            contexto.update(
                verbo=verbo, enunciado=actual['enunciado'], pista=actual['pista'], correcta=validas[0],
                correcto=correcto, respuesta=respuesta, resuelto=True,
            )
            return render(request, 'practica/quiz_verbos.html', contexto)

    verbos = list(Verbo.objects.filter(ejercitable=True))
    if not verbos:
        return render(request, 'practica/quiz_verbos.html', {**contexto, 'vacio': True})
    verbo = random.choice(verbos)
    ej = verbo.ejercicio(tiempo)
    request.session['ejercicio_actual'] = {
        'verbo_id': verbo.id, 'tiempo': tiempo, 'respuestas': ej['respuestas'],
        'enunciado': ej['enunciado'], 'pista': ej['pista'],
    }
    contexto.update(verbo=verbo, enunciado=ej['enunciado'], pista=ej['pista'])
    return render(request, 'practica/quiz_verbos.html', contexto)


@login_required
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
    return render(request, 'practica/progreso.html', {
        'resumen': servicios.resumen(usuario),
        'estado': servicios.estado(usuario),
        'fallos_palabras': fallos_palabras,
        'fallos_verbos': fallos_verbos,
        'por_tipo': por_tipo,
    })
