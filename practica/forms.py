from django import forms

from vocabulario.models import Palabra


class PalabraPropiaForm(forms.ModelForm):
    class Meta:
        model = Palabra
        fields = ['ingles', 'espanol', 'ejemplo']
        labels = {'ingles': 'Inglés', 'espanol': 'Español', 'ejemplo': 'Ejemplo (opcional)'}

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario

    def clean_ingles(self):
        ingles = ' '.join(self.cleaned_data['ingles'].split())
        ya = Palabra.objects.visibles(self.usuario).filter(ingles__iexact=ingles).exists()
        if ya:
            raise forms.ValidationError('Esa palabra ya está en tu vocabulario.')
        return ingles
