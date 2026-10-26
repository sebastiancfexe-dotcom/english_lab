from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

urlpatterns = [
    path('salud/', views.salud),
    path('auth/token/', TokenObtainPairView.as_view()),
    path('auth/token/refresh/', TokenRefreshView.as_view()),
    path('auth/registro/', views.registro),
    path('auth/yo/', views.yo),
    path('inicio/', views.inicio),
    path('nivel/', views.nivel_intro),
    path('nivel/test/', views.nivel_test),
    path('nivel/resultado/', views.nivel_resultado),
    path('consejos/', views.consejos),
    path('mis-palabras/', views.mis_palabras),
    path('mis-palabras/<int:pk>/', views.borrar_palabra),
    path('tarjetas/', views.tarjetas),
    path('tarjetas/registrar/', views.registrar_tarjeta),
    path('quiz/vocabulario/', views.quiz_vocab),
    path('quiz/verbos/', views.quiz_verbos),
    path('dictado/frases/', views.dictado_frases),
    path('oral/', views.oral),
    path('oral/<int:pk>/', views.oral_pregunta),
    path('oral/registrar/', views.oral_registrar),
    path('oral/historial/', views.oral_historial),
    path('progreso/', views.progreso),
    path('vocabulario/', views.vocabulario),
    path('verbos/', views.verbos),
]
