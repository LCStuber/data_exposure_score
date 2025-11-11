import os
import json
from datetime import datetime
from collections import defaultdict
from typing import Any, Dict, Optional, List

try:
    from pymongo import MongoClient
except Exception:
    MongoClient = None

USER = os.getenv("MONGO_USER")
PASS = os.getenv("MONGO_PASS")
HOST = os.getenv("MONGO_HOST")
PORT = os.getenv("MONGO_PORT")
AUTH_DB = os.getenv("MONGO_AUTH_DB")
DB_NAME = os.getenv("MONGO_DB")
COL_REPORT = os.getenv("MONGO_COLLECTION_REPORTS", "reports")

# --- Config / Domain definitions (unchanged) ---
ageRanges = [
  { "label": "< 18", "min": 0, "max": 17 },
  { "label": "18-24", "min": 18, "max": 24 },
  { "label": "25-34", "min": 25, "max": 34 },
  { "label": "35-44", "min": 35, "max": 44 },
  { "label": "45-54", "min": 45, "max": 54 },
  { "label": "55-64", "min": 55, "max": 64 },
  { "label": "65+", "min": 65, "max": 999 },
]
AGE_LABELS = [r["label"] for r in ageRanges]

DES_RANGES_DEF = [
  { "label": "0-199", "min": 0, "max": 200 },
  { "label": "200-399", "min": 200, "max": 400 },
  { "label": "400-599", "min": 400, "max": 600 },
  { "label": "600-799", "min": 600, "max": 800 },
  { "label": "800-1000", "min": 800, "max": 1000 },
]
DES_RANGE_LABELS = [r["label"] for r in DES_RANGES_DEF]

CAMPO_LIST = [
    "NomeDeclaradoOuSugeridoPeloAutor",
    "IdadeDeclaradaOuInferidaDoAutor",
    "GeneroAutoDeclaradoOuInferidoDoAutor",
    "OrientacaoSexualDeclaradaOuSugeridaPeloAutor",
    "StatusDeRelacionamentoDeclaradoOuSugeridoDoAutor",
    "ProfissaoOcupacaoDeclaradaPeloAutor",
    "NivelEducacionalDeclaradoOuInferidoDoAutor",
    "LocalizacaoPrincipalDeclaradaOuInferidaDoAutor",
    "CidadesComRelevanciaPessoalParaOAutor",
    "CrencaReligiosaDeclaradaOuSugeridaPeloAutor",
    "OpinioesPoliticasExpressasPeloAutor",
    "ExposicaoDeRelacionamentosPessoaisPeloAutor",
    "MencaoDoAutorAPosseDeCPF",
    "MencaoDoAutorAPosseDeRG",
    "MencaoDoAutorAPosseDePassaporte",
    "MencaoDoAutorAPosseDeTituloEleitor",
    "EtniaOuRacaAutoDeclaradaPeloAutor",
    "MencaoDoAutorAEnderecoResidencial",
    "MencaoDoAutorAContatoPessoal_TelefoneEmail",
    "MencaoDoAutorADadosBancarios",
    "MencaoDoAutorACartaoDeEmbarque",
    "IndicadoresDeRendaPropriaMencionadosPeloAutor",
    "MencoesAPatrimonioPessoalDoAutor",
    "LocalDeTrabalhoOuEstudoDeclaradoPeloAutor",
    "MencaoDoAutorARecebimentoDeBeneficioSocial",
    "MencoesAoProprioHistoricoFinanceiroPeloAutor",
    "MencoesDoAutorAProprioHistoricoCriminal",
    "MencaoDoAutorAPosseDeChavePix"
]

# --- Categoria definitions (valores da Tabela 2) ---
categorias = {
    "Informação Financeira": {"Impacto": 10, "Explorabilidade": 8},
    "Documentos Pessoais": {"Impacto": 10, "Explorabilidade": 7},
    "Localização em Tempo Real": {"Impacto": 8, "Explorabilidade": 9},
    "Contato Pessoal": {"Impacto": 8, "Explorabilidade": 10},
    "Rotina/Hábitos": {"Impacto": 6, "Explorabilidade": 6},
    "Posicionamento e Características Pessoais": {"Impacto": 4, "Explorabilidade": 5}
}
category_order = list(categorias.keys())


