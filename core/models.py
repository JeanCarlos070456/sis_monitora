import uuid
from django.db import models
from .services.rules import desempenho,BIMESTRE

def uid():return uuid.uuid4()
class AuditMixin(models.Model):
 id=models.UUIDField(primary_key=True,default=uid,editable=False)
 criado_em=models.DateTimeField(auto_now_add=True)
 atualizado_em=models.DateTimeField(auto_now=True)
 class Meta:abstract=True
class ImportBatch(AuditMixin):
 MODULOS=[('PDS','PDS'),('PAS','PAS'),('MON_PAS','Monitoramento PAS')]
 modulo=models.CharField(max_length=15,choices=MODULOS)
 arquivo=models.CharField(max_length=260)
 ano=models.PositiveIntegerField();quadrimestre=models.PositiveSmallIntegerField(default=1)
 estado=models.CharField(max_length=24,default='CONFERENCIA')
 linhas=models.JSONField(default=list,blank=True)
 texto_bruto=models.TextField(blank=True)
 observacao=models.TextField(blank=True)
 criado_por=models.CharField(max_length=254,blank=True)
 class Meta:ordering=['-criado_em']
class Indicador(AuditMixin):
 ano=models.PositiveIntegerField();quadrimestre=models.PositiveSmallIntegerField()
 codigo=models.CharField(max_length=100);nome=models.TextField()
 eixo_codigo=models.CharField(max_length=30,blank=True);eixo=models.CharField(max_length=255,blank=True)
 perspectiva_codigo=models.CharField(max_length=30,blank=True);perspectiva=models.CharField(max_length=255,blank=True)
 diretriz_codigo=models.CharField(max_length=30,blank=True);diretriz=models.TextField(blank=True)
 objetivo_codigo=models.CharField(max_length=80,blank=True);objetivo=models.TextField(blank=True)
 meta=models.DecimalField(max_digits=18,decimal_places=4,null=True,blank=True)
 resultado=models.DecimalField(max_digits=18,decimal_places=4,null=True,blank=True)
 meta_original=models.CharField(max_length=100,blank=True);resultado_original=models.CharField(max_length=100,blank=True)
 unidade=models.CharField(max_length=40,blank=True);polaridade=models.CharField(max_length=40,blank=True)
 monitoramento=models.CharField(max_length=80,blank=True);acumulativo=models.BooleanField(default=False)
 area=models.CharField(max_length=250,blank=True);analise_area=models.TextField(blank=True);registrado_por=models.CharField(max_length=150,blank=True)
 percentual=models.DecimalField(max_digits=16,decimal_places=2,null=True,blank=True)
 status=models.CharField(max_length=35,default='Não apurado');diferenca=models.DecimalField(max_digits=18,decimal_places=2,null=True,blank=True)
 origem=models.ForeignKey(ImportBatch,on_delete=models.SET_NULL,null=True,blank=True,related_name='indicadores')
 class Meta:
  constraints=[models.UniqueConstraint(fields=['ano','quadrimestre','codigo'],name='uniq_pds_ano_quad_codigo')]
  ordering=['codigo','ano','quadrimestre']
 def save(self,*a,**kw):
  c=desempenho(self.meta,self.resultado,self.polaridade)
  self.percentual,self.status,self.diferenca=c['percentual'],c['status'],c['diferenca']
  super().save(*a,**kw)
 @property
 def periodo(self):return f'{self.quadrimestre}º quadrimestre/{self.ano}'
class PlanoPAS(AuditMixin):
 ano=models.PositiveIntegerField();versao=models.CharField(max_length=80,default='1')
 ativo=models.BooleanField(default=True);nome_arquivo=models.CharField(max_length=260,blank=True)
 observacoes=models.TextField(blank=True)
 class Meta:
  constraints=[models.UniqueConstraint(fields=['ano','versao'],name='uniq_pas_ano_versao')]
  ordering=['-ano','-criado_em']
 def __str__(self):return f'PAS {self.ano} — {self.versao}'
