from django.urls import path

from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('tarjetas/', views.tarjetas, name='tarjetas'),
    path('tarjetas/registrar/', views.registrar_tarjeta, name='registrar_tarjeta'),
    path('quiz/vocabulario/', views.quiz_vocab, name='quiz_vocab'),
    path('quiz/verbos/', views.quiz_verbos, name='quiz_verbos'),
    path('dictado/frases/', views.dictado_frases, name='dictado_frases'),
    path('oral/', views.oral, name='oral'),
    path('oral/registrar/', views.oral_registrar, name='oral_registrar'),
    path('oral/historial/', views.oral_historial, name='oral_historial'),
    path('progreso/', views.progreso, name='progreso'),
    path('nivel/', views.nivel_intro, name='nivel_intro'),
    path('nivel/test/', views.nivel_test, name='nivel_test'),
    path('nivel/resultado/', views.nivel_resultado, name='nivel_resultado'),
    path('consejos/', views.consejos, name='consejos'),
    path('mis-palabras/', views.mis_palabras, name='mis_palabras'),
    path('mis-palabras/<int:pk>/borrar/', views.borrar_palabra, name='borrar_palabra'),
]