# --- Map fields to category names (unchanged) ---
exposicao_autor = {
    "NomeDeclaradoOuSugeridoPeloAutor": "Posicionamento e Características Pessoais",
    "IdadeDeclaradaOuInferidaDoAutor": "Posicionamento e Características Pessoais",
    "GeneroAutoDeclaradoOuInferidoDoAutor": "Posicionamento e Características Pessoais",
    "OrientacaoSexualDeclaradaOuSugeridaPeloAutor": "Posicionamento e Características Pessoais",
    "StatusDeRelacionamentoDeclaradoOuSugeridoDoAutor": "Posicionamento e Características Pessoais",
    "ProfissaoOcupacaoDeclaradaPeloAutor": "Rotina/Hábitos",
    "NivelEducacionalDeclaradoOuInferidoDoAutor": "Posicionamento e Características Pessoais",
    "LocalizacaoPrincipalDeclaradaOuInferidaDoAutor": "Localização em Tempo Real",
    "CidadesComRelevanciaPessoalParaOAutor": "Localização em Tempo Real",
    "CrencaReligiosaDeclaradaOuSugeridaPeloAutor": "Posicionamento e Características Pessoais",
    "OpinioesPoliticasExpressasPeloAutor": "Posicionamento e Características Pessoais",
    "ExposicaoDeRelacionamentosPessoaisPeloAutor": "Posicionamento e Características Pessoais",
    "MencaoDoAutorAPosseDeCPF": "Documentos Pessoais",
    "MencaoDoAutorAPosseDeRG": "Documentos Pessoais",
    "MencaoDoAutorAPosseDePassaporte": "Documentos Pessoais",
    "MencaoDoAutorAPosseDeTituloEleitor": "Documentos Pessoais",
    "EtniaOuRacaAutoDeclaradaPeloAutor": "Posicionamento e Características Pessoais",
    "MencaoDoAutorAEnderecoResidencial": "Localização em Tempo Real",
    "MencaoDoAutorAContatoPessoal_TelefoneEmail": "Contato Pessoal",
    "MencaoDoAutorADadosBancarios": "Informação Financeira",
    "MencaoDoAutorACartaoDeEmbarque": "Documentos Pessoais",
    "IndicadoresDeRendaPropriaMencionadosPeloAutor": "Informação Financeira",
    "MencoesAPatrimonioPessoalDoAutor": "Informação Financeira",
    "LocalDeTrabalhoOuEstudoDeclaradoPeloAutor": "Rotina/Hábitos",
    "MencaoDoAutorARecebimentoDeBeneficioSocial": "Informação Financeira",
    "MencoesAoProprioHistoricoFinanceiroPeloAutor": "Informação Financeira",
    "MencoesDoAutorAProprioHistoricoCriminal": "Documentos Pessoais",
    "MencaoDoAutorAPosseDeChavePix": "Informação Financeira"
}

# --- AHP implementation utilities ---

