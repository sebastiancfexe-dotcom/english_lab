from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q
from django.shortcuts import render

from .models import Categoria, Palabra


@login_required
def lista(request):
    visibles = Palabra.objects.filter(Q(propietario__isnull=True) | Q(propietario=request.user))
    categorias = (
        Categoria.objects.prefetch_related(Prefetch('palabras', queryset=visibles, to_attr='visibles'))
    )
    return render(request, 'vocabulario/lista.html', {
        'categorias': [c for c in categorias if c.visibles],
    })
