from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from practica.models import Intento, PreguntaOral, RegistroOral
from usuarios.models import Perfil
from verbos.models import Verbo
from vocabulario.models import Categoria, Frase, Palabra

User = get_user_model()


class ApiBase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = User.objects.create_user('ana', password='clave-larga-123')
        cls.otro = User.objects.create_user('beto', password='clave-larga-123')
        cls.categoria = Categoria.objects.create(nombre='General', slug='general')
        cls.palabra = Palabra.objects.create(categoria=cls.categoria, ingles='house', espanol='casa', nivel=1)
        cls.verbo = Verbo.objects.create(
            infinitivo='go', espanol='ir', tercera_persona='goes', pasado='went', participio='gone', irregular=True,
        )
        cls.frase = Frase.objects.create(texto='I like coffee.', traduccion='Me gusta el café.')
        cls.pregunta = PreguntaOral.objects.create(tema='entrevista', texto='Tell me about yourself.')

    def setUp(self):
        self.client.force_authenticate(self.usuario)


class SaludTests(APITestCase):
    def test_responde_sin_login(self):
        r = self.client.get('/api/salud/')
        self.assertEqual((r.status_code, r.data), (200, {'ok': True}))


class AutenticacionTests(APITestCase):
    def test_sin_token_responde_401(self):
        for ruta in ('/api/inicio/', '/api/tarjetas/', '/api/progreso/', '/api/oral/'):
            self.assertEqual(self.client.get(ruta).status_code, 401, ruta)

    def test_registro_devuelve_tokens_y_permite_entrar(self):
        r = self.client.post('/api/auth/registro/', {
            'username': 'nuevo', 'password1': 'una-clave-segura-9', 'password2': 'una-clave-segura-9',
        })
        self.assertEqual(r.status_code, 201)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {r.data["access"]}')
        self.assertEqual(self.client.get('/api/auth/yo/').data['username'], 'nuevo')

    def test_registro_con_claves_distintas_da_errores(self):
        r = self.client.post('/api/auth/registro/', {
            'username': 'nuevo', 'password1': 'una-clave-segura-9', 'password2': 'otra-distinta-9',
        })
        self.assertEqual(r.status_code, 400)
        self.assertIn('password2', r.data['errores'])

    def test_login_con_jwt(self):
        User.objects.create_user('carla', password='clave-larga-123')
        r = self.client.post('/api/auth/token/', {'username': 'carla', 'password': 'clave-larga-123'})
        self.assertEqual(r.status_code, 200)
        self.assertIn('access', r.data)
        self.assertEqual(
            self.client.post('/api/auth/token/', {'username': 'carla', 'password': 'mala'}).status_code, 401,
        )