def ahp_weights_from_pairwise(matrix: List[List[float]], labels: List[str]) -> Dict[str, Any]:
    """Recebe uma matriz pareada (n x n) e labels (ordem das linhas/colunas)
    Retorna: { 'weights': {label: weight}, 'lambda_max':..., 'CI':..., 'CR':... }
    (Implementação original mantida, pois está correta)
    """
    n = len(matrix)
    # validate
    if any(len(row) != n for row in matrix):
        raise ValueError("Matriz pareada deve ser quadrada n x n")

    # soma colunas
    col_sums = [0.0] * n
    for j in range(n):
        s = 0.0
        for i in range(n):
            s += matrix[i][j]
        col_sums[j] = s if s != 0 else 1.0

    # normaliza colunas
    norm = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            norm[i][j] = matrix[i][j] / col_sums[j]

    # média das linhas -> vetor de prioridades
    priorities = [sum(norm[i]) / n for i in range(n)]

    # normaliza prioridades para somarem 1
    total_p = sum(priorities)
    if total_p == 0:
        weights = {labels[i]: 1.0 / n for i in range(n)}
    else:
        weights = {labels[i]: priorities[i] / total_p for i in range(n)}

    # calcular lambda_max aproximado: (A * w) / w e média
    Aw = [0.0] * n
    for i in range(n):
        s = 0.0
        for j in range(n):
            s += matrix[i][j] * priorities[j]
        Aw[i] = s
    # evitar zeros
    ratios = []
    for i in range(n):
        if priorities[i] != 0:
            ratios.append(Aw[i] / priorities[i])
    lambda_max = sum(ratios) / len(ratios) if ratios else n

    CI = (lambda_max - n) / (n - 1) if n > 1 else 0.0
    # RI table (Saaty) para n=1..10
    RI_TABLE = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
    RI = RI_TABLE.get(n, 1.49)
    CR = CI / RI if RI != 0 else 0.0

    return {
        "weights": weights,
        "lambda_max": lambda_max,
        "CI": CI,
        "CR": CR,
        "n": n
    }

# --- NOVA FUNÇÃO (AHP Nível 2) ---
def compute_ahp_level2_from_scores(category_scores: Dict[str, float], category_order: List[str]) -> Dict[str, Any]:
    """
    Gera uma matriz pareada AHP a partir de scores absolutos (método da razão,
    conforme descrito no texto) e calcula os pesos.
    M_ij = score_i / score_j
    """
    n = len(category_order)
    matrix = [[0.0] * n for _ in range(n)]
    scores = [category_scores.get(cat, 0.0) for cat in category_order]

    for i in range(n):
        for j in range(n):
            score_i = scores[i]
            score_j = scores[j]
            if score_j > 0:
                matrix[i][j] = score_i / score_j
            elif score_i > 0:
                # i é > 0 mas j é 0. i é "infinitamente" melhor. Usar 9 (max Saaty).
                matrix[i][j] = 9.0
            else:
                # ambos são 0, são iguais
                matrix[i][j] = 1.0

    # Chamar a função AHP existente para calcular pesos e CR
    return ahp_weights_from_pairwise(matrix, category_order)


# --- LÓGICA ANTIGA (REMOVIDA) ---
# _default_pairwise = [ ... ]
# AHP_RESULT = ahp_weights_from_pairwise(_default_pairwise, category_order)
# AHP_WEIGHTS = AHP_RESULT["weights"]
# ...
# DES_MAX = 0.0
# for field, cat_name in exposicao_autor.items():
#     ...
#     DES_MAX += (cat["Impacto"] * cat["Explorabilidade"]) * AHP_WEIGHTS.get(cat_name, 0)
# --- FIM LÓGICA ANTIGA ---


# --- NOVA LÓGICA AHP 2 NÍVEIS (Início) ---

# --- AHP Nível 1: Pesos dos Critérios ---
# O texto não fornece uma matriz para Impacto vs. Explorabilidade.
# Assumindo pesos iguais (Matriz = [[1, 1], [1, 1]]) como base.
CRITERIA = ["Impacto", "Explorabilidade"]
level1_matrix = [
    [1, 1],  # Impacto vs (Impacto, Explorabilidade)
    [1, 1]   # Explorabilidade vs (Impacto, Explorabilidade)
]
AHP_L1_RESULT = ahp_weights_from_pairwise(level1_matrix, CRITERIA)
AHP_L1_WEIGHTS = AHP_L1_RESULT["weights"] # Resultado: {"Impacto": 0.5, "Explorabilidade": 0.5}

print("[AHP Nível 1] Pesos dos Critérios (w_j):", AHP_L1_WEIGHTS)

# --- AHP Nível 2: Pesos das Categorias (p_ij) (para cada critério) ---

# 1. Para Critério "Impacto"
impacto_scores = {cat: data["Impacto"] for cat, data in categorias.items()}
AHP_L2_IMPACTO_RES = compute_ahp_level2_from_scores(impacto_scores, category_order)
AHP_L2_IMPACTO_WEIGHTS = AHP_L2_IMPACTO_RES["weights"] # p_i,Impacto

