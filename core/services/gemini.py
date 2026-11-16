"""Gemini server-side; never expose API key to browser; no fallback provider."""
import requests
from django.conf import settings
class GeminiError(Exception):pass
def analisar(prompt):
 if not settings.GEMINI_API_KEY:raise GeminiError('GEMINI_API_KEY não configurada. Análise não executada.')
 modelo=settings.GEMINI_MODEL
 url=f'https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent'
 try:
  r=requests.post(url,params={'key':settings.GEMINI_API_KEY},json={'contents':[{'role':'user','parts':[{'text':prompt[:22000]}]}],'generationConfig':{'temperature':0.2,'maxOutputTokens':1300}},timeout=45)
  r.raise_for_status()
  data=r.json();parts=data.get('candidates',[{}])[0].get('content',{}).get('parts',[])
  texto='\n'.join(p.get('text','') for p in parts).strip()
  if not texto:raise GeminiError('Gemini não retornou texto. Verifique segurança, limites e cotas.')
  return texto
 except requests.RequestException as e:raise GeminiError('Falha na chamada Gemini: '+str(e)) from e
