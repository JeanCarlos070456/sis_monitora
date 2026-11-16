# Matriz de implementação × protótipo Lovable

Origem: `sismonitora(1).zip` de 04/11/2026 e capturas do banco/Storage. A implementação Django não é automaticamente equivalente ao sistema original.

| Domínio | Nesta versão Django | Lacuna para equivalência Lovable |
|---|---|---|
| Interface | Dashboard, menus e páginas principais | Fidelidade visual/pixel perfect e fluxos secundários |
| PDS | Indicadores, objetivos, cálculo, séries, CSV | Parser PDF SESPLAN, catálogo vigência, PPA, todas as diffs, dashboards aprofundados |
| PAS | Planos, ações, atividades, monitoramento, vínculo | Parser PAS PDFs, matching automático e versionamento completo |
| RDQA | Blocos gerados, edição, DOCX | Capítulo oficial integral, regras detalhadas de ordem/ligações, homologação |
| Gemini | Uma análise de indicador por demanda | Análise integrada, ampliada e agendamento/cotas |
| Segurança | Login Supabase, papéis aprovados na entrada | Renovação/revogação imediata, painel de aprovação, MFA e política institucional |
| Banco | ORM independente, Postgres/SQLite | Migração e compatibilidade integral do esquema e dados Lovable |
| Storage | Documento processado na memória | Persistência segura nos buckets privados + download assinado |
| Auditoria | Eventos principais | Log imutável de todas as operações |
| Importações | CSV/XLSX em duas etapas; PDFs leitura textual | Extração institucional estruturada de PDFs com conciliação |
| Testes | Unitários motor PDS | Integração, segurança, interface e regressão ponta a ponta |

**Status:** release 0.1 para exploração, validação de arquitetura e elaboração do backlog. Não homologado.
