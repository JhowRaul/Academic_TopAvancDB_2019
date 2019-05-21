from django.db import models

# Create your models here.
class Usuario(models.Model):
    apelido = models.CharField(max_length=15)
    nome = models.CharField(max_length=100)
    cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.apelido

class Mensagem(models.Model):
    id = models.TextField(max_length=None, primary_key=True)
    respostade = models.TextField(max_length=None)
    data = models.TextField(max_length=None)
    remetente = models.TextField(max_length=15)
    destinatarios = models.TextField(max_length=None)
    texto = models.TextField(max_length=None)