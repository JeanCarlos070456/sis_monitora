from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse,HttpResponseBadRequest
from django.contrib.auth import authenticate,login as dj_login,logout as dj_logout,get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Count
from django.conf import settings
from django.views.decorators.http import require_POST
from django.utils.text import slugify
from .models import *
from .services.rules import comparar,BIMESTRE,STATUS_ATIVIDADE
from .services import importer,gemini,reports,supabase_auth

def layout(request,title,**kwargs):
 kwargs['titulo']=title
 return kwargs

def gerente(user):return user.is_authenticated and user.is_staff

def exige_gerente(request):
 if not gerente(request.user):
  messages.error(request,'Ação exclusiva de administrador aprovado.')
  return False
 return True

def audit(user,acao,entidade,ref,**data):
 Auditoria.objects.create(autor=user.get_username(),acao=acao,entidade=entidade,referencia=str(ref),detalhes=data)

def entrar(request):
 if request.user.is_authenticated:return redirect('dashboard')
 if request.method=='POST':
  email=(request.POST.get('email') or '').strip().lower();senha=request.POST.get('password','')
  if settings.SIS_DEMO_MODE:
   user=authenticate(request,username=email,password=senha)
   if user and user.is_active:dj_login(request,user);return redirect('dashboard')
   messages.error(request,'E-mail ou senha inválidos no ambiente demonstrativo.')
  else:
   try:
    payload,role,data=supabase_auth.login(email,senha)
    User=get_user_model()
    user,_=User.objects.get_or_create(username='sb_'+payload['id'],defaults={'email':email})
    user.email=email;user.is_staff=role['role']=='admin';user.set_unusable_password();user.save()
    user.backend='django.contrib.auth.backends.ModelBackend';dj_login(request,user)
    request.session['supabase_access_token']=data['access_token']
    request.session['supabase_refresh_token']=data.get('refresh_token','')
    request.session['supabase_user_id']=payload['id']
    return redirect('dashboard')
   except supabase_auth.AuthProblem as exc:messages.error(request,str(exc))
 return render(request,'registration/login.html')

def solicitar_acesso(request):
 if request.method=='POST':
  if settings.SIS_DEMO_MODE:messages.info(request,'Solicitações são simuladas no modo demo. Consulte o administrador local.')
  else:
   try:
    supabase_auth.signup(request.POST.get('email',''),request.POST.get('password',''))
    messages.success(request,'Solicitação enviada. Verifique o e-mail e aguarde aprovação.')
   except supabase_auth.AuthProblem as exc:messages.error(request,str(exc))
  return redirect('login')
 return render(request,'registration/signup.html')

@require_POST
@login_required
def sair(request):dj_logout(request);return redirect('login')

@login_required
def dashboard(request):
 cards={'indicadores':Indicador.objects.values('codigo').distinct().count(),'acoes':Acao.objects.count(),'atividades':Atividade.objects.count(),'rdqas':RDQA.objects.count()}
 recentes=Indicador.objects.order_by('-criado_em')[:8]
 periodos=Indicador.objects.values('ano','quadrimestre').annotate(total=Count('id')).order_by('-ano','-quadrimestre')[:9]
 return render(request,'dashboard.html',layout(request,'Visão geral',cards=cards,recentes=recentes,periodos=periodos))

@login_required
def indicadores(request):
 qs=Indicador.objects.all()
 termo=request.GET.get('q','').strip();ano=request.GET.get('ano','')
 if termo:
  from django.db.models import Q
  qs=qs.filter(Q(codigo__icontains=termo)|Q(nome__icontains=termo)|Q(objetivo__icontains=termo))
 if ano.isdigit():qs=qs.filter(ano=int(ano))
 return render(request,'indicadores.html',layout(request,'Indicadores do PDS',itens=qs.order_by('codigo','-ano','-quadrimestre')[:350],q=termo,ano=ano))

@login_required
def indicador(request,codigo):
 qs=Indicador.objects.filter(codigo=codigo).order_by('ano','quadrimestre')
 atual=qs.last()
 if not atual:return HttpResponse('Indicador não encontrado',status=404)
 serie=list(qs);dados=[]
 for i,item in enumerate(serie):
  ant=serie[i-1] if i else None
  dados.append({'item':item,'comparacao':comparar(item.resultado,ant.resultado if ant else None,item.polaridade)})
 analises=AnaliseIA.objects.filter(referencia=codigo)[:10]
 return render(request,'indicador.html',layout(request,'Detalhe do indicador',item=atual,serie=dados,analises=analises))