# 2. Para Critério "Explorabilidade"
expl_scores = {cat: data["Explorabilidade"] for cat, data in categorias.items()}
AHP_L2_EXPL_RES = compute_ahp_level2_from_scores(expl_scores, category_order)
AHP_L2_EXPL_WEIGHTS = AHP_L2_EXPL_RES["weights"] # p_i,Explorabilidade

print(f"[AHP Nível 2 - Impacto] CR={AHP_L2_IMPACTO_RES['CR']:.4f} (Idealmente < 0.1)")
print(f"[AHP Nível 2 - Explorabilidade] CR={AHP_L2_EXPL_RES['CR']:.4f} (Idealmente < 0.1)")

# --- Pesos Globais (g_i) ---
# g_i = (p_i,Impacto * w_Impacto) + (p_i,Explorabilidade * w_Explorabilidade)
GLOBAL_CATEGORY_WEIGHTS = {}
for cat in category_order:
    w_impacto = AHP_L1_WEIGHTS.get("Impacto", 0.5)
    p_impacto = AHP_L2_IMPACTO_WEIGHTS.get(cat, 0.0)
    w_expl = AHP_L1_WEIGHTS.get("Explorabilidade", 0.5)
    p_expl = AHP_L2_EXPL_WEIGHTS.get(cat, 0.0)

    GLOBAL_CATEGORY_WEIGHTS[cat] = (p_impacto * w_impacto) + (p_expl * w_expl)

print("[AHP Global] Pesos Globais por Categoria (g_i):")
for k, v in GLOBAL_CATEGORY_WEIGHTS.items():
    print(f"  - {k}: {v:.4f}")

# --- DES_MAX (Soma de todos os pesos globais) ---
# Conforme metodologia, DES_MAX é a soma de g_i (exposição total)
DES_MAX = sum(GLOBAL_CATEGORY_WEIGHTS.values())
if DES_MAX == 0:
    print("[WARN] DES_MAX é zero. Verifique os scores de AHP.")
    DES_MAX = 1.0 # Evitar divisão por zero

print(f"[AHP] DES_MAX (Soma de g_i) = {DES_MAX:.4f}")

# --- NOVA LÓGICA AHP 2 NÍVEIS (Fim) ---


# --- Helper functions (unchanged) ---

def is_exposed(val: Any) -> bool:
    """Determina se um campo deve ser contado como 'apareceu/exposto'."""
    if val is None:
        return False
    if isinstance(val, str):
        return val.strip().upper() == "VERDADEIRO"
    if isinstance(val, bool):
        return bool(val)
    if isinstance(val, (int, float)):
        return val != 0
    if isinstance(val, (list, tuple)):
        for x in val:
            if is_exposed(x):
                return True
        return False
    try:
        return str(val).strip().upper() == "VERDADEIRO"
    except Exception:
        return False

# --- FUNÇÃO DE CÁLCULO DO DES (MODIFICADA) ---
def compute_des_from_informacoes(iniciais: Dict[str, Any]) -> float:
    """
    Calcula o DES de acordo com a metodologia AHP de 2 níveis (descrita no texto).
    O score é baseado em quais *categorias* (E_ui) foram expostas, não em quantos *campos*.
    DES_raw = sum(g_i * E_ui)
    """
    if not isinstance(iniciais, dict):
        return 1000.0

    # 1. Identificar *categorias* únicas expostas (E_ui = 1)
    exposed_categories = set()
    for campo, cat_name in exposicao_autor.items():
        if is_exposed(iniciais.get(campo, None)):
            # Se qualquer campo da categoria estiver exposto, a categoria conta
            exposed_categories.add(cat_name)

    # 2. Calcular DES_raw (soma dos pesos globais g_i das categorias expostas)
    des_raw = 0.0
    for cat_name in exposed_categories:
        # Usa os pesos globais (g_i) pré-calculados no escopo do módulo
        des_raw += GLOBAL_CATEGORY_WEIGHTS.get(cat_name, 0.0)

    # 3. Escalar e inverter (DES_final = 1000 - (DES_raw / DES_MAX) * 1000)
    if DES_MAX == 0:
        return 1000.0 # Sem exposição máxima, retorna score máximo (sem exposição)

    # des_raw / DES_MAX nos dá a fração da exposição máxima (0.0 a 1.0)
    # Multiplicamos por 1000 para a escala 0-1000
    des_scaled = (des_raw / DES_MAX) * 1000.0

    # Inverte (1000 = sem exposição, 0 = exposição máxima)
    des_final = 1000.0 - des_scaled
    des_final = max(0.0, min(1000.0, des_final))
    return des_final


