import os
import json
from datetime import datetime
from collections import defaultdict
from statistics import mean, median
from pymongo import MongoClient

USER = os.getenv("MONGO_USER")
PASS = os.getenv("MONGO_PASS")
HOST = os.getenv("MONGO_HOST", "localhost")
PORT = os.getenv("MONGO_PORT", "27017")
AUTH_DB = os.getenv("MONGO_AUTH_DB", "admin")
DB_NAME = os.getenv("MONGO_DB", "test")
COL_REPORTS = os.getenv("MONGO_COLLECTION_REPORTS", "reports")
COL_AGG = os.getenv("MONGO_COLLECTION_AGGREGATES", "reports_aggregates")

if not all([USER, PASS, HOST, PORT, AUTH_DB, DB_NAME]):
    raise RuntimeError("Please set MONGO env vars (MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT, MONGO_AUTH_DB, MONGO_DB)")

uri = f"mongodb://{HOST}:{PORT}/?authSource={AUTH_DB}"
client = MongoClient(uri, username=USER, password=PASS)
db = client[DB_NAME]
reports_coll = db[COL_REPORTS]
agg_coll = db[COL_AGG]

categories = {
    "Informação Financeira": {"Impacto": 10, "Explorabilidade": 8},
    "Documentos Pessoais": {"Impacto": 10, "Explorabilidade": 7},
    "Localização em Tempo Real": {"Impacto": 8, "Explorabilidade": 9},
    "Contato Pessoal": {"Impacto": 8, "Explorabilidade": 10},
    "Rotina/Hábitos": {"Impacto": 6, "Explorabilidade": 6},
    "Posicionamento e Características Pessoais": {"Impacto": 4, "Explorabilidade": 5},
}

# Map each report field to a category (best-effort mapping following your notebook fields list)
field_to_category = {
    "NomeDeclaradoOuSugeridoPeloAutor": "Posicionamento e Características Pessoais",
    "IdadeDeclaradaOuInferidaDoAutor": "Posicionamento e Características Pessoais",
    "GeneroAutoDeclaradoOuInferidoDoAutor": "Posicionamento e Características Pessoais",
    "OrientacaoSexualDeclaradaOuSugeridaPeloAutor": "Posicionamento e Características Pessoais",
    "StatusDeRelacionamentoDeclaradoOuSugeridoPeloAutor": "Posicionamento e Características Pessoais",
    "ProfissaoOcupacaoDeclaradaPeloAutor": "Rotina/Hábitos",
    "NivelEducacionalDeclaradoOuInferidoDoAutor": "Rotina/Hábitos",
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
    "MencaoDoAutorAEnderecoResidencial": "Contato Pessoal",
    "MencaoDoAutorAContatoPessoal_TelefoneEmail": "Contato Pessoal",
    "MencaoDoAutorADadosBancarios": "Informação Financeira",
    "MencaoDoAutorACartaoDeEmbarque": "Documentos Pessoais",
    "IndicadoresDeRendaPropriaMencionadosPeloAutor": "Informação Financeira",
    "MencoesAPatrimonioPessoalDoAutor": "Informação Financeira",
    "LocalDeTrabalhoOuEstudoDeclaradoPeloAutor": "Rotina/Hábitos",
    "MencaoDoAutorARecebimentoDeBeneficioSocial": "Informação Financeira",
    "MencoesAoProprioHistoricoFinanceiroPeloAutor": "Informação Financeira",
    "MencoesDoAutorAProprioHistoricoCriminal": "Documentos Pessoais",
    "MencaoDoAutorAPosseDeChavePix": "Informação Financeira",
}

field_weight = {}
for fld, cat_name in field_to_category.items():
    cat = categories.get(cat_name)
    if not cat:
        raise RuntimeError(f"Missing category mapping for {cat_name}")
    field_weight[fld] = cat["Impacto"] * cat["Explorabilidade"]

DES_MAX = sum(field_weight.values())

age_ranges = [
  { "label": "Todos", "min": 0, "max": 999 },
  { "label": "< 18", "min": 0, "max": 17 },
  { "label": "18-24", "min": 18, "max": 24 },
  { "label": "25-34", "min": 25, "max": 34 },
  { "label": "35-44", "min": 35, "max": 44 },
  { "label": "45-54", "min": 45, "max": 54 },
  { "label": "55-64", "min": 55, "max": 64 },
  { "label": "65+", "min": 65, "max": 999 },
]

def normalize_field_value(v):
    """Return True if the field indicates 'VERDADEIRO' (handles strings and lists)."""
    if v is None:
        return False
    if isinstance(v, list):
        return any((str(x).strip().upper() == "VERDADEIRO") for x in v)
    if isinstance(v, str):
        return v.strip().upper() == "VERDADEIRO"
    if isinstance(v, bool):
        return v
    return bool(v)

