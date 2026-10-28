from django.contrib.auth import get_user_model
from django.core import signing
from django.core.management import call_command
from rest_framework.test import APITestCase

from api.views import SAL_EJERCICIO
from usuarios.models import Perfil
from verbos.models import Verbo
from vocabulario.models import Palabra

from . import servicios
from .models import Intento


class BaseTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('cargar_datos', verbosity=0)
        cls.user = get_user_model().objects.create_user('ana', password='clave-segura-123')

    def setUp(self):
        self.client.force_authenticate(self.user)


class PracticaTests(BaseTest):
    def test_quiz_vocab_correcto_e_incorrecto(self):
        pregunta = self.client.get('/api/quiz/vocabulario/').data['palabra']
        palabra = Palabra.objects.get(pk=pregunta['id'])
        resp = self.client.post('/api/quiz/vocabulario/', {
            'palabra_id': palabra.id, 'modo': 'traducir', 'respuesta': f'  {palabra.ingles.upper()} ',
        }, format='json')
        self.assertTrue(resp.data['correcto'])
        resp = self.client.post('/api/quiz/vocabulario/', {
            'palabra_id': palabra.id, 'modo': 'traducir', 'respuesta': 'zzz',
        }, format='json')
        self.assertFalse(resp.data['correcto'])
        self.assertEqual(Intento.objects.filter(usuario=self.user).count(), 2)

    def test_quiz_verbos_cada_tiempo(self):
        for tiempo in ['presente', 'pasado', 'futuro']:
            ejercicio = self.client.get('/api/quiz/verbos/', {'tiempo': tiempo}).data
            valida = signing.loads(ejercicio['ticket'], salt=SAL_EJERCICIO)['respuestas'][0]
            resp = self.client.post(
                '/api/quiz/verbos/', {'ticket': ejercicio['ticket'], 'respuesta': valida}, format='json',
            )
            self.assertTrue(resp.data['correcto'], (tiempo, ejercicio))

    def test_ejercicios_por_tiempo(self):
        go = Verbo.objects.get(infinitivo='go')
        self.assertEqual(go.ejercicio('pasado')['respuestas'], ['went'])
        self.assertIn(go.ejercicio('presente')['respuestas'][0], ['go', 'goes'])
        self.assertIn(go.ejercicio('futuro')['respuestas'][0],
                      {'will go', 'am going to go', 'is going to go', 'are going to go'})

    def test_be_no_se_ejercita(self):
        self.assertFalse(Verbo.objects.get(infinitivo='be').ejercitable)

    def test_tarjeta_registra_intento(self):
        p = Palabra.objects.first()
        resp = self.client.post('/api/tarjetas/registrar/', {'palabra_id': p.id, 'correcto': True}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Intento.objects.get(tipo='tarjeta').correcto)

    def test_racha_y_resumen(self):
        p = Palabra.objects.first()
        Intento.objects.create(usuario=self.user, tipo='vocab', palabra=p, correcto=False)
        self.assertEqual(servicios.racha(self.user), 1)
        self.assertEqual(servicios.resumen(self.user)['porcentaje'], 0)


