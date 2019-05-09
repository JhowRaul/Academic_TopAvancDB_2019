from django.forms import ModelForm
from .models import Usuario

class novoUsuarioForm(ModelForm):
    class Meta:
        model = Usuario
        fields = ['apelido', 'nome']

class loginForm(ModelForm):
    class Meta:
        model = Usuario
        fields = ['apelido']