# --- Funções de normalização (unchanged) ---

def parse_iso_month(dt_str: Optional[str]) -> str:
    if not dt_str:
        return "unknown"
    try:
        s = dt_str.strip()
        if s.endswith("Z"):
            s = s.replace("Z", "+00:00")
        dt = datetime.fromisoformat(s)
        return dt.strftime("%Y-%m")
    except Exception:
        return "unknown"


def normalize_gender(g: Optional[Any]) -> str:
    if g is None:
        return "Outros"
    try:
        s = str(g).strip()
    except Exception:
        return "Outros"
    if s == "":
        return "Outros"
    s_low = s.lower()
    if s_low in {"masculino", "m", "male", "homem"}:
        return "Masculino"
    if s_low in {"feminino", "f", "female", "mulher"}:
        return "Feminino"
    return "Outros"


def age_range_label(age_value: Optional[Any]) -> str:
    if age_value is None:
        return "Outros"
    try:
        age = int(age_value)
    except Exception:
        return "Outros"
    for rng in ageRanges:
        if rng["min"] <= age <= rng["max"]:
            return rng["label"]
    return "Outros"


def get_des_range_label(score: float) -> Optional[str]:
    if score is None:
        return None
    last_range = DES_RANGES_DEF[-1]
    if last_range["min"] <= score <= last_range["max"]:
        return last_range["label"]
    for rng in DES_RANGES_DEF[:-1]:
        if rng["min"] <= score < rng["max"]:
            return rng["label"]
    if score < 0:
        return DES_RANGES_DEF[0]["label"]
    if score > 1000:
        return DES_RANGES_DEF[-1]["label"]
    return None


# --- Aggregation helpers (unchanged) ---

def make_acc():
    return {
        "count": 0,
        "sum_des": 0.0,
        "count_gt_800": 0,
        "des_range_counts": {label: 0 for label in DES_RANGE_LABELS}
    }


def combine(acc, des_val):
    acc["count"] += 1
    acc["sum_des"] += des_val
    if des_val > 800:
        acc["count_gt_800"] += 1
    range_label = get_des_range_label(des_val)
    if range_label and range_label in acc["des_range_counts"]:
        acc["des_range_counts"][range_label] += 1


def finalize(acc):
    count = acc.get("count", 0)
    if count == 0:
        return {
            "count": 0,
            "avg_des": None,
            "count_gt_800": 0,
            "percent_gt_800": None,
            "des_range_counts": {label: 0 for label in DES_RANGE_LABELS},
            "des_range_percents": {label: 0.0 for label in DES_RANGE_LABELS}
        }
    avg_des = acc["sum_des"] / count
    count_gt_800 = acc.get("count_gt_800", 0)
    percent_gt_800 = (count_gt_800 / count) * 100.0
    range_counts = acc.get("des_range_counts", {label: 0 for label in DES_RANGE_LABELS})
    des_range_percents = {label: (c / count) * 100.0 for label, c in range_counts.items()}
    return {
        "count": count,
        "avg_des": avg_des,
        "count_gt_800": count_gt_800,
        "percent_gt_800": percent_gt_800,
        "des_range_counts": range_counts,
        "des_range_percents": des_range_percents
    }


# --- Main processing function (MODIFICADO APENAS O 'ahp' METADATA) ---

