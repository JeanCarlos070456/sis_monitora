CREATE TABLE public.rdqa_documentos (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  ano integer NOT NULL,
  quadrimestre integer NOT NULL,
  data_fonte date,
  status text NOT NULL DEFAULT 'em_edicao',
  observacoes text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (ano, quadrimestre)
);

CREATE TABLE public.rdqa_blocos (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  documento_id uuid NOT NULL REFERENCES public.rdqa_documentos(id) ON DELETE CASCADE,
  objetivo_id uuid REFERENCES public.objetivos_estrategicos(id),
  acao_id uuid REFERENCES public.pas_acoes(id),
  numero_acao integer,
  ordem integer,
  analise_texto text,
  analise_origem text NOT NULL DEFAULT 'ia',
  editado_por text,
  editado_em timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (documento_id, acao_id)
);

CREATE INDEX rdqa_blocos_documento_idx ON public.rdqa_blocos (documento_id);

ALTER TABLE public.rdqa_documentos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.rdqa_blocos ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON public.rdqa_documentos FROM anon, authenticated;
REVOKE ALL ON public.rdqa_blocos FROM anon, authenticated;
GRANT ALL ON public.rdqa_documentos TO service_role;
GRANT ALL ON public.rdqa_blocos TO service_role;