from django.urls import path
from . import views as v
urlpatterns=[
 path('login/',v.entrar,name='login'),path('solicitar-acesso/',v.solicitar_acesso,name='signup'),path('sair/',v.sair,name='logout'),
 path('',v.dashboard,name='dashboard'),path('indicadores/',v.indicadores,name='indicadores'),path('indicadores/<str:codigo>/',v.indicador,name='indicador'),
 path('objetivos/',v.objetivos,name='objetivos'),path('objetivos/<str:codigo>/',v.objetivo,name='objetivo'),
 path('serie-historica/',v.serie_historica,name='serie'),path('comparacao/',v.comparacao,name='comparacao'),
 path('pas/',v.pas,name='pas'),path('acoes/<int:numero>/',v.acao,name='acao'),path('validacao-vinculos/',v.validacao_vinculos,name='vinculos'),
 path('importacoes/',v.importacoes,name='importacoes'),path('importar/<str:modulo>/',v.importar,name='importar'),path('conferir/<uuid:pk>/',v.conferir,name='conferir'),
 path('rdqa/',v.rdqa,name='rdqa'),path('rdqa/<uuid:pk>/',v.rdqa_detalhe,name='rdqa_detalhe'),path('rdqa/<uuid:pk>/gerar/',v.rdqa_gerar_blocos,name='rdqa_gerar'),path('rdqa/<uuid:pk>/docx/',v.rdqa_download,name='rdqa_download'),
 path('analises/',v.analise_ia,name='analises'),path('qualidade/',v.qualidade,name='qualidade'),path('atualizacoes/',v.atualizacoes,name='atualizacoes'),
 path('exportar/',v.exportar,name='exportar'),path('admin-sis/',v.administrar,name='admin_sis'),
]
