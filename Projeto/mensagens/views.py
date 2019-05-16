# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from .dao import UsuarioDao
from .form import loginForm, novoUsuarioForm
import redis
from nose.tools import ok_, eq_, raises
from gxredis import *

import datetime
import time

# client = redis.StrictRedis("localhost", 6379, 15)
HOSTNAME = "localhost"
PORT = 6379
DB = 15

# Create your views here.
def login(request):
    data = {}
    form = loginForm(request.POST or None)

    if form.is_valid():
        apelido =  form.cleaned_data['apelido']
        return redirect('url_painel', apelido=apelido)

    data['form'] = form
    return render(request, 'usuario/login.html', data);

def novo(request):
    data = {}
    form = novoUsuarioForm(request.POST or None)

    data['form'] = form

    if form.is_valid():
        client = redis.StrictRedis(HOSTNAME, PORT)
        dao = UsuarioDao(client)

        apelido = form.cleaned_data['apelido']
        nome = form.cleaned_data['nome']

        result = dao.item_set.sadd(apelido)

        if result == 1:
            print("Sucesso no registro")
            dao.item_hash(apelido=apelido).hset('apelido', apelido)
            dao.item_hash(apelido=apelido).hset('nome', nome)
            dao.item_hash(apelido=apelido).hset('cadastro', time.strftime("%d/%m/%Y"))
            data['result'] = "Usuário cadastrado com sucesso."

            return redirect('url_painel', apelido=apelido)
        else:
            print("Falha no registro")
            data['result'] = "Usuário já existe"
            return render(request, 'usuario/novo.html', data);

    return render(request, 'usuario/novo.html', data);

def painel(request, apelido):
    data= {}
    data['apelido'] = apelido
    data['now'] = datetime.datetime.now()

    client = redis.StrictRedis(HOSTNAME, PORT)
    dao = UsuarioDao(client)

    keys, result = dao.item_set.smembers_mget()
    if apelido.encode() in keys:
        return render(request, 'painel/home.html', data);
    else:
        data['result'] = 'Usuário não está cadastrado.'
        return redirect('url_login')