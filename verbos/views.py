from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Verbo


@login_required
def lista(request):
    return render(request, 'verbos/lista.html', {'verbos': Verbo.objects.all()})