@login_required
def objetivos(request):
 rows=Indicador.objects.exclude(objetivo='').values('objetivo_codigo','objetivo').annotate(total=Count('codigo',distinct=True)).order_by('objetivo_codigo')
 return render(request,'objetivos.html',layout(request,'Objetivos estratégicos',itens=rows))

@login_required
def objetivo(request,codigo):
 rows=Indicador.objects.filter(objetivo_codigo=codigo).order_by('codigo','ano')
 return render(request,'indicadores.html',layout(request,f'Objetivo {codigo}',itens=rows,q='',ano=''))

@login_required
def serie_historica(request):
 codigos=Indicador.objects.values_list('codigo',flat=True).distinct().order_by('codigo')
 codigo=request.GET.get('codigo') or (codigos.first() if codigos.exists() else '')
 serie=Indicador.objects.filter(codigo=codigo).order_by('ano','quadrimestre')
 return render(request,'serie.html',layout(request,'Série histórica',codigos=codigos,codigo=codigo,serie=serie))

@login_required
def comparacao(request):
 anos=list(Indicador.objects.values_list('ano',flat=True).distinct().order_by('-ano'))
 ano=int(request.GET.get('ano')) if request.GET.get('ano','').isdigit() else (anos[0] if anos else 2026)
 itens=Indicador.objects.filter(ano=ano).order_by('codigo','quadrimestre')[:400]
 return render(request,'indicadores.html',layout(request,f'Comparação PDS — {ano}',itens=itens,q='',ano=str(ano)))

@login_required
def pas(request):
 planos=PlanoPAS.objects.prefetch_related('acoes').all()
 acoes=Acao.objects.select_related('plano').prefetch_related('atividades').all()[:250]
 return render(request,'pas.html',layout(request,'Programação Anual de Saúde',planos=planos,acoes=acoes))

@login_required
def acao(request,numero):
 qs=Acao.objects.filter(numero=numero).select_related('plano').prefetch_related('atividades').order_by('-plano__ano','-plano__criado_em')
 obj=qs.first()
 if not obj:return HttpResponse('Ação não encontrada',status=404)
 if request.method=='POST':
  if not exige_gerente(request):return redirect('acao',numero=numero)
  try:
   ano=int(request.POST['ano']);q=int(request.POST['quadrimestre'])
   if q not in (1,2,3):raise ValueError()
   m,_=Monitoramento.objects.update_or_create(acao=obj,ano=ano,quadrimestre=q,defaults={'situacao':request.POST.get('situacao',''),'analise':request.POST.get('analise',''),'entraves':request.POST.get('entraves',''),'providencias':request.POST.get('providencias','')})
   for at in obj.atividades.all():
    st=request.POST.get('atividade_'+str(at.pk),'NAO_INFORMADA')
    if st in STATUS_ATIVIDADE:MonitoramentoAtividade.objects.update_or_create(monitoramento=m,atividade=at,defaults={'status':st,'confirmado':True})
   audit(request.user,'MONITORAR','PAS',obj.pk,ano=ano,quadrimestre=q)
   messages.success(request,'Monitoramento registrado.')
  except (ValueError,KeyError):messages.error(request,'Ano ou quadrimestre inválido.')
  return redirect('acao',numero=numero)
 return render(request,'acao.html',layout(request,f'Ação PAS {numero}',acao=obj,monitoramentos=obj.monitoramentos.prefetch_related('atividades').all(),status_opts=STATUS_ATIVIDADE))

@login_required
def validacao_vinculos(request):
 qs=Acao.objects.select_related('plano').all()[:300]
 if request.method=='POST' and exige_gerente(request):
  a=get_object_or_404(Acao,pk=request.POST.get('acao_id'))
  indicador=get_object_or_404(Indicador,pk=request.POST.get('indicador_id'))
  if request.POST.get('operacao')=='remover':a.indicadores.remove(indicador)
  else:a.indicadores.add(indicador)
  audit(request.user,'VINCULAR','PAS',a.pk,indicador=str(indicador.pk));messages.success(request,'Vínculo atualizado.');return redirect('vinculos')
 inds=Indicador.objects.order_by('codigo','-ano')[:500]
 return render(request,'vinculos.html',layout(request,'Validação de vínculos PDS × PAS',acoes=qs,indicadores=inds))