def process_reports_from_iterable(iter_reports):
    overall = make_acc()
    by_age = defaultdict(make_acc)
    by_gender = defaultdict(make_acc)
    by_age_and_gender = defaultdict(lambda: defaultdict(make_acc))
    monthly_general = defaultdict(make_acc)
    monthly_by_age = defaultdict(lambda: defaultdict(make_acc))
    monthly_by_gender = defaultdict(lambda: defaultdict(make_acc))
    monthly_by_age_and_gender = defaultdict(lambda: defaultdict(lambda: defaultdict(make_acc)))

    field_counts_overall = {c: 0 for c in CAMPO_LIST}
    by_age_field_counts = defaultdict(lambda: {c: 0 for c in CAMPO_LIST})
    by_gender_field_counts = defaultdict(lambda: {c: 0 for c in CAMPO_LIST})
    monthly_field_counts = defaultdict(lambda: {c: 0 for c in CAMPO_LIST})

    monthly_by_age_field_counts = defaultdict(lambda: defaultdict(lambda: {c: 0 for c in CAMPO_LIST}))
    monthly_by_gender_field_counts = defaultdict(lambda: defaultdict(lambda: {c: 0 for c in CAMPO_LIST}))
    by_age_and_gender_field_counts = defaultdict(lambda: defaultdict(lambda: {c: 0 for c in CAMPO_LIST}))
    monthly_by_age_and_gender_field_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {c: 0 for c in CAMPO_LIST})))

    for doc in iter_reports:
        report_raw = doc.get("report") if isinstance(doc, dict) and "report" in doc else doc
        if isinstance(report_raw, str):
            try:
                report = json.loads(report_raw)
            except Exception:
                continue
        else:
            report = report_raw
        if not isinstance(report, dict):
            continue

        iniciais = report.get("InformacoesIniciais", {}) or {}
        adicionais = report.get("InformacoesAdicionais", {}) or {}

        # --- CHAMA A NOVA FUNÇÃO DE CÁLCULO ---
        des_score = compute_des_from_informacoes(iniciais)
        # --- FIM DA MUDANÇA ---

        idade_val = adicionais.get("Idade") or adicionais.get("IdadeDeclaradaOuInferidaDoAutor") or adicionais.get("idade")
        genero_val = adicionais.get("Genero") or adicionais.get("GeneroDeclarado") or adicionais.get("GeneroAutoDeclaradoOuInferidoDoAutor") or adicionais.get("genero")
        age_label = age_range_label(idade_val)
        gen_label = normalize_gender(genero_val)

        dt = adicionais.get("DataUltimoTweet") or adicionais.get("data_ultimo_tweet") or adicionais.get("DataUltimoPost")
        month = parse_iso_month(dt)

        combine(overall, des_score)
        combine(by_age[age_label], des_score)
        combine(by_gender[gen_label], des_score)
        combine(by_age_and_gender[age_label][gen_label], des_score)
        combine(monthly_general[month], des_score)
        combine(monthly_by_age[month][age_label], des_score)
        combine(monthly_by_gender[month][gen_label], des_score)
        combine(monthly_by_age_and_gender[month][age_label][gen_label], des_score)

        for campo in CAMPO_LIST:
            present = is_exposed(iniciais.get(campo, None))
            if present:
                field_counts_overall[campo] += 1
                monthly_field_counts[month][campo] += 1
                by_age_field_counts[age_label][campo] += 1
                by_gender_field_counts[gen_label][campo] += 1
                monthly_by_age_field_counts[month][age_label][campo] += 1
                monthly_by_gender_field_counts[month][gen_label][campo] += 1
                by_age_and_gender_field_counts[age_label][gen_label][campo] += 1
                monthly_by_age_and_gender_field_counts[month][age_label][gen_label][campo] += 1

    by_age["Todos"] = overall
    agg_overall_final = finalize(overall)

    result = {
        "overall": agg_overall_final,
        "by_age": {k: finalize(v) for k, v in by_age.items()},
        "by_gender": {k: finalize(v) for k, v in by_gender.items()},
        "by_age_and_gender": {
            age: {g: finalize(acc) for g, acc in gen_map.items()}
            for age, gen_map in by_age_and_gender.items()
        },
        "monthly_general": {k: finalize(v) for k, v in monthly_general.items()},
        "monthly_by_age": {
            month: {age: finalize(acc) for age, acc in age_map.items()}
            for month, age_map in monthly_by_age.items()
        },
        "monthly_by_gender": {
            month: {g: finalize(acc) for g, acc in gen_map.items()}
            for month, gen_map in monthly_by_gender.items()
        },
        "monthly_by_age_and_gender": {
            month: {
                age: {g: finalize(acc) for g, acc in gen_map.items()}
                for age, gen_map in age_map.items()
            }
            for month, age_map in monthly_by_age_and_gender.items()
        },
        "field_counts_overall": field_counts_overall,
        "monthly_field_counts": {m: v for m, v in monthly_field_counts.items()},
        "by_age_field_counts": {age: v for age, v in by_age_field_counts.items()},
        "by_gender_field_counts": {g: v for g, v in by_gender_field_counts.items()},
        "monthly_by_age_field_counts": {m: v for m, v in monthly_by_age_field_counts.items()},
        "monthly_by_gender_field_counts": {m: v for m, v in monthly_by_gender_field_counts.items()},
        "by_age_and_gender_field_counts": {a: v for a, v in by_age_and_gender_field_counts.items()},
        "monthly_by_age_and_gender_field_counts": {m: v for m, v in monthly_by_age_and_gender_field_counts.items()},
        
        # --- AHP metadata (ATUALIZADO) ---
        "ahp": {
            "method": "AHP 2-Level (Texto)",
            "des_max_global": DES_MAX,
            "global_category_weights_g_i": GLOBAL_CATEGORY_WEIGHTS,
            "level1_criteria_weights_w_j": AHP_L1_WEIGHTS,
            "level2_category_weights_p_ij": {
                "Impacto": {
                    "weights": AHP_L2_IMPACTO_WEIGHTS,
                    "CR": AHP_L2_IMPACTO_RES["CR"]
                },
                "Explorabilidade": {
                    "weights": AHP_L2_EXPL_WEIGHTS,
                    "CR": AHP_L2_EXPL_RES["CR"]
                }
            }
        }
    }
    return result


