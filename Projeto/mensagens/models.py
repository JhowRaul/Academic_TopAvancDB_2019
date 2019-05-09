from django.db import models

# Create your models here.
class Usuario(models.Model):
    apelido = models.CharField(max_length=15)
    nome = models.CharField(max_length=100)
    cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.apelido