class LecturaTests(ApiBase):
    def test_inicio(self):
        r = self.client.get('/api/inicio/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['categorias'], [{'nombre': 'General', 'slug': 'general'}])
        self.assertEqual(r.data['estado']['meta'], 1000)
        self.assertNotIn('stats', r.data['estado'])
        self.assertNotIn('ids_dominadas', r.data['estado'])

    def test_progreso_vocabulario_y_verbos(self):
        self.assertEqual(self.client.get('/api/progreso/').status_code, 200)
        self.assertEqual(self.client.get('/api/vocabulario/').data['categorias'][0]['palabras'][0]['ingles'], 'house')
        self.assertEqual(self.client.get('/api/verbos/').data['verbos'][0]['pasado'], 'went')

    def test_vocabulario_no_muestra_palabras_propias_de_otro(self):
        Palabra.objects.create(categoria=self.categoria, ingles='secret', espanol='secreto', propietario=self.otro)
        palabras = self.client.get('/api/vocabulario/').data['categorias'][0]['palabras']
        self.assertEqual([p['ingles'] for p in palabras], ['house'])

    def test_actividad_cubre_30_dias_con_ceros(self):
        actividad = self.client.get('/api/progreso/').data['actividad']
        self.assertEqual(len(actividad), 30)
        self.assertTrue(all(d['total'] == 0 for d in actividad))
        Intento.objects.create(usuario=self.usuario, tipo='vocab', palabra=self.palabra, correcto=True)
        Intento.objects.create(usuario=self.usuario, tipo='vocab', palabra=self.palabra, correcto=False)
        Intento.objects.create(usuario=self.otro, tipo='vocab', palabra=self.palabra, correcto=True)
        hoy = self.client.get('/api/inicio/').data['actividad'][-1]
        self.assertEqual((hoy['total'], hoy['aciertos'], hoy['fallos']), (2, 1, 1))

    def test_bloques_cuentan_lo_asumido_por_el_test_como_dominado(self):
        bloques = self.client.get('/api/progreso/').data['bloques']
        self.assertEqual(bloques, [{'numero': 1, 'total': 1, 'dominadas': 0, 'asumido': False, 'porcentaje': 0}])
        Perfil.objects.update_or_create(usuario=self.usuario, defaults={'nivel_inicial': 2})
        bloques = self.client.get('/api/progreso/').data['bloques']
        self.assertEqual((bloques[0]['porcentaje'], bloques[0]['asumido']), (100, True))

    def test_consejos(self):
        r = self.client.get('/api/consejos/')
        self.assertEqual(r.data['faltan'], 1000)
        self.assertEqual(r.data['plan'][0], {'por_dia': 5, 'dias': 200})


class PracticaTests(ApiBase):
    def test_tarjetas_y_registro(self):
        r = self.client.get('/api/tarjetas/')
        self.assertEqual([p['ingles'] for p in r.data['palabras']], ['house'])
        r = self.client.post('/api/tarjetas/registrar/', {'palabra_id': self.palabra.id, 'correcto': True}, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(Intento.objects.get(usuario=self.usuario).correcto)

    def test_tarjeta_inexistente_o_ajena_da_404(self):
        propia = Palabra.objects.create(categoria=self.categoria, ingles='mine', espanol='mia', propietario=self.otro)
        r = self.client.post('/api/tarjetas/registrar/', {'palabra_id': propia.id, 'correcto': True}, format='json')
        self.assertEqual(r.status_code, 404)

    def test_quiz_vocab_traducir_no_revela_el_ingles(self):
        palabra = self.client.get('/api/quiz/vocabulario/').data['palabra']
        self.assertEqual(palabra, {'id': self.palabra.id, 'espanol': 'casa'})

    def test_quiz_vocab_dictado_envia_el_ingles(self):
        palabra = self.client.get('/api/quiz/vocabulario/?modo=dictado').data['palabra']
        self.assertEqual(palabra, {'id': self.palabra.id, 'ingles': 'house'})

    def test_quiz_vocab_corrige_ignorando_mayusculas_y_espacios(self):
        r = self.client.post('/api/quiz/vocabulario/', {
            'palabra_id': self.palabra.id, 'modo': 'traducir', 'respuesta': '  HOUSE ',
        }, format='json')
        self.assertTrue(r.data['correcto'])
        r = self.client.post('/api/quiz/vocabulario/', {
            'palabra_id': self.palabra.id, 'modo': 'dictado', 'respuesta': 'hause',
        }, format='json')
        self.assertFalse(r.data['correcto'])
        self.assertEqual(Intento.objects.filter(tipo='vocab').count(), 1)
        self.assertEqual(Intento.objects.filter(tipo='dictado').count(), 1)

    def test_quiz_verbos_con_ticket(self):
        ej = self.client.get('/api/quiz/verbos/?tiempo=pasado').data
        self.assertIn('ticket', ej)
        self.assertNotIn('went', str(ej['enunciado']))
        r = self.client.post('/api/quiz/verbos/', {'ticket': ej['ticket'], 'respuesta': 'went'}, format='json')
        self.assertTrue(r.data['correcto'])
        self.assertEqual(r.data['correcta'], 'went')
        self.assertEqual(Intento.objects.get(tipo='verbo').tiempo, 'pasado')

    def test_quiz_verbos_rechaza_ticket_alterado(self):
        ej = self.client.get('/api/quiz/verbos/').data
        r = self.client.post('/api/quiz/verbos/', {'ticket': ej['ticket'] + 'x', 'respuesta': 'went'}, format='json')
        self.assertEqual(r.status_code, 400)
        self.assertFalse(Intento.objects.exists())

    def test_dictado_frases(self):
        r = self.client.get('/api/dictado/frases/')
        self.assertEqual(r.data['frase'], {'id': self.frase.id, 'texto': 'I like coffee.'})
        r = self.client.post('/api/dictado/frases/', {'frase_id': self.frase.id, 'respuesta': 'i like coffee'}, format='json')
        self.assertEqual(r.data['puntaje'], 100)
        self.assertTrue(r.data['correcto'])
        self.assertEqual(r.data['frase']['traduccion'], 'Me gusta el café.')


class NivelTests(ApiBase):
    def test_test_de_nivel_guarda_el_perfil(self):
        preguntas = self.client.get('/api/nivel/test/').data['preguntas']
        self.assertEqual(len(preguntas), 1)
        r = self.client.post('/api/nivel/test/', {
            'respuestas': [{'palabra_id': self.palabra.id, 'elegida_id': self.palabra.id}],
        }, format='json')
        self.assertTrue(r.data['ok'])
        resultado = self.client.get('/api/nivel/resultado/')
        self.assertEqual(resultado.status_code, 200)
        self.assertEqual(resultado.data['bloques'][0]['aciertos'], 1)

    def test_resultado_sin_test_da_404(self):
        self.assertEqual(self.client.get('/api/nivel/resultado/').status_code, 404)

    def test_respuestas_vacias_dan_400(self):
        self.assertEqual(self.client.post('/api/nivel/test/', {'respuestas': []}, format='json').status_code, 400)


class MisPalabrasTests(ApiBase):
    def test_bloqueado_hasta_dominar_el_90_por_ciento(self):
        self.assertFalse(self.client.get('/api/mis-palabras/').data['puede_agregar'])
        r = self.client.post('/api/mis-palabras/', {'ingles': 'cat', 'espanol': 'gato'}, format='json')
        self.assertEqual(r.status_code, 403)

    def test_staff_puede_agregar_y_borrar_solo_las_suyas(self):
        self.usuario.is_staff = True
        self.usuario.save()
        r = self.client.post('/api/mis-palabras/', {'ingles': 'cat', 'espanol': 'gato'}, format='json')
        self.assertEqual(r.status_code, 201)
        propia = Palabra.objects.get(propietario=self.usuario)
        ajena = Palabra.objects.create(categoria=self.categoria, ingles='dog', espanol='perro', propietario=self.otro)
        self.assertEqual(self.client.delete(f'/api/mis-palabras/{ajena.id}/').status_code, 404)
        self.assertEqual(self.client.delete(f'/api/mis-palabras/{propia.id}/').status_code, 204)
        self.assertTrue(Palabra.objects.filter(pk=ajena.pk).exists())

    def test_palabra_repetida_da_error_de_validacion(self):
        self.usuario.is_staff = True
        self.usuario.save()
        r = self.client.post('/api/mis-palabras/', {'ingles': 'HOUSE', 'espanol': 'casa'}, format='json')
        self.assertEqual(r.status_code, 400)
        self.assertIn('ingles', r.data['errores'])


class OralTests(ApiBase):
    def test_pregunta_y_registro(self):
        r = self.client.get('/api/oral/')
        self.assertEqual(r.data['pregunta']['id'], self.pregunta.id)
        self.assertFalse(r.data['hoy_hecho'])
        r = self.client.post('/api/oral/registrar/', {
            'pregunta_id': self.pregunta.id, 'autoevaluacion': 4, 'duracion': 75, 'notas': 'bien',
        }, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertTrue(self.client.get(f'/api/oral/{self.pregunta.id}/').data['hoy_hecho'])
        historial = self.client.get('/api/oral/historial/').data
        self.assertEqual(historial['registros'][0]['autoevaluacion'], 4)
        self.assertEqual(historial['resumen_oral']['total'], 1)

    def test_calificacion_fuera_de_rango_da_400(self):
        for nota in (0, 6, 'x', None):
            r = self.client.post('/api/oral/registrar/', {
                'pregunta_id': self.pregunta.id, 'autoevaluacion': nota,
            }, format='json')
            self.assertEqual(r.status_code, 400, nota)
        self.assertFalse(RegistroOral.objects.exists())

    def test_con_una_sola_pregunta_pedir_otra_no_falla(self):
        r = self.client.get(f'/api/oral/?excluir={self.pregunta.id}')
        self.assertEqual(r.data['pregunta']['id'], self.pregunta.id)
