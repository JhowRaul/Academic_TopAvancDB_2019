# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from .dao import UsuarioDao, MensagemDao
from .form import loginForm, novoUsuarioForm, formNovaMsg, formRespostaMsg
import redis
from nose.tools import ok_, eq_, raises
from gxredis import *
from datetime import datetime
from uuid import uuid4
import json

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
        # Recuperar mensagens recebidas
        dao2 = MensagemDao(client, key_params={"apelido": apelido})

        listaMensagem = []
        listaMensagemEnv = []
        ids, mensagens = dao2.item_set.smembers_mget()

        idsEnv, mensagensEnv = dao2.item_set_env.smembers_mget()

        for elem in ids:
            elemNovo = str(elem, 'utf-8').replace(':', '-')
            listaMensagem.append(elemNovo)

        data['mensagens'] = listaMensagem

        for elem in idsEnv:
            elemNovo = str(elem, 'utf-8').replace(':', '-')
            listaMensagemEnv.append(elemNovo)

        data['mensagensEnv'] = listaMensagemEnv

        return render(request, 'painel/home.html', data);
    else:
        data['result'] = 'Usuário não está cadastrado.'
        return redirect('url_login')

def novaMsg(request, apelido):
    data = {}
    data['apelido'] = apelido

    formNova = formNovaMsg(request.POST or None)
    data['formNovaMsg'] = formNova

    client = redis.StrictRedis(HOSTNAME, PORT)
    dao = UsuarioDao(client)

    keys, result = dao.item_set.smembers_mget()
    if apelido.encode() in keys:
        if formNova.is_valid():

            dataa = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            dataId = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
            id = "mensagem:" + dataId
            remetente = apelido
            destinatarios = formNova.cleaned_data['destinatarios']
            texto = formNova.cleaned_data['texto']

            # Tranformando destinatarios em lista
            destSplit = destinatarios.split()
            dest = []

            for elem in destSplit:
                if elem.encode() in keys:
                    dest.append(elem)
                else:
                    print(elem + " não cadastrado.")

            # Criando mensagem completa
            msg = {'id':id,'remetente':remetente,'destinatarios':dest,'texto':texto,'data':dataa}

            # Tranformando mensagem em json
            msgJSON = json.dumps(msg)

            # Salvando JSON de mensagem completa
            dao2 = MensagemDao(client, key_params={"id": id, "apelido": apelido})
            result = dao2.item(id=id).set(msgJSON)

            teste = dao2.item(id=id).get()
            print(teste)

            if result == 1:
                # Loop para enviar para todos os destinatarios
                for elem in dest:
                    dao2.item_set(apelido=elem).sadd(id)

                # Salvando para ler enviadas
                dao2.item_set_env(apelido=apelido).sadd(id)

                return redirect('url_painel', apelido=apelido)
            else:
                print("Falha no envio")
                # data['result'] = "Falha no envio"
                return redirect('url_painel', apelido=apelido)

        return render(request, 'painel/nova-msg.html', data);
    else:
        data['result'] = 'Usuário não está cadastrado.'
        return redirect('url_login')

def mensagem(request, apelido, mensagem):
    data = {}
    data['apelido'] = apelido
    data['mensagem'] = mensagem

    mensagemDois = mensagem.replace('-', ':')
    data['mensagemDois'] = mensagemDois

    client = redis.StrictRedis(HOSTNAME, PORT)
    dao = UsuarioDao(client)
    dao2 = MensagemDao(client, key_params={"id": mensagemDois, "apelido": apelido})

    keys, result = dao.item_set.smembers_mget()
    mensagemGet = dao2.item(id=mensagemDois).get()
    if apelido.encode() in keys:
        if mensagemGet != None:
            msg = json.loads(str(mensagemGet, 'utf-8'))
            data['mensagemGet'] = msg

            if msg['remetente'] == apelido or apelido in msg['destinatarios']:
                redisClient = redis.StrictRedis(host=HOSTNAME, port=PORT)
                respostas = redisClient.zrange(mensagem, 0, -1)

                listRespostas = []
                for elem in respostas:
                    elemOk = str(elem, 'utf-8').replace(':', '-')
                    listRespostas.append(elemOk)

                data['respostas'] = listRespostas

                return render(request, 'painel/mensagem.html', data)
            else:
                print("Essa mensagem não é de " + apelido)
                return redirect('url_painel', apelido=apelido)
        else:
            return redirect('url_painel', apelido=apelido)
    else:
        return redirect('url_login')

def responder(request, apelido, mensagem):
    formResposta = formRespostaMsg(request.POST or None)
    data = {}
    data['formResposta'] = formResposta
    data['apelido'] = apelido
    data['mensagem'] = mensagem

    if formResposta.is_valid():
        client = redis.StrictRedis(HOSTNAME, PORT)
        dao = UsuarioDao(client)
        dao2 = MensagemDao(client, key_params={"id": mensagem, "apelido": apelido})

        keys, result = dao.item_set.smembers_mget()
        if apelido.encode() in keys:
            mensagemDois = mensagem.replace('-', ':')
            mensagemGet = dao2.item(id=mensagemDois).get()
            if mensagemGet != None:
                msg = json.loads(str(mensagemGet, 'utf-8'))
                data['mensagemGet'] = msg
                print("Antiga: ")
                print(msg)

                if msg['remetente'] == apelido or apelido in msg['destinatarios']:
                    dataa = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                    dataId = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
                    id = "mensagem:" + dataId
                    remetente = apelido
                    destinatarios = []
                    texto = formResposta.cleaned_data['texto']

                    # Tranformando destinatarios em lista
                    for elem in msg['destinatarios']:
                        if elem.encode() in keys:
                            if elem != apelido:
                                destinatarios.append(elem)
                        else:
                            print(elem + " não cadastrado.")

                    destinatarios.append(msg['remetente'])

                    # Criando mensagem completa
                    msgNova = {'id': id, 'remetente': remetente, 'destinatarios': destinatarios, 'respostaDe': mensagem, 'texto': texto, 'data': dataa}

                    # Tranformando mensagem em json
                    msgJSON = json.dumps(msgNova)

                    # Salvando JSON de mensagem completa
                    dao3 = MensagemDao(client, key_params={"id": id, "apelido": apelido})
                    result = dao3.item(id=id).set(msgJSON)

                    teste = dao3.item(id=id).get()
                    print("Nova")
                    print(teste)

                    if result == 1:
                        # Loop para enviar para todos os destinatarios
                        for elem in destinatarios:
                            dao3.item_set(apelido=elem).sadd(id)

                        # Salvando para ler enviadas
                        dao3.item_set_env(apelido=apelido).sadd(id)

                        redisClient = redis.StrictRedis(host=HOSTNAME, port=PORT)
                        # Salvando para ler respostas
                        numRespostas = redisClient.zcard(mensagem)
                        numRespostas += 1
                        redisClient.zadd(mensagem, {id: numRespostas})

                        return redirect('url_painel', apelido=apelido)
                    else:
                        print("Falha no envio")
                        # data['result'] = "Falha no envio"
                        return redirect('url_painel', apelido=apelido)
                else:
                    print("Essa mensagem não é de " + apelido + ', portanto não pode responde-la.')
                    return redirect('url_painel', apelido=apelido)
            else:
                # Mensagem não encontrada
                return redirect('url_painel', apelido=apelido)
        else:
            return redirect('url_login')

    return render(request, 'painel/resposta.html', data)