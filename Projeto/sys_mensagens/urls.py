"""sys_mensagens URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from mensagens.views import login, novo, painel, novaMsg

urlpatterns = [
    path('painel/<slug:apelido>', painel, name='url_painel'),
    path('painel/<slug:apelido>/nova', novaMsg, name='url_nova_msg'),
    path('painel/<slug:apelido>/resposta', painel, name='url_nova_resposta'),
    path('login/', login, name='url_login'),
    path('novo/', novo, name='url_novo'),
]
