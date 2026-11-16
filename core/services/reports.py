from io import BytesIO
from docx import Document
from docx.shared import Cm,Pt
from ..models import Indicador,Acao,Monitoramento

def criar_docx(rdqa):
 d=Document();section=d.sections[0]
 section.top_margin=Cm(2.5);section.bottom_margin=Cm(2.5)
 section.left_margin=Cm(3);section.right_margin=Cm(2)
 d.add_heading('SIS MONITORA — RDQA',0)
 d.add_paragraph(f'Relatório Detalhado do Quadrimestre Anterior · {rdqa.quadrimestre}º quadrimestre de {rdqa.ano}')
 d.add_paragraph('Versão de trabalho gerada pelo SIS Monitora. Exige validação e homologação institucional.')
 for bloco in rdqa.blocos.all():
  d.add_heading(bloco.titulo,level=2)
  d.add_paragraph(bloco.conteudo or 'Análise pendente de conferência pela área técnica.')
 d.add_paragraph('Fonte: registros estruturados do SIS Monitora; conferir documentos originais e data de corte.')
 data=BytesIO();d.save(data);return data.getvalue()

def construir_blocos(rdqa):
 from ..models import BlocoRDQA
 indic=Indicador.objects.filter(ano=rdqa.ano,quadrimestre=rdqa.quadrimestre).order_by('objetivo_codigo','codigo')
 n=0
 for obj in indic:
  titulo=f'Indicador {obj.codigo}: {obj.nome[:120]}'
  linhas=[f'Objetivo: {obj.objetivo or obj.objetivo_codigo or "Não informado"}',f'Meta: {obj.meta if obj.meta is not None else "Não informada"} {obj.unidade}',f'Resultado: {obj.resultado if obj.resultado is not None else "Não apurado"}',f'Desempenho: {obj.status}'+(f' ({obj.percentual}% da meta)' if obj.percentual is not None else '')]
  if obj.analise_area:linhas.append('Análise da área: '+obj.analise_area)
  else:linhas.append('Análise da área: pendente de inclusão.')
  chave='IND:'+obj.codigo
  BlocoRDQA.objects.get_or_create(documento=rdqa,chave=chave,defaults={'titulo':titulo,'tipo':'INDICADOR','conteudo':'\n'.join(linhas),'origem':'sistema','ordem':n})
  n+=1
 acoes=Acao.objects.filter(plano__ano=rdqa.ano,plano__ativo=True).distinct().order_by('numero')
 for acao in acoes:
  mon=Monitoramento.objects.filter(acao=acao,ano=rdqa.ano,quadrimestre=rdqa.quadrimestre).first()
  if not mon:continue
  linhas=[f'Ação {acao.numero}: {acao.descricao}',f'Situação: {mon.situacao or "Não informada"}',f'Análise: {mon.analise or "Pendente"}']
  for am in mon.atividades.select_related('atividade').all():linhas.append(f'Atividade {am.atividade.numero}: {am.atividade.descricao} — {am.get_status_display() if hasattr(am,"get_status_display") else am.status}')
  if mon.entraves:linhas.append('Entraves: '+mon.entraves)
  if mon.providencias:linhas.append('Providências: '+mon.providencias)
  BlocoRDQA.objects.get_or_create(documento=rdqa,chave='ACAO:'+str(acao.pk),defaults={'titulo':f'Ação PAS {acao.numero}','tipo':'OBJETIVO_ESTRATEGICO','conteudo':'\n'.join(linhas),'origem':'sistema','ordem':n})
  n+=1
 return n
