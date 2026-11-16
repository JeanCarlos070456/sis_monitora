-- Cadastro próprio de objetivos estratégicos (derivado dos indicadores do PDS)
CREATE TABLE public.objetivos_estrategicos (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  codigo text NOT NULL UNIQUE,
  descricao text,
  eixo_codigo text,
  eixo text,
  diretriz_codigo text,
  diretriz text,
  created_at timestamptz NOT NULL DEFAULT now()
);
GRANT SELECT, INSERT, UPDATE, DELETE ON public.objetivos_estrategicos TO anon, authenticated;
GRANT ALL ON public.objetivos_estrategicos TO service_role;
ALTER TABLE public.objetivos_estrategicos ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Acesso aberto objetivos" ON public.objetivos_estrategicos FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);

-- Sincroniza os objetivos a partir dos indicadores já importados
CREATE OR REPLACE FUNCTION public.sincronizar_objetivos_estrategicos()
RETURNS integer
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE inseridos integer;
BEGIN
  WITH base AS (
    SELECT DISTINCT
      trim(split_part(objetivo, ' - ', 1)) AS codigo,
      trim(substring(objetivo from position(' - ' in objetivo) + 3)) AS descricao,
      eixo_codigo, eixo, diretriz_codigo, diretriz
    FROM public.indicadores_pds_resultados
    WHERE objetivo IS NOT NULL AND position(' - ' in objetivo) > 0
  ), ins AS (
    INSERT INTO public.objetivos_estrategicos (codigo, descricao, eixo_codigo, eixo, diretriz_codigo, diretriz)
    SELECT codigo, descricao, eixo_codigo, eixo, diretriz_codigo, diretriz
    FROM base
    WHERE codigo <> ''
    ON CONFLICT (codigo) DO UPDATE
      SET descricao = COALESCE(EXCLUDED.descricao, public.objetivos_estrategicos.descricao),
          eixo_codigo = COALESCE(EXCLUDED.eixo_codigo, public.objetivos_estrategicos.eixo_codigo),
          eixo = COALESCE(EXCLUDED.eixo, public.objetivos_estrategicos.eixo),
          diretriz_codigo = COALESCE(EXCLUDED.diretriz_codigo, public.objetivos_estrategicos.diretriz_codigo),
          diretriz = COALESCE(EXCLUDED.diretriz, public.objetivos_estrategicos.diretriz)
    RETURNING 1
  )
  SELECT count(*)::int INTO inseridos FROM ins;
  RETURN inseridos;
END;
$$;

-- Planos anuais da PAS (ano + versão)
CREATE TABLE public.pas_planos (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  ano integer NOT NULL,
  versao text NOT NULL,
  nome_arquivo text,
  storage_path text,
  status text NOT NULL DEFAULT 'ativo',
  observacoes text,
  ativo boolean NOT NULL DEFAULT true,
  data_importacao timestamptz NOT NULL DEFAULT now(),
  UNIQUE (ano, versao)
);
GRANT SELECT, INSERT, UPDATE, DELETE ON public.pas_planos TO anon, authenticated;
GRANT ALL ON public.pas_planos TO service_role;
ALTER TABLE public.pas_planos ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Acesso aberto pas_planos" ON public.pas_planos FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);

-- Importações da PAS (aprovada e monitoramento quadrimestral)
CREATE TABLE public.pas_importacoes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tipo text NOT NULL,
  ano integer NOT NULL,
  versao text,
  quadrimestre integer,
  bimestre_referencia text,
  plano_id uuid REFERENCES public.pas_planos(id) ON DELETE SET NULL,
  nome_arquivo text NOT NULL,
  storage_path text,
  status text NOT NULL DEFAULT 'processando',
  acoes_encontradas integer DEFAULT 0,
  atividades_encontradas integer DEFAULT 0,
  matches_automaticos integer DEFAULT 0,
  matches_manuais integer DEFAULT 0,
  alteracoes integer DEFAULT 0,
  inconsistencias integer DEFAULT 0,
  usuario text,
  observacoes text,
  data_upload timestamptz NOT NULL DEFAULT now(),
  data_processamento timestamptz
);
GRANT SELECT, INSERT, UPDATE, DELETE ON public.pas_importacoes TO anon, authenticated;
GRANT ALL ON public.pas_importacoes TO service_role;
ALTER TABLE public.pas_importacoes ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Acesso aberto pas_importacoes" ON public.pas_importacoes FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);

