"""Importação em duas etapas: prévia + confirmação atômica. Nunca inventar valor de PDF."""
import csv,io
from django.db import transaction
from openpyxl import load_workbook
from pypdf import PdfReader
from ..models import Indicador,PlanoPAS,Acao,Atividade,Monitoramento,MonitoramentoAtividade,Auditoria
from .rules import dec,status_atividade
class ImportErrorUser(ValueError):pass

def extrair(upload):
 filename=upload.name.lower()
 if upload.size>10*1024*1024:raise ImportErrorUser('Limite de 10 MB por arquivo')
 content=upload.read()
 if filename.endswith('.pdf'):
  reader=PdfReader(io.BytesIO(content))
  texto='\n'.join((p.extract_text() or '') for p in reader.pages[:200])
  return [],texto[:150000],'PDF disponível apenas para conferência textual: conversão estruturada exige validação do parser institucional.'
 if filename.endswith('.csv'):
  raw=content.decode('utf-8-sig')
  linhas=list(csv.DictReader(io.StringIO(raw),delimiter=';' if raw[:2000].count(';')>raw[:2000].count(',') else ','))
 elif filename.endswith('.xlsx'):
  wb=load_workbook(io.BytesIO(content),read_only=True,data_only=True)
  sheet=wb.active;rows=sheet.iter_rows(values_only=True)
  header=[str(v).strip() if v is not None else '' for v in next(rows)]
  linhas=[dict(zip(header,[str(v) if v is not None else '' for v in row])) for row in rows]
 else:raise ImportErrorUser('Formato não suportado. Use CSV, XLSX ou PDF.')
 if len(linhas)>10000:raise ImportErrorUser('Limite de 10 mil registros por arquivo')
 return linhas,'','Prévia estruturada gerada. Confirme para gravar.'

def field(row,*names,default=''):
 norm={str(k).strip().lower().replace(' ','_'):v for k,v in row.items()}
 for key in names:
  value=norm.get(key.lower())
  if value is not None and str(value).strip()!='':return str(value).strip()
 return default
@transaction.atomic
def confirmar(batch,modo,autor):
 if batch.estado!='CONFERENCIA':raise ImportErrorUser('Lote já processado ou cancelado')
 if not batch.linhas:raise ImportErrorUser('PDF não pode ser gravado automaticamente sem dados estruturados validados')
 if modo not in ('manter','substituir'):raise ImportErrorUser('Escolha manter ou substituir registros duplicados')
 total=0;ignorados=0
 if batch.modulo=='PDS':
  for row in batch.linhas:
   codigo=field(row,'codigo','codigo_indicador')
   nome=field(row,'indicador','nome')
   if not codigo or not nome:raise ImportErrorUser('CSV PDS exige colunas codigo e indicador em todas as linhas')
   valores=dict(nome=nome,meta=dec(field(row,'meta','meta_anual')),
    resultado=dec(field(row,'resultado','resultado_periodo')),polaridade=field(row,'polaridade'),
    eixo=field(row,'eixo'),eixo_codigo=field(row,'eixo_codigo'),
    diretriz=field(row,'diretriz'),diretriz_codigo=field(row,'diretriz_codigo'),
    objetivo=field(row,'objetivo'),objetivo_codigo=field(row,'objetivo_codigo'),
    unidade=field(row,'unidade'),area=field(row,'area','area_responsavel'),
    analise_area=field(row,'analise','analise_resultado'),
    meta_original=field(row,'meta','meta_anual'),resultado_original=field(row,'resultado','resultado_periodo'),origem=batch)
   obj,created=Indicador.objects.get_or_create(ano=batch.ano,quadrimestre=batch.quadrimestre,codigo=codigo,defaults=valores)
   if created:total+=1
   elif modo=='substituir':
    for k,v in valores.items():setattr(obj,k,v)
    obj.save();total+=1
   else:ignorados+=1
 elif batch.modulo=='PAS':
  versao=field(batch.linhas[0],'versao',default='1')
  plano,_=PlanoPAS.objects.get_or_create(ano=batch.ano,versao=versao,defaults={'nome_arquivo':batch.arquivo})
  for row in batch.linhas:
   n=field(row,'numero_acao','acao_numero')
   if not n.isdigit() or not field(row,'descricao_acao','acao'):raise ImportErrorUser('PAS exige numero_acao e descricao_acao')
   values={'descricao':field(row,'descricao_acao','acao'),'area':field(row,'area'),'objetivo_codigo':field(row,'objetivo_codigo')}
   acao,cr=Acao.objects.get_or_create(plano=plano,numero=int(n),defaults=values)
   if not cr and modo=='substituir':
    for k,v in values.items():setattr(acao,k,v)
    acao.save()
   ati=field(row,'numero_atividade')
   if ati.isdigit() and field(row,'descricao_atividade'):
    Atividade.objects.update_or_create(acao=acao,numero=int(ati),defaults={'descricao':field(row,'descricao_atividade')}) if modo=='substituir' else Atividade.objects.get_or_create(acao=acao,numero=int(ati),defaults={'descricao':field(row,'descricao_atividade')})
   total+=1
 elif batch.modulo=='MON_PAS':
  for row in batch.linhas:
   na=field(row,'numero_acao')
   try:acao=Acao.objects.get(plano__ano=batch.ano,plano__ativo=True,numero=int(na))
   except (Acao.DoesNotExist,Acao.MultipleObjectsReturned,ValueError,TypeError):raise ImportErrorUser(f'Ação {na} não encontrada ou ambígua na PAS ativa do ano')
   m,_=Monitoramento.objects.get_or_create(acao=acao,ano=batch.ano,quadrimestre=batch.quadrimestre)
   if modo=='substituir' or not m.analise:
    m.situacao=field(row,'situacao_acao');m.analise=field(row,'analise','analise_texto');m.entraves=field(row,'entraves');m.providencias=field(row,'providencias');m.save()
   at=field(row,'numero_atividade')
   if at.isdigit():
    try:atividade=Atividade.objects.get(acao=acao,numero=int(at))
    except Atividade.DoesNotExist:raise ImportErrorUser(f'Atividade {at} ausente na ação {na}')
    status=field(row,'status_atividade') or status_atividade(field(row,'relato'))
    if status not in ('NAO_INICIADA','EM_ANDAMENTO','CONCLUIDA','NAO_INFORMADA'):raise ImportErrorUser('Status de atividade inválido: '+status)
    if modo=='substituir':MonitoramentoAtividade.objects.update_or_create(monitoramento=m,atividade=atividade,defaults={'status':status,'relato':field(row,'relato')})
    else:MonitoramentoAtividade.objects.get_or_create(monitoramento=m,atividade=atividade,defaults={'status':status,'relato':field(row,'relato')})
   total+=1
 batch.estado='CONFIRMADO';batch.save(update_fields=['estado','atualizado_em'])
 Auditoria.objects.create(autor=autor,acao='IMPORTAR',entidade=batch.modulo,referencia=str(batch.pk),detalhes={'gravados':total,'ignorados':ignorados,'modo':modo})
 return total,ignorados
