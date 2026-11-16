// Tipos e rótulos do capítulo do RDQA — módulo seguro para o navegador.
import type { StatusAtividade } from "./pas/regras";

export interface IndicadorDoBloco {
  codigo_indicador: string | null;
  indicador: string | null;
  referencia_catalogo: string | null;
  polaridade: string | null;
  meta_anual: number | null;
  unidade: string | null;
  meta_pds: string | null;
  percentual_alcance: number | null;
  status_desempenho: string | null;
  analise_area: string | null;
  resultados: Record<number, { valor: number | null; apurado: boolean }>;
}

export interface AtividadeDoBloco {
  numero: number | null;
  descricao: string;
  status: StatusAtividade;
  status_informado: boolean;
  reportado: string | null;
  entraves: Array<{ entrave: string | null; providencia: string | null }>;
}

export interface AcaoRdqa {
  acao_id: string;
  numero_acao: number;
  descricao_acao: string;
  area_desempenho: string | null;
  area_monitoramento: string | null;
  situacao_acao: string | null;
  controle: string | null;
  monitorada: boolean;
  atividades: AtividadeDoBloco[];
  entravesAcao: Array<{ entrave: string | null; providencia: string | null }>;
}

export interface BlocoRdqa {
  /** "IND:<código>" para bloco de indicador, "OE:<código>" para ações ligadas ao objetivo. */
  chave: string;
  tipo_vinculo: "INDICADOR" | "OBJETIVO_ESTRATEGICO";
  indicador: IndicadorDoBloco | null;
  acoes: AcaoRdqa[];
  analise: string | null;
  analise_origem: string | null;
  /** Alertas de conferência (divergências, ausências), nunca inferências. */
  alertas: string[];
}

export interface ObjetivoRdqa {
  codigo: string;
  descricao: string | null;
  blocos: BlocoRdqa[];
}

export interface DiretrizRdqa {
  codigo: string;
  nome: string;
  descritivo: string | null;
  objetivos: ObjetivoRdqa[];
}

export interface EixoRdqa {
  codigo: string;
  nome: string;
  diretrizes: DiretrizRdqa[];
}

export interface CapituloRdqa {
  documento_id: string;
  ano: number;
  quadrimestre: number;
  data_fonte: string | null;
  eixos: EixoRdqa[];
  totalBlocos: number;
  blocosSemAnalise: number;
}

const STATUS_VALIDOS: StatusAtividade[] = [
  "CONCLUIDA",
  "EM_ANDAMENTO",
  "NAO_INICIADA",
  "NAO_INFORMADA",
];

/** Rótulo do status no padrão do documento RDQA. */
export function rotuloStatusRdqa(status: string | null | undefined, quadrimestre: number): string {
  const s = (status ?? "NAO_INFORMADA") as StatusAtividade;
  switch (STATUS_VALIDOS.includes(s) ? s : "NAO_INFORMADA") {
    case "CONCLUIDA":
      return `Concluído ${quadrimestre}Q`;
    case "EM_ANDAMENTO":
      return "Em Andamento";
    case "NAO_INICIADA":
      return "Não Iniciada";
    default:
      return "Não Informada";
  }
}
