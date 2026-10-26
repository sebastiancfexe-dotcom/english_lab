from django.contrib import admin
from django.urls import include, path

# Django es solo el backend: la API en /api/ y el panel de administración en /admin/.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
