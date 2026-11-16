# SIS Monitora · Django / Python · Versão de testes (0.1)

**Escopo:** implementação inicial funcional para testes e evolução — **não é cópia 100% equivalente ao Lovable nem sistema homologado para produção.** O repositório Lovable foi usado como fonte de engenharia reversa. A stack principal atende à decisão da equipe: Python, Django Templates, Supabase PostgreSQL/Auth, Render, Gemini, CSS e JS.

## Começar agora — Windows

1. Instale Python 3.12 ou 3.13 e certifique-se de que `py` funciona no terminal.
2. Extraia este ZIP para uma pasta local.
3. Execute `INICIAR_WINDOWS.bat` ou, no PowerShell, use os comandos abaixo.
4. Abra `http://127.0.0.1:8000/login/`.
5. Acesse com `admin@demo.local` e senha `Demo@12345`. **Somente para ambiente local de demonstração.**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py makemigrations core
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Se o PowerShell bloquear a ativação, use `.venv\Scripts\python.exe` em todos os comandos. O script `.bat` evita a política de execução do PowerShell.

## Começar — Linux/macOS

```bash
bash INICIAR_LINUX_MAC.sh
```

## Funcionalidades efetivamente implementadas nesta entrega

- Navegação responsiva, dashboard, consulta a PDS, indicadores, objetivos, séries e comparação tabular.
- Motor de desempenho PDS portado de `src/lib/pds/calculos.ts`, preservando metas, polaridade, zero e valores ausentes.
- PAS: planos/versionamento básico, ações, atividades, monitoramento manual, status explícitos e vínculos com indicadores.
- Importação de CSV/XLSX PDS/PAS/monitoramento com prévia e confirmação transacional; resolução de duplicidade manter/substituir.
- Extração **textual** de PDF para **revisão**: não transforma automaticamente PDFs SESPLAN em tabelas; falta portar validadores específicos e testar em documentos reais.
- RDQA: gerar blocos a partir dos registros estruturados, editar blocos e exportar DOCX.
- Gemini: análise orientada por indicador via API no servidor, somente quando `GEMINI_API_KEY` configurada.
- Autenticação local no modo demo; login Supabase Auth em modo integrado com consulta `user_roles` aprovada.
- Trilha simples de importações, alterações manuais e exportação CSV.
- Testes unitários do motor de cálculo sem depender de Django.

## Supabase e Render (INTEGRAÇÃO REQUER CONFIGURAÇÃO E TESTES)

No `.env` do ambiente de integração:

```dotenv
SIS_DEMO_MODE=false
DEBUG=false
DJANGO_SECRET_KEY=<gerar-valor-forte>
DATABASE_URL=postgresql://usuario:senha@host:5432/banco
SUPABASE_URL=https://SEU-PROJETO.supabase.co
SUPABASE_ANON_KEY=<chave-publicavel-legacy-anon-ou-api-compativel>
ALLOWED_HOSTS=seu-servico.onrender.com
CSRF_TRUSTED_ORIGINS=https://seu-servico.onrender.com
GEMINI_API_KEY=<somente-se-usar-IA>
```

**Atenção:** para o primeiro deploy, use projeto Supabase de **homologação vazio**, não o banco existente em produção. A estrutura ORM desta versão **não** é idêntica às tabelas Lovable. Faça mapeamento/migração específica e testes de integridade antes de reutilizar dados/credenciais de qualquer ambiente institucional. Não execute `migrate` diretamente no Supabase legado sem revisão técnica.

Execute as migrações uma vez, preferencialmente como operação de release separada:

```bash
python manage.py makemigrations core
python manage.py migrate
python manage.py collectstatic --noinput
```

**Importante:** a entrega gera a migração inicial do aplicativo na primeira execução (`makemigrations core`), pois o banco alvo pode ser SQLite local ou PostgreSQL de homologação. Antes do deploy, versione o arquivo de migração criado e não regenere a cada inicialização.

### Supabase Auth

O login é validado no endpoint oficial `/auth/v1/token`. A identidade `user.id` e seu perfil são consultados na tabela `public.user_roles` protegida por RLS, seguindo as migrações originais. Os papéis esperados são `admin` e `viewer`, com `approved=true`. No Django, a sessão é emitida somente após a aprovação. **Pendente para produção:** revalidação periódica/revogação imediata de sessão, revisão do modelo de autorização, trilha completa de auditoria e fluxo administrativo de aprovação/revogação diretamente pela interface. A aprovação/revogação deve ser feita no Supabase até o módulo ser finalizado.

### Segurança

- Não inclua `.env` no Git e nunca exponha `service_role` nem `GEMINI_API_KEY` ao navegador.
- Nunca use `SIS_DEMO_MODE=true` em produção. Não publique credenciais de demo.
- Ative HTTPS, domínio permitido, backups, expiração de sessão e monitoramento.
- O DOCX é **rascunho**: homologação não automatizada.
- Dados enviados ao Gemini devem ter classificação e autorização institucional.

## Modelos de importação

Confira `exemplos/pds_exemplo.csv`, `exemplos/pas_exemplo.csv`, `exemplos/monitoramento_pas_exemplo.csv` — são *fictícios*. O PDF original é extraído apenas como texto de conferência e não pode ser confirmado diretamente.

## Testes

```bash
python -m unittest discover -s tests -v
python manage.py check
```

## Referência Lovable e rastreabilidade

A pasta `referencia_lovable/` contém cópias selecionadas (sem segredos) das regras originais e migrações, preservadas para comparação de comportamentos. O dump de produção fornecido **não está incluído** no pacote para evitar exposição de dados. Consulte `docs/ESCOPO_E_LACUNAS.md`.

## Próximos passos de engenharia

1. Mapear integralmente o esquema Lovable e decidir estratégia de migração de dados.
2. Portar o parser SESPLAN e parser de relatórios PAS, usando amostras reais anonimizadas e testes de regressão.
3. Homologar os cálculos, as linhagens de catálogo PDS e os casos de reimportação.
4. Completar RDQA oficial, análises integradas/ampliadas, análise de qualidade e fluxo de aprovação.
5. Corrigir lacunas de segurança, testes end-to-end e observabilidade antes de implantação institucional.