@login_required
def importacoes(request):
 return render(request,'importacoes.html',layout(request,'Importações e conferência',lotes=ImportBatch.objects.all()[:100]))

@login_required
def importar(request,modulo='PDS'):
 if modulo not in ('PDS','PAS','MON_PAS'):return HttpResponseBadRequest('Módulo inválido')
 if request.method=='POST':
  if not exige_gerente(request):return redirect('importacoes')
  upload=request.FILES.get('arquivo')
  if not upload:messages.error(request,'Selecione o arquivo.');return redirect('importar',modulo=modulo)
  try:
   ano=int(request.POST.get('ano',''));q=int(request.POST.get('quadrimestre','1'))
   if not 2020<=ano<=2100 or q not in (1,2,3):raise ValueError()
   linhas,texto,alerta=importer.extrair(upload)
   lote=ImportBatch.objects.create(modulo=modulo,arquivo=upload.name[:260],ano=ano,quadrimestre=q,linhas=linhas,texto_bruto=texto,observacao=alerta,criado_por=request.user.get_username())
   return redirect('conferir',pk=lote.pk)
  except (ValueError,importer.ImportErrorUser) as exc:messages.error(request,str(exc))
 return render(request,'importar.html',layout(request,'Importar '+modulo,modulo=modulo))

@login_required
def conferir(request,pk):
 lote=get_object_or_404(ImportBatch,pk=pk)
 if request.method=='POST':
  if not exige_gerente(request):return redirect('importacoes')
  try:
   if request.POST.get('acao')=='cancelar':lote.estado='CANCELADO';lote.save();messages.info(request,'Importação cancelada.')
   else:
    n,ign=importer.confirmar(lote,request.POST.get('modo','manter'),request.user.get_username())
    messages.success(request,f'Importação concluída: {n} registros processados; {ign} mantidos sem alteração.')
   return redirect('importacoes')
  except (importer.ImportErrorUser,ValueError) as exc:messages.error(request,str(exc))
 return render(request,'conferir.html',layout(request,'Conferência de importação',lote=lote,linhas=lote.linhas[:30]))

@login_required
def rdqa(request):
 if request.method=='POST':
  if not exige_gerente(request):return redirect('rdqa')
  try:
   ano=int(request.POST.get('ano',''));q=int(request.POST.get('quadrimestre',''))
   if q not in (1,2,3):raise ValueError()
   doc,cr=RDQA.objects.get_or_create(ano=ano,quadrimestre=q)
   if cr:reports.construir_blocos(doc)
   messages.success(request,'Documento criado ou localizado. Blocos existentes não foram sobrescritos.')
   return redirect('rdqa_detalhe',pk=doc.pk)
  except ValueError:messages.error(request,'Informe ano e quadrimestre válidos.')
 return render(request,'rdqa.html',layout(request,'Relatório RDQA',documentos=RDQA.objects.order_by('-ano','-quadrimestre')))

@login_required
def rdqa_detalhe(request,pk):
 doc=get_object_or_404(RDQA,pk=pk)
 if request.method=='POST':
  if not exige_gerente(request):return redirect('rdqa_detalhe',pk=pk)
  if doc.status=='homologado':messages.error(request,'Documento homologado está bloqueado.');return redirect('rdqa_detalhe',pk=pk)
  bloco=get_object_or_404(BlocoRDQA,pk=request.POST.get('bloco_id'),documento=doc)
  bloco.conteudo=request.POST.get('conteudo','')[:35000];bloco.origem='manual';bloco.editado_por=request.user.get_username();bloco.save()
  audit(request.user,'EDITAR_BLOCO','RDQA',bloco.pk)
  messages.success(request,'Bloco atualizado.');return redirect('rdqa_detalhe',pk=pk)
 return render(request,'rdqa_detalhe.html',layout(request,f'RDQA {doc.quadrimestre}º/{doc.ano}',doc=doc,blocos=doc.blocos.all()))