-- Ações estratégicas da PAS
CREATE TABLE public.pas_acoes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  plano_id uuid REFERENCES public.pas_planos(id) ON DELETE CASCADE,
  ano_pas integer NOT NULL,
  versao_pas text NOT NULL,
  numero_acao integer NOT NULL,
  descricao_acao text NOT NULL,
  objetivo_id uuid REFERENCES public.objetivos_estrategicos(id) ON DELETE SET NULL,
  objetivo_texto text,
  eixo_codigo text,
  eixo text,
  diretriz_codigo text,
  diretriz text,
  meta_texto text,
  tipo_vinculo text NOT NULL DEFAULT 'INDICADOR',
  area_monitoramento text,
  area_desempenho text,
  ativo boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (ano_pas, versao_pas, numero_acao)
);
GRANT SELECT, INSERT, UPDATE, DELETE ON public.pas_acoes TO anon, authenticated;
GRANT ALL ON public.pas_acoes TO service_role;
ALTER TABLE public.pas_acoes ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Acesso aberto pas_acoes" ON public.pas_acoes FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);
CREATE INDEX idx_pas_acoes_ano ON public.pas_acoes (ano_pas, numero_acao);

-- Atividades planejadas de cada ação
CREATE TABLE public.pas_atividades (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  acao_id uuid NOT NULL REFERENCES public.pas_acoes(id) ON DELETE CASCADE,
  numero_atividade integer,
  descricao_atividade text NOT NULL,
  area_desempenho text,
  versao_pas text,
  ativo boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now()
);
GRANT SELECT, INSERT, UPDATE, DELETE ON public.pas_atividades TO anon, authenticated;
GRANT ALL ON public.pas_atividades TO service_role;
ALTER TABLE public.pas_atividades ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Acesso aberto pas_atividades" ON public.pas_atividades FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);
CREATE INDEX idx_pas_atividades_acao ON public.pas_atividades (acao_id);

-- Relacionamento entre ação da PAS e indicador do PDS
CREATE TABLE public.pas_acao_indicador (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  acao_id uuid NOT NULL REFERENCES public.pas_acoes(id) ON DELETE CASCADE,
  codigo_indicador text,
  indicador_texto text,
  referencia_indicador_pds text,
  tipo_vinculo text NOT NULL DEFAULT 'INDICADOR',
  confianca_relacionamento text NOT NULL DEFAULT 'BAIXA',
  criterio_match text,
  validado_manualmente boolean NOT NULL DEFAULT false,
  validado_por text,
  validado_em timestamptz,
  created_at timestamptz NOT NULL DEFAULT now()
);
GRANT SELECT, INSERT, UPDATE, DELETE ON public.pas_acao_indicador TO anon, authenticated;
GRANT ALL ON public.pas_acao_indicador TO service_role;
ALTER TABLE public.pas_acao_indicador ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Acesso aberto pas_acao_indicador" ON public.pas_acao_indicador FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);
CREATE INDEX idx_pas_acao_indicador_codigo ON public.pas_acao_indicador (codigo_indicador);

-- Monitoramento quadrimestral das ações
CREATE TABLE public.pas_monitoramento_acoes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  importacao_id uuid REFERENCES public.pas_importacoes(id) ON DELETE SET NULL,
  acao_id uuid REFERENCES public.pas_acoes(id) ON DELETE CASCADE,
  numero_acao_relatorio integer,
  acao_localizada boolean NOT NULL DEFAULT true,
  ano integer NOT NULL,
  quadrimestre integer NOT NULL,
  bimestre_referencia text NOT NULL,
  area_responsavel text,
  inicio_previsto date,
  fim_previsto date,
  inicio_efetivo date,
  fim_efetivo date,
  situacao_acao text,
  controle text,
  analise_texto text,
  descricao_acao_relatorio text,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (acao_id, ano, quadrimestre)
);
GRANT SELECT, INSERT, UPDATE, DELETE ON public.pas_monitoramento_acoes TO anon, authenticated;
GRANT ALL ON public.pas_monitoramento_acoes TO service_role;
ALTER TABLE public.pas_monitoramento_acoes ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Acesso aberto pas_mon_acoes" ON public.pas_monitoramento_acoes FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);
CREATE INDEX idx_pas_mon_acoes_periodo ON public.pas_monitoramento_acoes (ano, quadrimestre);

