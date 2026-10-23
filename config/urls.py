from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cuentas/', include('usuarios.urls')),
    path('vocabulario/', include('vocabulario.urls')),
    path('verbos/', include('verbos.urls')),
    path('', include('practica.urls')),
]
