CREATE TYPE public.app_role AS ENUM ('admin', 'viewer');
CREATE TABLE public.user_roles (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
 role public.app_role NOT NULL DEFAULT 'viewer',
 approved boolean NOT NULL DEFAULT false,
 approved_by uuid,
 approved_at timestamptz,
 created_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(user_id)
);
GRANT SELECT ON public.user_roles TO authenticated;
GRANT ALL ON public.user_roles TO service_role;
ALTER TABLE public.user_roles ENABLE ROW LEVEL SECURITY;
CREATE POLICY own_role_read ON public.user_roles FOR SELECT TO authenticated USING (user_id = auth.uid());
CREATE FUNCTION public.has_role(_user_id uuid, _role public.app_role) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public AS $$ SELECT _user_id = auth.uid() AND EXISTS (SELECT 1 FROM public.user_roles WHERE user_id = _user_id AND role = _role AND approved); $$;
REVOKE ALL ON FUNCTION public.has_role(uuid, public.app_role) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.has_role(uuid, public.app_role) TO authenticated, service_role;
CREATE FUNCTION public.has_approved_access() RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public AS $$ SELECT EXISTS (SELECT 1 FROM public.user_roles WHERE user_id = auth.uid() AND approved); $$;
REVOKE ALL ON FUNCTION public.has_approved_access() FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.has_approved_access() TO authenticated, service_role;
CREATE FUNCTION public.register_access_request() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$ BEGIN INSERT INTO public.user_roles(user_id) VALUES (NEW.id) ON CONFLICT(user_id) DO NOTHING; RETURN NEW; END; $$;
REVOKE ALL ON FUNCTION public.register_access_request() FROM PUBLIC, anon, authenticated;
CREATE TRIGGER app_access_request AFTER INSERT ON auth.users FOR EACH ROW EXECUTE FUNCTION public.register_access_request();
DO $$ DECLARE t text; BEGIN FOREACH t IN ARRAY ARRAY['alteracoes_registros','analises_ia','analises_qualidade','importacoes_sesplan','inconsistencias','indicadores_pds_resultados','objetivos_estrategicos','pas_acao_indicador','pas_acoes','pas_alteracoes_versao','pas_atividades','pas_entraves','pas_importacoes','pas_inconsistencias','pas_monitoramento_acoes','pas_monitoramento_atividades','pas_planos','rdqa_blocos','rdqa_documentos'] LOOP EXECUTE format('GRANT SELECT, INSERT, UPDATE, DELETE ON public.%I TO authenticated',t); EXECUTE format('GRANT ALL ON public.%I TO service_role',t); EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY',t); EXECUTE format('CREATE POLICY approved_read ON public.%I FOR SELECT TO authenticated USING (public.has_approved_access())',t); EXECUTE format('CREATE POLICY admin_insert ON public.%I FOR INSERT TO authenticated WITH CHECK (public.has_role(auth.uid(), ''admin''))',t); EXECUTE format('CREATE POLICY admin_update ON public.%I FOR UPDATE TO authenticated USING (public.has_role(auth.uid(), ''admin'')) WITH CHECK (public.has_role(auth.uid(), ''admin''))',t); EXECUTE format('CREATE POLICY admin_delete ON public.%I FOR DELETE TO authenticated USING (public.has_role(auth.uid(), ''admin''))',t); END LOOP; END $$;
REVOKE ALL ON FUNCTION public.sincronizar_objetivos_estrategicos() FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.sincronizar_objetivos_estrategicos() TO service_role;
CREATE POLICY admin_pdf_upload ON storage.objects FOR INSERT TO authenticated WITH CHECK (bucket_id IN ('sesplan-pdfs','pas-pdfs') AND public.has_role(auth.uid(), 'admin'));
CREATE POLICY approved_pdf_read ON storage.objects FOR SELECT TO authenticated USING (bucket_id IN ('sesplan-pdfs','pas-pdfs') AND public.has_approved_access());
CREATE POLICY admin_pdf_update ON storage.objects FOR UPDATE TO authenticated USING (bucket_id IN ('sesplan-pdfs','pas-pdfs') AND public.has_role(auth.uid(), 'admin')) WITH CHECK (bucket_id IN ('sesplan-pdfs','pas-pdfs') AND public.has_role(auth.uid(), 'admin'));