@login_required
def rdqa_gerar_blocos(request,pk):
 if request.method!='POST':return HttpResponse(status=405)
 if not exige_gerente(request):return redirect('rdqa_detalhe',pk=pk)
 doc=get_object_or_404(RDQA,pk=pk)
 if doc.status!='homologado':
  n=reports.construir_blocos(doc);messages.success(request,f'{n} blocos de origem identificados; edições preservadas.')
 return redirect('rdqa_detalhe',pk=pk)

@login_required
def rdqa_download(request,pk):
 doc=get_object_or_404(RDQA,pk=pk);data=reports.criar_docx(doc)
 r=HttpResponse(data,content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
 r['Content-Disposition']=f'attachment; filename="RDQA_{doc.ano}_Q{doc.quadrimestre}.docx"';return r

@login_required
def analise_ia(request):
 if request.method=='POST':
  if not exige_gerente(request):return redirect('analises')
  codigo=request.POST.get('codigo','').strip();item=Indicador.objects.filter(codigo=codigo).order_by('-ano','-quadrimestre').first()
  if not item:messages.error(request,'Indicador não encontrado.');return redirect('analises')
  contexto=f'Indicador: {item.nome}\nCódigo: {item.codigo}\nMeta: {item.meta}\nResultado: {item.resultado}\nStatus calculado: {item.status}\nAnálise da área: {item.analise_area}'
  prompt=('Produza uma análise técnica prudente de monitoramento do PDS SES-DF usando SOMENTE os dados fornecidos. Não invente causas, fontes, números ou conclusões. Identifique lacunas e sinalize necessidade de validação humana.\n'+contexto)
  try:
   resposta=gemini.analisar(prompt)
   AnaliseIA.objects.create(tipo='indicador',referencia=codigo,pergunta=prompt,resposta=resposta,modelo=settings.GEMINI_MODEL,gerado_por=request.user.get_username())
   messages.success(request,'Análise gerada para conferência humana.');return redirect('indicador',codigo=codigo)
  except gemini.GeminiError as exc:messages.error(request,str(exc))
 return render(request,'analises.html',layout(request,'Análises com Gemini',analises=AnaliseIA.objects.all()[:60],codigos=Indicador.objects.values_list('codigo',flat=True).distinct().order_by('codigo')))

@login_required
def qualidade(request):
 nao=Indicador.objects.filter(status='Não calculável').order_by('-criado_em')[:100]
 faltando=Indicador.objects.filter(status='Não apurado').order_by('-criado_em')[:100]
 return render(request,'qualidade.html',layout(request,'Qualidade dos dados',nao=nao,faltando=faltando))

@login_required
def atualizacoes(request):
 return render(request,'atualizacoes.html',layout(request,'Histórico de atualizações',auditorias=Auditoria.objects.all()[:150],lotes=ImportBatch.objects.all()[:40]))

@login_required
def exportar(request):
 import csv
 tabela=request.GET.get('tabela','indicadores')
 r=HttpResponse(content_type='text/csv; charset=utf-8');r.write('\ufeff');r['Content-Disposition']=f'attachment; filename="sismonitora_{tabela}.csv"'
 w=csv.writer(r,delimiter=';')
 if tabela=='indicadores':
  w.writerow(['ano','quadrimestre','codigo','indicador','objetivo','meta','resultado','polaridade','percentual','status','analise_area'])
  for i in Indicador.objects.all():w.writerow([i.ano,i.quadrimestre,i.codigo,i.nome,i.objetivo,i.meta,i.resultado,i.polaridade,i.percentual,i.status,i.analise_area])
 elif tabela=='acoes':
  w.writerow(['ano','versao','numero','descricao','area','objetivo_codigo'])
  for a in Acao.objects.select_related('plano'):w.writerow([a.plano.ano,a.plano.versao,a.numero,a.descricao,a.area,a.objetivo_codigo])
 else:return HttpResponseBadRequest('Exportação não suportada')
 return r

@login_required
def administrar(request):
 if not exige_gerente(request):return redirect('dashboard')
 users=get_user_model().objects.all().order_by('username')[:100]
 return render(request,'admin_sis.html',layout(request,'Administração',usuarios=users))
