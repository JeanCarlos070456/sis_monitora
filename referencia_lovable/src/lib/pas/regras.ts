// Regras centrais do módulo PAS: bimestre considerado, normalização de texto,
// similaridade e rótulos de status. Devem ser usadas por parsers, telas e exportações.

/** Bimestre de fechamento de cada quadrimestre — regra única do sistema. */
export const BIMESTRE_DO_QUADRIMESTRE: Record<number, string> = {
  1: "Março/Abril",
  2: "Julho/Agosto",
  3: "Novembro/Dezembro",
};

/** Bimestres anteriores de cada quadrimestre (usados apenas para localizar a estrutura). */
export const BIMESTRES_DO_QUADRIMESTRE: Record<number, string[]> = {
  1: ["Janeiro/Fevereiro", "Março/Abril"],
  2: ["Maio/Junho", "Julho/Agosto"],
  3: ["Setembro/Outubro", "Novembro/Dezembro"],
};

export function bimestreConsiderado(quadrimestre: number): string {
  return BIMESTRE_DO_QUADRIMESTRE[quadrimestre] ?? "";
}

export type StatusAtividade =
  | "NAO_INICIADA"
  | "EM_ANDAMENTO"
  | "CONCLUIDA"
  | "NAO_INFORMADA";

export const STATUS_ATIVIDADE: StatusAtividade[] = [
  "CONCLUIDA",
  "EM_ANDAMENTO",
  "NAO_INICIADA",
  "NAO_INFORMADA",
];

export const ROTULO_STATUS_ATIVIDADE: Record<StatusAtividade, string> = {
  NAO_INICIADA: "Não iniciada",
  EM_ANDAMENTO: "Em andamento",
  CONCLUIDA: "Concluída",
  NAO_INFORMADA: "Não informada",
};

/** Classes de cor por status — sempre acompanhadas do texto do status. */
export const CLASSE_STATUS_ATIVIDADE: Record<StatusAtividade, string> = {
  CONCLUIDA: "bg-emerald-50 text-emerald-700 border-emerald-200",
  EM_ANDAMENTO: "bg-amber-50 text-amber-800 border-amber-200",
  NAO_INICIADA: "bg-red-50 text-red-700 border-red-200",
  NAO_INFORMADA: "bg-muted text-muted-foreground border-border",
};

export type TipoVinculo = "INDICADOR" | "OBJETIVO_ESTRATEGICO";
export type Confianca = "ALTA" | "MEDIA" | "BAIXA";

export const ROTULO_CONFIANCA: Record<Confianca, string> = {
  ALTA: "Alta",
  MEDIA: "Média",
  BAIXA: "Baixa",
};

/**
 * Identifica o status explícito informado no texto da atividade relatada.
 * Nunca infere: sem marcação explícita devolve NAO_INFORMADA.
 */
export function statusExplicitoNoTexto(texto: string | null | undefined): StatusAtividade {
  if (!texto) return "NAO_INFORMADA";
  const t = normalizarTexto(texto);
  if (/\bconcluida\b|\bconcluido\b|\bfinalizada\b/.test(t)) return "CONCLUIDA";
  if (/\bem andamento\b|\bandamento\b|\biniciada\b(?!.*\bnao\b)/.test(t)) return "EM_ANDAMENTO";
  if (/\bnao iniciada\b|\bnao iniciado\b/.test(t)) return "NAO_INICIADA";
  return "NAO_INFORMADA";
}

/** Normaliza texto para comparação: sem acento, minúsculo, sem pontuação e sem status final. */
export function normalizarTexto(texto: string | null | undefined): string {
  if (!texto) return "";
  return texto
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^\w\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

/** Normalização usada no match de atividades: remove também o status ao final. */
export function normalizarParaMatch(texto: string | null | undefined): string {
  return normalizarTexto(texto)
    .replace(/\b(concluida|concluido|em andamento|andamento|nao iniciada|nao iniciado)\b\s*$/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

/** Similaridade textual 0–1 por bigramas (Dice). */
export function similaridade(a: string, b: string): number {
  const x = normalizarParaMatch(a);
  const y = normalizarParaMatch(b);
  if (!x || !y) return 0;
  if (x === y) return 1;
  const bigramas = (s: string) => {
    const set = new Map<string, number>();
    for (let i = 0; i < s.length - 1; i++) {
      const g = s.slice(i, i + 2);
      set.set(g, (set.get(g) ?? 0) + 1);
    }
    return set;
  };
  const bx = bigramas(x);
  const by = bigramas(y);
  let comuns = 0;
  for (const [g, n] of bx) comuns += Math.min(n, by.get(g) ?? 0);
  const total = [...bx.values()].reduce((s, n) => s + n, 0) +
    [...by.values()].reduce((s, n) => s + n, 0);
  return total === 0 ? 0 : (2 * comuns) / total;
}

export function confiancaPorSimilaridade(valor: number): Confianca {
  if (valor >= 0.92) return "ALTA";
  if (valor >= 0.7) return "MEDIA";
  return "BAIXA";
}

/** Percentual de atividades concluídas — informação operacional, não status de desempenho. */
export function percentualConclusao(
  total: number,
  concluidas: number,
): number | null {
  if (total <= 0) return null;
  return (concluidas / total) * 100;
}

export function resumirAtividades(
  status: Array<StatusAtividade | string | null | undefined>,
) {
  const contagem: Record<StatusAtividade, number> = {
    CONCLUIDA: 0,
    EM_ANDAMENTO: 0,
    NAO_INICIADA: 0,
    NAO_INFORMADA: 0,
  };
  for (const s of status) {
    const chave = (s ?? "NAO_INFORMADA") as StatusAtividade;
    if (chave in contagem) contagem[chave] += 1;
    else contagem.NAO_INFORMADA += 1;
  }
  const total = status.length;
  return {
    total,
    ...contagem,
    percentual: percentualConclusao(total, contagem.CONCLUIDA),
  };
}