class NivelTests(BaseTest):
    def test_datos_cargados_en_10_bloques(self):
        niveles = set(Palabra.objects.oficiales().filter(nivel__isnull=False).values_list('nivel', flat=True))
        self.assertEqual(niveles, set(range(1, 11)))
        self.assertGreaterEqual(Palabra.objects.oficiales().filter(nivel__isnull=False).count(), 950)

    def test_cargar_datos_es_idempotente(self):
        antes = Palabra.objects.count()
        call_command('cargar_datos', verbosity=0)
        self.assertEqual(Palabra.objects.count(), antes)

    def test_construir_test(self):
        preguntas = servicios.construir_test()
        self.assertEqual(len(preguntas), servicios.BLOQUES * servicios.PREGUNTAS_POR_BLOQUE)
        for q in preguntas:
            self.assertEqual(len(q['opciones']), servicios.OPCIONES)
            self.assertIn(q['id'], [o['id'] for o in q['opciones']])
            self.assertEqual(len({o['espanol'] for o in q['opciones']}), servicios.OPCIONES)

    def _respuestas(self, preguntas, acierta_hasta):
        """Acierta las preguntas de los bloques <= acierta_hasta y se equivoca (o no sabe) en el resto."""
        niveles = dict(Palabra.objects.filter(id__in=[q['id'] for q in preguntas]).values_list('id', 'nivel'))
        return [
            {'palabra_id': q['id'], 'elegida_id': q['id'] if niveles[q['id']] <= acierta_hasta else None}
            for q in preguntas
        ]

    def test_evaluar_todo_correcto(self):
        res = servicios.evaluar_nivel(self._respuestas(servicios.construir_test(), 10))
        self.assertEqual(res['nivel_inicial'], 11)
        self.assertGreaterEqual(res['vocab_estimado'], 950)

    def test_evaluar_todo_incorrecto(self):
        res = servicios.evaluar_nivel(self._respuestas(servicios.construir_test(), 0))
        self.assertEqual(res['nivel_inicial'], 1)
        self.assertEqual(res['vocab_estimado'], 0)

    def test_evaluar_mitad(self):
        res = servicios.evaluar_nivel(self._respuestas(servicios.construir_test(), 5))
        self.assertEqual(res['nivel_inicial'], 6)
        self.assertTrue(400 <= res['vocab_estimado'] <= 520, res['vocab_estimado'])

    def test_evaluar_ignora_basura_y_duplicados(self):
        p = Palabra.objects.oficiales().filter(nivel=1).first()
        res = servicios.evaluar_nivel([
            {'palabra_id': p.id, 'elegida_id': p.id}, {'palabra_id': p.id, 'elegida_id': p.id},
            {'palabra_id': 999999, 'elegida_id': 1}, 'texto', {},
        ])
        self.assertEqual(res['detalle']['1']['total'], 1)

    def test_post_guarda_perfil_y_muestra_resultado(self):
        preguntas = self.client.get('/api/nivel/test/').data['preguntas']
        resp = self.client.post('/api/nivel/test/', {'respuestas': self._respuestas(preguntas, 3)}, format='json')
        self.assertEqual(resp.status_code, 200)
        perfil = Perfil.objects.get(usuario=self.user)
        self.assertEqual(perfil.nivel_inicial, 4)
        self.assertIsNotNone(perfil.test_fecha)
        self.assertEqual(self.client.get('/api/nivel/resultado/').status_code, 200)

    def test_post_invalido(self):
        resp = self.client.post('/api/nivel/test/', {'respuestas': 'no es una lista'}, format='json')
        self.assertEqual(resp.status_code, 400)
        resp = self.client.post('/api/nivel/test/', {'respuestas': []}, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_resultado_sin_test_da_404(self):
        self.assertEqual(self.client.get('/api/nivel/resultado/').status_code, 404)

    def test_estado_cuenta_palabras_asumidas(self):
        Perfil.objects.update_or_create(usuario=self.user, defaults={'nivel_inicial': 4})
        est = servicios.estado(self.user)
        esperadas = Palabra.objects.oficiales().filter(nivel__lt=4).count()
        self.assertEqual(est['asumidas'], esperadas)
        self.assertEqual(est['bloque_activo'], 4)
        self.assertFalse(est['desbloqueado'])

    def test_practica_se_centra_en_el_bloque_activo(self):
        Perfil.objects.update_or_create(usuario=self.user, defaults={'nivel_inicial': 6})
        for p in servicios.elegir_palabras(self.user, n=60):
            self.assertTrue(p.nivel is None or p.nivel >= 6, p)

    def test_dominar_un_bloque_avanza_al_siguiente(self):
        Perfil.objects.update_or_create(usuario=self.user, defaults={'nivel_inicial': 9})
        for p in Palabra.objects.oficiales().filter(nivel=9):
            for _ in range(3):
                Intento.objects.create(usuario=self.user, tipo='vocab', palabra=p, correcto=True)
        self.assertEqual(servicios.estado(self.user)['bloque_activo'], 10)

    def test_palabras_dominadas_pesan_menos(self):
        p = Palabra.objects.oficiales().filter(nivel=1).first()
        for _ in range(3):
            Intento.objects.create(usuario=self.user, tipo='vocab', palabra=p, correcto=True)
        self.assertIn(p.id, servicios.estado(self.user)['ids_dominadas'])


class MisPalabrasTests(BaseTest):
    def test_bloqueado_antes_de_dominar(self):
        resp = self.client.post('/api/mis-palabras/', {'ingles': 'zebra', 'espanol': 'cebra'}, format='json')
        self.assertEqual(resp.status_code, 403)
        self.assertFalse(Palabra.objects.filter(ingles='zebra').exists())

    def test_desbloqueado_permite_agregar_y_son_privadas(self):
        Perfil.objects.update_or_create(usuario=self.user, defaults={'nivel_inicial': 11})
        self.assertTrue(servicios.estado(self.user)['desbloqueado'])
        resp = self.client.post('/api/mis-palabras/', {'ingles': 'zebra', 'espanol': 'cebra'}, format='json')
        self.assertEqual(resp.status_code, 201)
        palabra = Palabra.objects.get(ingles='zebra')
        self.assertEqual(palabra.propietario, self.user)
        # Otra persona no la ve ni puede borrarla.
        otro = get_user_model().objects.create_user('beto', password='clave-segura-123')
        self.assertFalse(Palabra.objects.visibles(otro).filter(ingles='zebra').exists())
        self.client.force_authenticate(otro)
        self.assertEqual(self.client.delete(f'/api/mis-palabras/{palabra.pk}/').status_code, 404)
        self.assertTrue(Palabra.objects.filter(pk=palabra.pk).exists())

    def test_no_permite_duplicar(self):
        Perfil.objects.update_or_create(usuario=self.user, defaults={'nivel_inicial': 11})
        resp = self.client.post('/api/mis-palabras/', {'ingles': 'Apple', 'espanol': 'manzana'}, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(Palabra.objects.filter(propietario=self.user).exists())

    def test_el_admin_puede_agregar_sin_desbloquear(self):
        self.user.is_staff = True
        self.user.save()
        self.client.post('/api/mis-palabras/', {'ingles': 'zebra', 'espanol': 'cebra'}, format='json')
        self.assertTrue(Palabra.objects.filter(propietario=self.user, ingles='zebra').exists())


class TecnicoTests(BaseTest):
    def test_categorias_tecnicas_cargadas_con_ejemplo(self):
        from vocabulario.models import Categoria
        tecnicas = Categoria.objects.filter(es_tecnica=True)
        self.assertEqual(tecnicas.count(), 6)
        palabras = Palabra.objects.filter(categoria__in=tecnicas)
        self.assertGreaterEqual(palabras.count(), 150)
        self.assertFalse(palabras.filter(ejemplo='').exists())
        self.assertFalse(palabras.filter(nivel__isnull=False).exists())

    def test_nucleo_no_se_mezcla_con_tecnico_al_recargar(self):
        # 'salary' existe en el núcleo y en el vocabulario técnico.
        call_command('cargar_datos', verbosity=0)
        nucleo = Palabra.objects.get(ingles='salary', categoria__es_tecnica=False)
        tecnica = Palabra.objects.get(ingles='salary', categoria__es_tecnica=True)
        self.assertIsNotNone(nucleo.nivel)
        self.assertIsNone(tecnica.nivel)

    def test_practica_por_defecto_excluye_tecnico(self):
        for p in servicios.elegir_palabras(self.user, n=100):
            self.assertFalse(p.categoria.es_tecnica, p)

    def test_se_puede_practicar_una_categoria_tecnica(self):
        palabras = servicios.elegir_palabras(self.user, 'dev-git', n=5)
        self.assertEqual(len(palabras), 5)
        self.assertTrue(all(p.categoria.slug == 'dev-git' for p in palabras))
        resp = self.client.get('/api/tarjetas/', {'categoria': 'dev-git'})
        self.assertEqual(len(resp.data['palabras']), 20)

    def test_dominar_tecnico_no_cuenta_para_la_meta(self):
        antes = servicios.estado(self.user)['total']
        for p in Palabra.objects.filter(categoria__es_tecnica=True):
            for _ in range(3):
                Intento.objects.create(usuario=self.user, tipo='vocab', palabra=p, correcto=True)
        est = servicios.estado(self.user)
        self.assertEqual(est['total'], antes)
        self.assertEqual(est['tecnicas_dominadas'], est['tecnicas_total'])
        self.assertFalse(est['desbloqueado'])

    def test_inicio_incluye_categorias_tecnicas(self):
        resp = self.client.get('/api/inicio/')
        self.assertEqual(len(resp.data['categorias_tech']), 6)
        self.assertIn('dev-ops', [c['slug'] for c in resp.data['categorias_tech']])


class FrasesTests(BaseTest):
    def test_datos_de_frases_cargados(self):
        from vocabulario.models import Frase
        self.assertGreaterEqual(Frase.objects.count(), 200)
        self.assertTrue(Frase.objects.filter(tema='diario').exclude(traduccion='').exists())
        # Los ejemplos del vocabulario técnico también sirven como frases de dictado.
        self.assertTrue(Frase.objects.filter(texto='I found a bug in the login page.').exists())

    def test_cargar_datos_no_duplica_frases_ni_preguntas(self):
        from vocabulario.models import Frase
        from .models import PreguntaOral
        antes = (Frase.objects.count(), PreguntaOral.objects.count())
        call_command('cargar_datos', verbosity=0)
        self.assertEqual((Frase.objects.count(), PreguntaOral.objects.count()), antes)

    def test_comparar_frase_exacta_ignora_mayusculas_y_puntuacion(self):
        r = servicios.comparar_frase("We don't deploy on Fridays.", "we DON'T deploy on fridays")
        self.assertEqual(r['puntaje'], 100)
        self.assertTrue(r['correcto'])

    def test_comparar_frase_marca_palabras_mal(self):
        r = servicios.comparar_frase('I will push the changes today.', 'I will pull the changes today')
        estados = {p['texto']: p['estado'] for p in r['palabras']}
        self.assertEqual(estados['push'], 'mal')
        self.assertEqual(estados['changes'], 'ok')
        self.assertEqual(r['puntaje'], 83)
        self.assertFalse(r['correcto'])

    def test_comparar_frase_vacia_y_palabras_de_mas(self):
        self.assertEqual(servicios.comparar_frase('Hello there', '')['puntaje'], 0)
        r = servicios.comparar_frase('Hello there', 'well hello there my friend')
        self.assertLess(r['puntaje'], servicios.UMBRAL_FRASE)

    def test_comparar_frase_con_palabra_faltante(self):
        r = servicios.comparar_frase('I am on call this weekend', 'I am on call weekend')
        self.assertFalse(r['correcto'])
        self.assertEqual(sum(p['estado'] == 'mal' for p in r['palabras']), 1)

    def test_dictado_frases_flujo(self):
        from vocabulario.models import Frase
        datos = self.client.get('/api/dictado/frases/').data
        frase = Frase.objects.get(pk=datos['frase']['id'])
        resp = self.client.post(
            '/api/dictado/frases/', {'frase_id': frase.id, 'respuesta': frase.texto}, format='json',
        )
        self.assertTrue(resp.data['correcto'])
        intento = Intento.objects.get(tipo='frase')
        self.assertEqual((intento.puntaje, intento.frase), (100, frase))
        resp = self.client.post(
            '/api/dictado/frases/', {'frase_id': frase.id, 'respuesta': 'nada que ver'}, format='json',
        )
        self.assertFalse(resp.data['correcto'])

    def test_dictado_frases_filtra_por_tema(self):
        from vocabulario.models import Frase
        for _ in range(10):
            datos = self.client.get('/api/dictado/frases/', {'tema': 'diario'}).data
            self.assertEqual(Frase.objects.get(pk=datos['frase']['id']).tema, 'diario')

    def test_frase_fallada_pesa_mas(self):
        from vocabulario.models import Frase
        f = Frase.objects.filter(tema='diario').first()
        for _ in range(5):
            Intento.objects.create(usuario=self.user, tipo='frase', frase=f, correcto=False, puntaje=10)
        elegidas = [servicios.elegir_frase(self.user, 'diario') for _ in range(300)]
        # Con peso 11 frente a 1 de las otras 19, debería salir bastante más que 1/20 (15 veces).
        self.assertGreater(sum(e == f for e in elegidas), 50)


class OralTests(BaseTest):
    def test_endpoints_responden(self):
        for ruta in ['/api/oral/', '/api/oral/historial/']:
            self.assertEqual(self.client.get(ruta).status_code, 200, ruta)

    def test_preguntas_cargadas(self):
        from .models import PreguntaOral
        self.assertGreaterEqual(PreguntaOral.objects.count(), 25)
        self.assertEqual(set(PreguntaOral.objects.values_list('tema', flat=True)), {'entrevista', 'tecnica', 'reunion'})
        self.assertFalse(PreguntaOral.objects.filter(modelo='').exists())

    def test_otra_pregunta_no_repite_la_anterior(self):
        p1 = self.client.get('/api/oral/').data['pregunta']
        for _ in range(10):
            otra = self.client.get('/api/oral/', {'excluir': p1['id']}).data['pregunta']
            self.assertNotEqual(otra['id'], p1['id'])

    def test_filtro_por_tema(self):
        p = self.client.get('/api/oral/', {'tema': 'reunion'}).data['pregunta']
        self.assertEqual(p['tema'], 'reunion')

    def test_registrar_practica(self):
        from .models import PreguntaOral, RegistroOral
        p = self.client.get('/api/oral/').data['pregunta']
        resp = self.client.post('/api/oral/registrar/', {
            'pregunta_id': p['id'], 'duracion': 75, 'autoevaluacion': 4, 'notas': 'más vocabulario',
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        r = RegistroOral.objects.get(usuario=self.user)
        self.assertEqual((r.pregunta, r.duracion_seg, r.autoevaluacion), (PreguntaOral.objects.get(pk=p['id']), 75, 4))
        self.assertEqual(self.client.get('/api/oral/historial/').data['registros'][0]['pregunta'], p['texto'])

    def test_registrar_rechaza_nota_invalida(self):
        from .models import RegistroOral
        p = self.client.get('/api/oral/').data['pregunta']
        for nota in [0, 6, 'x', '']:
            resp = self.client.post(
                '/api/oral/registrar/', {'pregunta_id': p['id'], 'autoevaluacion': nota}, format='json',
            )
            self.assertEqual(resp.status_code, 400, nota)
        self.assertFalse(RegistroOral.objects.exists())

    def test_registrar_limita_duracion_y_requiere_post(self):
        from .models import RegistroOral
        p = self.client.get('/api/oral/').data['pregunta']
        self.client.post(
            '/api/oral/registrar/', {'pregunta_id': p['id'], 'autoevaluacion': 3, 'duracion': 99999}, format='json',
        )
        self.assertEqual(RegistroOral.objects.get().duracion_seg, 3600)
        self.assertEqual(self.client.get('/api/oral/registrar/').status_code, 405)

    def test_elegir_pregunta_prefiere_las_no_practicadas(self):
        from .models import PreguntaOral, RegistroOral
        todas = list(PreguntaOral.objects.filter(tema='reunion'))
        for p in todas[:-1]:
            RegistroOral.objects.create(usuario=self.user, pregunta=p, autoevaluacion=3)
        for _ in range(20):
            self.assertEqual(servicios.elegir_pregunta(self.user, 'reunion'), todas[-1])

    def test_la_practica_oral_cuenta_para_la_racha_y_el_resumen(self):
        from .models import PreguntaOral, RegistroOral
        self.assertEqual(servicios.racha(self.user), 0)
        p = PreguntaOral.objects.first()
        RegistroOral.objects.create(usuario=self.user, pregunta=p, autoevaluacion=2, duracion_seg=90)
        RegistroOral.objects.create(usuario=self.user, pregunta=p, autoevaluacion=4, duracion_seg=30)
        self.assertEqual(servicios.racha(self.user), 1)
        res = servicios.resumen_oral(self.user)
        self.assertEqual((res['total'], res['minutos'], res['promedio']), (2, 2, 3.0))

    def test_historial_es_privado(self):
        from .models import PreguntaOral, RegistroOral
        otro = get_user_model().objects.create_user('beto', password='clave-segura-123')
        RegistroOral.objects.create(usuario=otro, pregunta=PreguntaOral.objects.first(), autoevaluacion=5, notas='SECRETO')
        self.assertEqual(self.client.get('/api/oral/historial/').data['registros'], [])


class ExamenAdaptativoTests(BaseTest):
    def _responder(self, historial, aciertos=True):
        """Pide la siguiente pregunta y la contesta bien (o mal) añadiéndola al historial."""
        paso = servicios.paso_examen(historial)
        self.assertFalse(paso['terminado'])
        q = paso['pregunta']
        elegida = q['id'] if aciertos else next(o['id'] for o in q['opciones'] if o['id'] != q['id'])
        historial.append({'palabra_id': q['id'], 'elegida_id': elegida})
        return paso

    def test_empieza_en_el_nivel_mas_bajo(self):
        paso = servicios.paso_examen([])
        self.assertFalse(paso['terminado'])
        self.assertEqual(Palabra.objects.get(pk=paso['pregunta']['id']).nivel, 1)
        self.assertEqual(paso['progreso']['nivel'], 1)
        self.assertEqual(paso['progreso']['avance'], 0)
        self.assertEqual(len(paso['progreso']['niveles']), servicios.BLOQUES)

    def test_sube_de_nivel_al_acertar(self):
        historial = []
        for _ in range(servicios.EXAMEN_ACIERTOS):
            self._responder(historial)
        paso = servicios.paso_examen(historial)
        self.assertEqual(paso['progreso']['nivel'], 2)
        self.assertEqual(paso['progreso']['aprobados'], 1)
        self.assertEqual(Palabra.objects.get(pk=paso['pregunta']['id']).nivel, 2)

    def test_no_repite_palabras(self):
        historial = []
        for _ in range(servicios.EXAMEN_ACIERTOS + 1):
            self._responder(historial)
        ids = [r['palabra_id'] for r in historial]
        self.assertEqual(len(ids), len(set(ids)))

    def test_termina_al_reprobar_un_nivel(self):
        historial = []
        for _ in range(servicios.EXAMEN_ACIERTOS):  # aprueba el nivel 1
            self._responder(historial)
        for _ in range(servicios.EXAMEN_FALLOS):    # reprueba el nivel 2
            self._responder(historial, aciertos=False)
        paso = servicios.paso_examen(historial)
        self.assertTrue(paso['terminado'])
        res = paso['resultado']
        self.assertEqual(res['nivel_inicial'], 2)
        self.assertTrue(res['detalle']['1']['aprobado'])
        self.assertFalse(res['detalle']['2']['aprobado'])
        self.assertEqual(len(res['errores']), servicios.EXAMEN_FALLOS)
        self.assertEqual({e['bloque'] for e in res['errores']}, {2})
        self.assertGreaterEqual(res['vocab_estimado'], Palabra.objects.oficiales().filter(nivel=1).count())

    def test_fallar_todo_deja_el_nivel_1(self):
        historial = []
        for _ in range(servicios.EXAMEN_FALLOS):
            self._responder(historial, aciertos=False)
        res = servicios.paso_examen(historial)['resultado']
        self.assertEqual(res['nivel_inicial'], 1)
        self.assertEqual(res['vocab_estimado'], 0)

    def test_aprobar_todo_completa_el_nucleo(self):
        historial = []
        while not servicios.paso_examen(historial)['terminado']:
            self._responder(historial)
        res = servicios.paso_examen(historial)['resultado']
        self.assertEqual(res['nivel_inicial'], servicios.BLOQUES + 1)
        self.assertEqual(len(historial), servicios.BLOQUES * servicios.EXAMEN_ACIERTOS)
        self.assertEqual(res['errores'], [])

    def test_ignora_respuestas_de_otro_nivel_duplicadas_y_basura(self):
        dificil = Palabra.objects.oficiales().filter(nivel=5).first()
        facil = Palabra.objects.oficiales().filter(nivel=1).first()
        paso = servicios.paso_examen([
            {'palabra_id': dificil.id, 'elegida_id': dificil.id},   # no es del nivel actual
            {'palabra_id': facil.id, 'elegida_id': facil.id},
            {'palabra_id': facil.id, 'elegida_id': facil.id},       # duplicada
            'texto', {}, {'palabra_id': 'x'}, {'palabra_id': 999999, 'elegida_id': 1},
        ])
        self.assertEqual(paso['progreso']['aciertos_nivel'], 1)
        self.assertEqual(paso['progreso']['nivel'], 1)

    def test_endpoint_guarda_el_resultado_al_terminar(self):
        historial = []
        for _ in range(servicios.EXAMEN_FALLOS):
            self._responder(historial, aciertos=False)
        resp = self.client.post('/api/nivel/examen/', {'historial': historial}, format='json')
        self.assertTrue(resp.data['terminado'])
        perfil = Perfil.objects.get(usuario=self.user)
        self.assertEqual(perfil.nivel_inicial, 1)
        self.assertEqual(len(perfil.errores), servicios.EXAMEN_FALLOS)
        self.assertEqual(self.client.get('/api/nivel/resultado/').data['errores'], perfil.errores)

    def test_endpoint_devuelve_pregunta_sin_guardar_mientras_dura(self):
        resp = self.client.post('/api/nivel/examen/', {'historial': []}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.data['terminado'])
        self.assertIn('pregunta', resp.data)
        self.assertIsNone(Perfil.de(self.user).test_fecha)

    def test_endpoint_rechaza_historial_invalido(self):
        for malo in ('no es lista', [{}] * 201):
            resp = self.client.post('/api/nivel/examen/', {'historial': malo}, format='json')
            self.assertEqual(resp.status_code, 400)

    def test_endpoint_requiere_login(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.post('/api/nivel/examen/', {'historial': []}, format='json').status_code, 401)


class QuizPorNivelTests(BaseTest):
    def test_quiz_vocab_respeta_el_nivel_pedido(self):
        for nivel in (1, 5, 10):
            for _ in range(5):
                pregunta = self.client.get('/api/quiz/vocabulario/', {'nivel': nivel}).data['palabra']
                self.assertEqual(Palabra.objects.get(pk=pregunta['id']).nivel, nivel)

    def test_nivel_fuera_de_rango_se_ignora(self):
        for malo in ('0', '11', 'abc', '-1'):
            self.assertEqual(self.client.get('/api/quiz/vocabulario/', {'nivel': malo}).status_code, 200)

    def test_nivel_no_trae_palabras_propias_ni_tecnicas(self):
        for _ in range(30):
            pregunta = self.client.get('/api/quiz/vocabulario/', {'nivel': 3}).data['palabra']
            palabra = Palabra.objects.get(pk=pregunta['id'])
            self.assertIsNone(palabra.propietario_id)
            self.assertFalse(palabra.categoria.es_tecnica)

    def test_nivel_info_en_intro(self):
        datos = self.client.get('/api/nivel/').data
        self.assertEqual(len(datos['niveles']), servicios.BLOQUES)
        self.assertEqual(datos['niveles'][0], {'numero': 1, 'nombre': 'Inicial', 'cefr': 'A1'})
        self.assertEqual(datos['quiz']['preguntas'], servicios.QUIZ_PREGUNTAS)