def compute_des_for_report(report_obj):
    """
    Expect report_obj to be the parsed JSON saved in your reports collection under 'report' field:
    - report_obj["InformacoesIniciais"] : dict with many keys with "VERDADEIRO"/"FALSO" or lists.
    - report_obj["InformacoesAdicionais"]["Idade"] (optional)
    - report_obj["InformacoesAdicionais"]["Genero"] (optional)
    - report_obj["InformacoesAdicionais"]["DataUltimoTweet"] (optional ISO)
    """
    info_init = report_obj.get("InformacoesIniciais", {}) or {}
    des = 0.0
    for fld, weight in field_weight.items():
        v = info_init.get(fld)
        if normalize_field_value(v):
            des += weight

    des_scaled = (des / DES_MAX) * 1000 if DES_MAX > 0 else 0.0
    des_final = 1000.0 - des_scaled
    return {
        "des_raw": des,
        "des_scaled": des_scaled,
        "des_final": des_final
    }

def parse_month_from_iso(isotext):
    if not isotext:
        return None
    try:
        if isotext.endswith("Z"):
            isotext = isotext.replace("Z", "+00:00")
        dt = datetime.fromisoformat(isotext)
        return dt.strftime("%Y-%m")
    except Exception:
        try:
            dt = datetime.strptime(isotext[:10], "%Y-%m-%d")
            return dt.strftime("%Y-%m")
        except Exception:
            return None

def choose_age_range_label(age):
    try:
        if age is None:
            return "Outros"
        age = int(age)
    except Exception:
        return "Outros"
    for r in age_ranges:
        if r["min"] <= age <= r["max"] and r["label"] != "Todos":
            return r["label"]
    return "Todos"

def normalize_gender(g):
    if not g:
        return "Outros"
    s = str(g).strip().lower()
    if s in ("masculino", "m", "male", "homem"):
        return "Masculino"
    if s in ("feminino", "f", "female", "mulher"):
        return "Feminino"
    return "Outros"

overall_docs = []
by_age = defaultdict(list)    
by_gender = defaultdict(list)   
monthly = defaultdict(lambda: {
    "docs": [],
    "by_age": defaultdict(list),
    "by_gender": defaultdict(list)
})

cursor = reports_coll.find({}, projection={"report": 1})
total = reports_coll.count_documents({})
print(f"[INFO] Found {total} report docs in collection '{COL_REPORTS}'")

for doc in cursor:
    report_obj = doc.get("report")
    if report_obj is None:
        continue
    des_stats = compute_des_for_report(report_obj)
    des_final = des_stats["des_final"]

    info_add = report_obj.get("InformacoesAdicionais", {}) or {}
    idade = info_add.get("Idade")
    genero = info_add.get("Genero")
    data_ultimo = info_add.get("DataUltimoTweet")

    age_label = choose_age_range_label(idade)
    gender_label = normalize_gender(genero)
    month_label = parse_month_from_iso(data_ultimo) or "sem_data"

    overall_docs.append(des_final)
    by_age[age_label].append(des_final)
    by_gender[gender_label].append(des_final)

    monthly_entry = monthly[month_label]
    monthly_entry["docs"].append(des_final)
    monthly_entry["by_age"][age_label].append(des_final)
    monthly_entry["by_gender"][gender_label].append(des_final)

def summary_stats(values):
    if not values:
        return {"count": 0, "mean": None, "median": None, "min": None, "max": None}
    return {
        "count": len(values),
        "mean": float(mean(values)),
        "median": float(median(values)),
        "min": float(min(values)),
        "max": float(max(values))
    }

overall_summary = {
    "total_docs": len(overall_docs),
    "des": summary_stats(overall_docs),
    "by_age": {k: summary_stats(v) for k, v in by_age.items()},
    "by_gender": {k: summary_stats(v) for k, v in by_gender.items()},
    "DES_MAX_used": DES_MAX
}

monthly_summary = {}
for m, entry in sorted(monthly.items()):
    monthly_summary[m] = {
        "total_docs": len(entry["docs"]),
        "des": summary_stats(entry["docs"]),
        "by_age": {k: summary_stats(v) for k, v in entry["by_age"].items()},
        "by_gender": {k: summary_stats(v) for k, v in entry["by_gender"].items()},
    }

final_doc = {
    "_id": f"agg_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
    "generated_at": datetime.utcnow(),
    "overall": overall_summary,
    "monthly": monthly_summary,
    "meta": {
        "reports_collection": COL_REPORTS,
        "computed_from_docs": total
    }
}

agg_coll.replace_one({"_id": final_doc["_id"]}, final_doc, upsert=True)
print("[INFO] Aggregation written to collection:", COL_AGG)

print(json.dumps({
    "generated_at": final_doc["generated_at"].isoformat() + "Z",
    "overall": overall_summary,
    "sample_months_count": len(monthly_summary)
}, default=str, indent=2))