class Acao(AuditMixin):
 plano=models.ForeignKey(PlanoPAS,on_delete=models.CASCADE,related_name='acoes')
 numero=models.PositiveIntegerField();descricao=models.TextField();area=models.CharField(max_length=260,blank=True)
 objetivo_codigo=models.CharField(max_length=80,blank=True)
 indicadores=models.ManyToManyField('Indicador',blank=True,related_name='acoes')
 class Meta:
  constraints=[models.UniqueConstraint(fields=['plano','numero'],name='uniq_pas_plano_acao')]
  ordering=['numero']
class Atividade(AuditMixin):
 acao=models.ForeignKey(Acao,on_delete=models.CASCADE,related_name='atividades')
 numero=models.PositiveIntegerField();descricao=models.TextField()
 class Meta:
  constraints=[models.UniqueConstraint(fields=['acao','numero'],name='uniq_pas_acao_atividade')]
  ordering=['numero']
class Monitoramento(AuditMixin):
 acao=models.ForeignKey(Acao,on_delete=models.CASCADE,related_name='monitoramentos')
 ano=models.PositiveIntegerField();quadrimestre=models.PositiveSmallIntegerField()
 situacao=models.CharField(max_length=100,blank=True);analise=models.TextField(blank=True)
 entraves=models.TextField(blank=True);providencias=models.TextField(blank=True)
 class Meta:constraints=[models.UniqueConstraint(fields=['acao','ano','quadrimestre'],name='uniq_mon_acao_periodo')]
 @property
 def bimestre(self):return BIMESTRE.get(self.quadrimestre,'')
class MonitoramentoAtividade(AuditMixin):
 monitoramento=models.ForeignKey(Monitoramento,on_delete=models.CASCADE,related_name='atividades')
 atividade=models.ForeignKey(Atividade,on_delete=models.CASCADE)
 status=models.CharField(max_length=30,default='NAO_INFORMADA');relato=models.TextField(blank=True)
 confirmado=models.BooleanField(default=False)
 class Meta:constraints=[models.UniqueConstraint(fields=['monitoramento','atividade'],name='uniq_mon_atividade')]
class RDQA(AuditMixin):
 ano=models.PositiveIntegerField();quadrimestre=models.PositiveSmallIntegerField()
 status=models.CharField(max_length=24,default='em_edicao')
 observacoes=models.TextField(blank=True);data_fonte=models.DateField(null=True,blank=True)
 class Meta:constraints=[models.UniqueConstraint(fields=['ano','quadrimestre'],name='uniq_rdqa_periodo')]
class BlocoRDQA(AuditMixin):
 documento=models.ForeignKey(RDQA,on_delete=models.CASCADE,related_name='blocos')
 chave=models.CharField(max_length=180);titulo=models.TextField();tipo=models.CharField(max_length=30,default='INDICADOR')
 conteudo=models.TextField(blank=True);origem=models.CharField(max_length=30,default='manual')
 ordem=models.PositiveIntegerField(default=0);editado_por=models.CharField(max_length=254,blank=True)
 class Meta:
  constraints=[models.UniqueConstraint(fields=['documento','chave'],name='uniq_rdqa_bloco_chave')]
  ordering=['ordem','titulo']
class AnaliseIA(AuditMixin):
 tipo=models.CharField(max_length=60);referencia=models.CharField(max_length=255)
 pergunta=models.TextField();resposta=models.TextField();modelo=models.CharField(max_length=100)
 gerado_por=models.CharField(max_length=254)
 class Meta:ordering=['-criado_em']
class Auditoria(AuditMixin):
 autor=models.CharField(max_length=254);acao=models.CharField(max_length=100);entidade=models.CharField(max_length=80)
 referencia=models.CharField(max_length=255);detalhes=models.JSONField(default=dict,blank=True)
 class Meta:ordering=['-criado_em']