-- Monitoramento quadrimestral das atividades
CREATE TABLE public.pas_monitoramento_atividades (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  monitoramento_acao_id uuid NOT NULL REFERENCES public.pas_monitoramento_acoes(id) ON DELETE CASCADE,
  atividade_id uuid REFERENCES public.pas_atividades(id) ON DELETE SET NULL,
  numero_atividade_relatorio integer,
  texto_reportado text,
  status_atividade text NOT NULL DEFAULT 'NAO_INFORMADA',
  confianca_match text,
  criterio_match text,
  validado_manualmente boolean NOT NULL DEFAULT false,
  ano integer NOT NULL,
  quadrimestre integer NOT NULL,
  bimestre_referencia text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
GRANT SELECT, INSERT, UPDATE, DELETE ON public.pas_monitoramento_atividades TO anon, authenticated;
GRANT ALL ON public.pas_monitoramento_atividades TO service_role;
ALTER TABLE public.pas_monitoramento_atividades ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Acesso aberto pas_mon_atividades" ON public.pas_monitoramento_atividades FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);
CREATE INDEX idx_pas_mon_ativ_mon_acao ON public.pas_monitoramento_atividades (monitoramento_acao_id);

-- Entraves e providências
CREATE TABLE public.pas_entraves (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  monitoramento_acao_id uuid NOT NULL REFERENCES public.pas_monitoramento_acoes(id) ON DELETE CASCADE,
  monitoramento_atividade_id uuid REFERENCES public.pas_monitoramento_atividades(id) ON DELETE SET NULL,
  atividade_id uuid REFERENCES public.pas_atividades(id) ON DELETE SET NULL,
  entrave text,
  providencia text,
  texto_original text NOT NULL,
  ano integer NOT NULL,
  quadrimestre integer NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
GRANT SELECT, INSERT, UPDATE, DELETE ON public.pas_entraves TO anon, authenticated;
GRANT ALL ON public.pas_entraves TO service_role;
ALTER TABLE public.pas_entraves ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Acesso aberto pas_entraves" ON public.pas_entraves FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);

-- Alertas de qualidade das importações da PAS
CREATE TABLE public.pas_inconsistencias (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  importacao_id uuid REFERENCES public.pas_importacoes(id) ON DELETE CASCADE,
  tipo text NOT NULL,
  descricao text NOT NULL,
  numero_acao integer,
  numero_atividade integer,
  ano integer,
  quadrimestre integer,
  created_at timestamptz NOT NULL DEFAULT now()
);
GRANT SELECT, INSERT, UPDATE, DELETE ON public.pas_inconsistencias TO anon, authenticated;
GRANT ALL ON public.pas_inconsistencias TO service_role;
ALTER TABLE public.pas_inconsistencias ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Acesso aberto pas_inconsistencias" ON public.pas_inconsistencias FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);

-- Histórico de alterações entre versões da PAS aprovada
CREATE TABLE public.pas_alteracoes_versao (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  importacao_id uuid REFERENCES public.pas_importacoes(id) ON DELETE CASCADE,
  ano integer NOT NULL,
  versao_anterior text,
  versao_nova text,
  tipo_alteracao text NOT NULL,
  numero_acao integer,
  numero_atividade integer,
  valor_anterior text,
  valor_novo text,
  created_at timestamptz NOT NULL DEFAULT now()
);
GRANT SELECT, INSERT, UPDATE, DELETE ON public.pas_alteracoes_versao TO anon, authenticated;
GRANT ALL ON public.pas_alteracoes_versao TO service_role;
ALTER TABLE public.pas_alteracoes_versao ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Acesso aberto pas_alteracoes" ON public.pas_alteracoes_versao FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);