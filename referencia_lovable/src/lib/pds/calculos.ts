// Cálculos de desempenho do PDS: % de alcance da meta, status, diferença,
// variação e tendência. Regras conforme especificação (itens 12 a 22).

export type Polaridade = "Maior - melhor" | "Menor - melhor";

export const STATUS = {
  INSUFICIENTE: "Insuficiente",
  MEDIO: "Médio",
  BOM: "Bom",
  OTIMO: "Ótimo",
  NAO_APURADO: "Não apurado",
  NAO_CALCULAVEL: "Não calculável",
} as const;

export type StatusDesempenho = (typeof STATUS)[keyof typeof STATUS];

export function normalizaPolaridade(p: string | null | undefined): Polaridade | null {
  if (!p) return null;
  const t = p.toLowerCase();
  if (t.includes("menor")) return "Menor - melhor";
  if (t.includes("maior")) return "Maior - melhor";
  return null;
}

export function statusPorPercentual(pct: number): StatusDesempenho {
  if (pct < 50) return STATUS.INSUFICIENTE;
  if (pct < 70) return STATUS.MEDIO;
  if (pct < 90) return STATUS.BOM;
  return STATUS.OTIMO;
}

export interface ResultadoCalculo {
  percentual: number | null;
  status: StatusDesempenho;
  diferenca: number | null;
}

export function calcularDesempenho(
  meta: number | null,
  resultado: number | null,
  polaridade: string | null | undefined,
): ResultadoCalculo {
  if (resultado == null) {
    return { percentual: null, status: STATUS.NAO_APURADO, diferenca: null };
  }
  const pol = normalizaPolaridade(polaridade);
  if (!pol || meta == null) {
    return { percentual: null, status: STATUS.NAO_CALCULAVEL, diferenca: null };
  }

  let percentual: number | null = null;
  let status: StatusDesempenho;

  if (pol === "Maior - melhor") {
    if (meta === 0) {
      return { percentual: null, status: STATUS.NAO_CALCULAVEL, diferenca: null };
    }
    percentual = (resultado / meta) * 100;
    status = statusPorPercentual(percentual);
  } else {
    // Menor - melhor
    if (meta === 0) {
      if (resultado === 0) {
        percentual = 100;
        status = STATUS.OTIMO;
      } else {
        percentual = 0;
        status = STATUS.INSUFICIENTE;
      }
    } else if (resultado <= meta) {
      percentual = 100;
      status = STATUS.OTIMO;
    } else {
      percentual = (meta / resultado) * 100;
      status = statusPorPercentual(percentual);
    }
  }

  const diferenca =
    pol === "Maior - melhor" ? resultado - meta : meta - resultado;

  return { percentual: arred(percentual), status, diferenca: arred(diferenca) };
}

export type Tendencia = "Melhora" | "Piora" | "Estabilidade" | "Sem comparação";

export interface Comparacao {
  variacaoAbsoluta: number | null;
  variacaoPercentual: number | null;
  tendencia: Tendencia;
  evolucaoStatus: string | null;
}

const HIERARQUIA: StatusDesempenho[] = [
  STATUS.INSUFICIENTE,
  STATUS.MEDIO,
  STATUS.BOM,
  STATUS.OTIMO,
];

export function compararComAnterior(
  atual: number | null,
  anterior: number | null,
  polaridade: string | null | undefined,
  statusAtual?: string | null,
  statusAnterior?: string | null,
): Comparacao {
  if (atual == null || anterior == null) {
    return {
      variacaoAbsoluta: null,
      variacaoPercentual: null,
      tendencia: "Sem comparação",
      evolucaoStatus: null,
    };
  }
  const pol = normalizaPolaridade(polaridade);
  const variacaoAbsoluta = arred(atual - anterior);
  const variacaoPercentual =
    anterior !== 0 ? arred(((atual - anterior) / anterior) * 100) : null;

  let tendencia: Tendencia;
  if (atual === anterior) {
    tendencia = "Estabilidade";
  } else if (!pol) {
    tendencia = "Sem comparação";
  } else if (pol === "Maior - melhor") {
    tendencia = atual > anterior ? "Melhora" : "Piora";
  } else {
    tendencia = atual < anterior ? "Melhora" : "Piora";
  }

  let evolucaoStatus: string | null = null;
  const iA = statusAtual ? HIERARQUIA.indexOf(statusAtual as StatusDesempenho) : -1;
  const iB = statusAnterior ? HIERARQUIA.indexOf(statusAnterior as StatusDesempenho) : -1;
  if (iA >= 0 && iB >= 0 && iA !== iB) {
    evolucaoStatus = iA > iB ? "Melhora de classificação" : "Piora de classificação";
  } else if (iA >= 0 && iB >= 0) {
    evolucaoStatus = "Manteve classificação";
  }

  return { variacaoAbsoluta, variacaoPercentual, tendencia, evolucaoStatus };
}

function arred(v: number | null): number | null {
  if (v == null || !Number.isFinite(v)) return null;
  return Math.round(v * 100) / 100;
}

/** "Bom — 82,4% da meta" */
export function rotuloStatus(status: string | null, percentual: number | null): string {
  if (!status) return "—";
  if (status === STATUS.NAO_APURADO || status === STATUS.NAO_CALCULAVEL) return status;
  if (percentual == null) return status;
  return `${status} — ${percentual.toLocaleString("pt-BR", { maximumFractionDigits: 1 })}% da meta`;
}

export type CorStatus =
  | "otimo"
  | "bom"
  | "medio"
  | "insuficiente"
  | "naoapurado"
  | "naocalculavel";

export function corDoStatus(status: string | null): CorStatus {
  switch (status) {
    case STATUS.OTIMO:
      return "otimo";
    case STATUS.BOM:
      return "bom";
    case STATUS.MEDIO:
      return "medio";
    case STATUS.INSUFICIENTE:
      return "insuficiente";
    case STATUS.NAO_CALCULAVEL:
      return "naocalculavel";
    default:
      return "naoapurado";
  }
}
