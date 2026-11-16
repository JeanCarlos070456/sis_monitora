"""Executável sem Django: python -m unittest discover -s tests -v"""
import unittest
from decimal import Decimal
from core.services.rules import desempenho,comparar,BIMESTRE,status_atividade
class TestPDS(unittest.TestCase):
 def test_maior_melhor(self):
  p=desempenho(80,72,'Maior - melhor');self.assertEqual(p['percentual'],Decimal('90.00'));self.assertEqual(p['status'],'Ótimo')
 def test_maior_acima_meta(self):self.assertEqual(desempenho(30,40,'Maior - melhor')['percentual'],Decimal('133.33'))
 def test_menor_abaixo_meta(self):self.assertEqual(desempenho(10,8,'Menor - melhor')['percentual'],Decimal('100.00'))
 def test_menor_acima_meta(self):self.assertEqual(desempenho(10,20,'Menor - melhor')['status'],'Médio')
 def test_meta_zero_menor_zero(self):self.assertEqual(desempenho(0,0,'Menor - melhor')['status'],'Ótimo')
 def test_meta_zero_menor_positivo(self):self.assertEqual(desempenho(0,5,'Menor - melhor')['status'],'Insuficiente')
 def test_meta_zero_maior(self):self.assertEqual(desempenho(0,5,'Maior - melhor')['status'],'Não calculável')
 def test_null_distinto_zero(self):self.assertEqual(desempenho(10,None,'Maior - melhor')['status'],'Não apurado')
 def test_polaridade_ausente(self):self.assertEqual(desempenho(10,5,'')['status'],'Não calculável')
 def test_limites(self):
  for pct,status in [(49,'Insuficiente'),(50,'Médio'),(69,'Médio'),(70,'Bom'),(89,'Bom'),(90,'Ótimo')]:self.assertEqual(desempenho(100,pct,'Maior - melhor')['status'],status)
 def test_variacao(self):self.assertEqual(comparar(15,10,'Menor - melhor')['tendencia'],'Piora')
 def test_sem_anterior(self):self.assertEqual(comparar(15,None,'Maior - melhor')['tendencia'],'Sem comparação')
 def test_bimestre(self):self.assertEqual(BIMESTRE[2],'Julho/Agosto')
 def test_status_expresso(self):self.assertEqual(status_atividade('atividade não iniciada'),'NAO_INICIADA')
if __name__=='__main__':unittest.main()
