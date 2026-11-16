from django.core.management.base import BaseCommand,CommandError
from django.conf import settings
from django.contrib.auth import get_user_model
from core.models import Indicador,PlanoPAS,Acao,Atividade,Monitoramento,MonitoramentoAtividade,RDQA
from core.services.reports import construir_blocos
class Command(BaseCommand):
 help='Cria dados fictícios de demonstração (APENAS SIS_DEMO_MODE=true).'
 def add_arguments(self,parser):parser.add_argument('--password',default='Demo@12345')
 def handle(self,*args,**opts):
  if not settings.SIS_DEMO_MODE:raise CommandError('Bloqueado fora de SIS_DEMO_MODE')
  User=get_user_model();u,cr=User.objects.get_or_create(username='admin@demo.local',defaults={'email':'admin@demo.local','is_staff':True,'is_superuser':True})
  if cr:u.set_password(opts['password']);u.save()
  else:self.stdout.write('Administrador já existe. Senha não alterada.')
  defs=[('PDS001','Cobertura da Atenção Primária',80,74,'Maior - melhor','Objetivo 1 - Qualificar a APS'),('PDS002','Taxa de internações evitáveis',12,10,'Menor - melhor','Objetivo 1 - Qualificar a APS'),('PDS003','Tempo de espera para atendimento',20,None,'Menor - melhor','Objetivo 2 - Melhorar o acesso'),('PDS004','Cobertura de vigilância territorial',75,85,'Maior - melhor','Objetivo 3 - Fortalecer a vigilância')]
  for q in [1,2,3]:
   for c,n,m,r,p,o in defs:
    v=None if r is None else r+(q-2)*2
    Indicador.objects.get_or_create(ano=2026,quadrimestre=q,codigo=c,defaults={'nome':n,'meta':m,'resultado':v,'polaridade':p,'objetivo_codigo':o.split(' - ')[0],'objetivo':o,'eixo':'Gestão e Atenção à Saúde','diretriz':'Fortalecimento da Rede de Saúde','area':'Área técnica demonstrativa','unidade':'%','analise_area':'Dados exclusivamente fictícios para testes de fluxo.'})
  plano,_=PlanoPAS.objects.get_or_create(ano=2026,versao='DEMO-1')
  for n,t,ativs in [(1,'Qualificar o monitoramento da atenção primária',['Realizar diagnóstico territorial','Atualizar painel de indicadores']),(2,'Fortalecer a vigilância em saúde',['Revisar fluxos de coleta','Capacitar equipes'])]:
   a,_=Acao.objects.get_or_create(plano=plano,numero=n,defaults={'descricao':t,'objetivo_codigo':'Objetivo 1' if n==1 else 'Objetivo 3','area':'SES-DF (fictício)'})
   for k,at in enumerate(ativs,1):
    t,_=Atividade.objects.get_or_create(acao=a,numero=k,defaults={'descricao':at})
   m,_=Monitoramento.objects.get_or_create(acao=a,ano=2026,quadrimestre=2,defaults={'situacao':'Em andamento','analise':'Registro de demonstração; não representa a realidade da SES-DF.'})
   for at in a.atividades.all():MonitoramentoAtividade.objects.get_or_create(monitoramento=m,atividade=at,defaults={'status':'EM_ANDAMENTO'})
  doc,_=RDQA.objects.get_or_create(ano=2026,quadrimestre=2)
  construir_blocos(doc)
  self.stdout.write(self.style.SUCCESS('Dados fictícios gerados. Login: admin@demo.local / senha configurada no comando.'))
