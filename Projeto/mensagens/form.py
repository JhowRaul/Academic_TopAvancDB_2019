from django.forms import ModelForm
from django import forms
from .models import Usuario
from .models import Mensagem

class novoUsuarioForm(ModelForm):
    apelido = forms.CharField(widget=forms.TextInput(
        attrs={
            'class': 'form-control'
        }
    ))
    nome = forms.CharField(widget=forms.TextInput(
        attrs={
            'class': 'form-control'
        }
    ))

    class Meta:
        model = Usuario
        fields = ['apelido', 'nome']

class loginForm(ModelForm):
    apelido = forms.CharField(widget=forms.TextInput(
        attrs={
            'class': 'form-control'
        }
    ))

    class Meta:
        model = Usuario
        fields = ['apelido']

class formNovaMsg(ModelForm):
    destinatarios = forms.CharField(widget=forms.TextInput(
        attrs={
            'class': 'form-control'
        }
    ))
    class Meta:
        model = Mensagem
        fields = ['destinatarios', 'texto']