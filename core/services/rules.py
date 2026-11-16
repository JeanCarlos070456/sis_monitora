"""Port fiel das regras base de src/lib/pds/calculos.ts e pas/regras.ts do Lovable."""
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import re,unicodedata
STATUSES=('Insuficiente','Médio','Bom','Ótimo')
def dec(v):
 if v is None or v=='':return None
 if isinstance(v,Decimal):return v
 s=str(v).strip().replace('R$','').replace('%','').replace(' ','')
 if ',' in s:s=s.replace('.','').replace(',','.')
 try:return Decimal(s)
 except InvalidOperation:return None

def arred(v):return v.quantize(Decimal('0.01'),rounding=ROUND_HALF_UP) if v is not None else None

def desempenho(meta,resultado,polaridade):
 m,r=dec(meta),dec(resultado)
 if r is None:return {'percentual':None,'status':'Não apurado','diferenca':None}
 pol=(polaridade or '').lower()
 if m is None or not ('maior' in pol or 'menor' in pol):return {'percentual':None,'status':'Não calculável','diferenca':None}
 if 'maior' in pol:
  if m==0:return {'percentual':None,'status':'Não calculável','diferenca':None}
  p=(r/m)*100;dif=r-m
 else:
  if m==0:p=Decimal(100) if r==0 else Decimal(0)
  elif r<=m:p=Decimal(100)
  else:p=(m/r)*100
  dif=m-r
 status='Insuficiente' if p<50 else 'Médio' if p<70 else 'Bom' if p<90 else 'Ótimo'
 return {'percentual':arred(p),'status':status,'diferenca':arred(dif)}

def comparar(atual,anterior,polaridade):
 a,b=dec(atual),dec(anterior)
 if a is None or b is None:return {'variacao_absoluta':None,'variacao_percentual':None,'tendencia':'Sem comparação'}
 pol=(polaridade or '').lower()
 tendencia=('Estabilidade' if a==b else 'Melhora' if (a>b and 'maior' in pol) or (a<b and 'menor' in pol) else 'Piora') if ('maior' in pol or 'menor' in pol) else 'Sem comparação'
 return {'variacao_absoluta':arred(a-b),'variacao_percentual':arred((a-b)/b*100) if b!=0 else None,'tendencia':tendencia}
BIMESTRE={1:'Março/Abril',2:'Julho/Agosto',3:'Novembro/Dezembro'}
STATUS_ATIVIDADE={'NAO_INICIADA':'Não iniciada','EM_ANDAMENTO':'Em andamento','CONCLUIDA':'Concluída','NAO_INFORMADA':'Não informada'}
def status_atividade(texto):
 s=''.join(x for x in unicodedata.normalize('NFD',texto or '') if unicodedata.category(x)!='Mn').lower()
 if re.search(r'\b(concluida|concluido|finalizada)\b',s):return 'CONCLUIDA'
 if re.search(r'\bnao iniciad[ao]\b',s):return 'NAO_INICIADA'
 if re.search(r'\b(em andamento|andamento|iniciada)\b',s):return 'EM_ANDAMENTO'
 return 'NAO_INFORMADA'
