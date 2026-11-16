"""Supabase Auth login. JWT validado no serviço Supabase, papéis consultados com JWT e RLS."""
import requests
from django.conf import settings
class AuthProblem(Exception):pass

def request_json(method,path,token=None,payload=None):
 if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:raise AuthProblem('Supabase não configurado')
 headers={'apikey':settings.SUPABASE_ANON_KEY,'Content-Type':'application/json'}
 if token:headers['Authorization']='Bearer '+token
 try:
  r=requests.request(method,settings.SUPABASE_URL+path,json=payload,headers=headers,timeout=15)
  if r.status_code>=400:raise AuthProblem('Supabase recusou a operação. Verifique credenciais, aprovação e RLS.')
  return r.json()
 except requests.RequestException as e:raise AuthProblem('Supabase indisponível: '+str(e)) from e

def login(email,password):
 data=request_json('POST','/auth/v1/token?grant_type=password',payload={'email':email,'password':password})
 jwt=data.get('access_token');user=data.get('user') or {}
 if not jwt or not user.get('id'):raise AuthProblem('Resposta de autenticação inválida')
 role=request_json('GET',f'/rest/v1/user_roles?user_id=eq.{user["id"]}&select=role,approved',token=jwt)
 if not role or not role[0].get('approved'):raise AuthProblem('Acesso pendente de aprovação por administrador')
 return user,role[0],data

def signup(email,password):
 return request_json('POST','/auth/v1/signup',payload={'email':email,'password':password})
