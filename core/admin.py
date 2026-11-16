from django.contrib import admin
from .models import *
for model in [ImportBatch,Indicador,PlanoPAS,Acao,Atividade,Monitoramento,MonitoramentoAtividade,RDQA,BlocoRDQA,AnaliseIA,Auditoria]:admin.site.register(model)