def main():
    # ... (O restante da função main() permanece inalterado) ...
    script_to_run_final = None

    use_db = all([USER, PASS, HOST, PORT, AUTH_DB, DB_NAME]) and MongoClient is not None
    docs_iter = None
    client = None
    connected_to_db = False

    if use_db:
        try:
            tls_ca = os.getenv("MONGO_TLS_CA_FILE", "rds-combined-ca-bundle.pem")
            if not os.path.exists(tls_ca):
                print(f"[WARN] Arquivo TLS CA não encontrado em {tls_ca}. Tentando conectar sem TLS CA.")
                uri = (
                    f"mongodb://{HOST}:{PORT}/?tls=true"
                    f"&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false&authSource={AUTH_DB}"
                )
            else:
                 uri = (
                    f"mongodb://{HOST}:{PORT}/?tls=true&tlsCAFile={tls_ca}"
                    f"&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false&authSource={AUTH_DB}"
                )
            client = MongoClient(uri, username=USER, password=PASS, serverSelectionTimeoutMS=5000)
            client.server_info()
            db = client[DB_NAME]
            coll = db[COL_REPORT]
            docs_iter = coll.find({}, projection={"report": 1})
            connected_to_db = True
            print("[INFO] Conectado ao MongoDB. Lendo coleção 'reports'.")
        except Exception as e:
            print(f"[WARN] Falha ao conectar ao MongoDB: {e}. Irei usar fallback.")

    if not connected_to_db:
        fallback_path = "test.json"
        try:
            print("[INFO] DB indisponível. Criando 'test.json' de fallback no CWD.")
            # ... (Dados de teste inalterados) ...
            test_data = [
                {
                    "report": {
                        "InformacoesIniciais": {
                            "NomeDeclaradoOuSugeridoPeloAutor": "VERDADEIRO",
                            "IdadeDeclaradaOuInferidaDoAutor": "VERDADEIRO",
                            "MencaoDoAutorADadosBancarios": "VERDADEIRO"
                        },
                        "InformacoesAdicionais": {
                            "Idade": 22,
                            "Genero": "Masculino",
                            "DataUltimoTweet": "2023-01-10T12:00:00Z"
                        }
                    }
                },
                {
                    "report": {
                        "InformacoesIniciais": {
                            "NomeDeclaradoOuSugeridoPeloAutor": "VERDADEIRO",
                            "MencaoDoAutorAPosseDeCPF": "VERDADEIRO"
                        },
                        "InformacoesAdicionais": {
                            "Idade": 35,
                            "Genero": "Feminino",
                            "DataUltimoTweet": "2023-01-15T12:00:00Z"
                        }
                    }
                },
                {
                    "report": {
                        "InformacoesIniciais": {
                            "MencaoDoAutorAPosseDeCPF": "VERDADEIRO",
                            "MencaoDoAutorAContatoPessoal_TelefoneEmail": "VERDADEIRO"
                        },
                        "InformacoesAdicionais": {
                            "Idade": 40,
                            "Genero": "Feminino",
                            "DataUltimoTweet": "2023-02-05T12:00:00Z"
                        }
                    }
                },
                {
                     "report": {
                        "InformacoesIniciais": {
                            "MencaoDoAutorAPosseDeCPF": "VERDADEIRO"
                        },
                        "InformacoesAdicionais": {
                            "Idade": 22,
                            "Genero": "Masculino",
                            "DataUltimoTweet": "2023-02-10T12:00:00Z"
                        }
                    }
                },
                {
                    "report": {
                        "InformacoesIniciais": {},
                        "InformacoesAdicionais": {
                            "Idade": 68,
                            "Genero": "nb",
                            "DataUltimoTweet": "2023-02-10T12:00:00Z"
                        }
                    }
                }
            ]
            with open(fallback_path, "w", encoding="utf-8") as fh:
                json.dump(test_data, fh)
            with open(fallback_path, "r", encoding="utf-8") as fh:
                sample = json.load(fh)
                if isinstance(sample, dict) and "InformacoesIniciais" in sample:
                    docs_iter = [{"report": sample}]
                elif isinstance(sample, list):
                    docs_iter = [{"report": x} if not isinstance(x, dict) or "report" not in x else x for x in sample]
                else:
                    docs_iter = [{"report": sample}]
            print(f"[INFO] Usando fallback: {fallback_path}")
        except Exception as e_fallback:
             print(f"[ERROR] Falha ao criar ou ler o arquivo de fallback: {e_fallback}")
             docs_iter = []

    if not docs_iter:
        print("[ERROR] Nenhum documento para processar (DB e fallback falharam).")
        agg = process_reports_from_iterable([])
    else:
        agg = process_reports_from_iterable(docs_iter)

    print("[INFO] Resultados da Agregação (Metodologia AHP 2 Níveis):")
    print(json.dumps(agg, ensure_ascii=False, indent=2))

    if script_to_run_final:
        try:
            with open("aggregate_reports_final.py", "w", encoding="utf-8") as f:
                f.write(script_to_run_final)
            print("[INFO] Script modificado salvo em 'aggregate_reports_final.py'.")
        except Exception as e_save_script:
            print(f"[WARN] Falha ao salvar script modificado: {e_save_script}")
    else:
        print("[INFO] 'script_to_run_final' não definido, pulando salvamento do script.")

    try:
        with open("aggregation_results_final.json", "w", encoding="utf-8") as f:
            json.dump(agg, f, ensure_ascii=False, indent=2)
        print("[INFO] Resultados da agregação salvos em 'aggregation_results_final.json'.")
    except Exception as e_save_json:
        print(f"[WARN] Falha ao salvar resultados da agregação: {e_save_json}")

    if connected_to_db and client is not None:
        try:
            summary_coll = db.get_collection("aggregates")
            doc = {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "aggregates": agg
            }
            summary_coll.insert_one(doc)
            print("[INFO] Agregados gravados em 'aggregates'.")
        except Exception as e:
            print(f"[WARN] Não foi possível gravar agregados: {e}")


if __name__ == "__main__":
    main()