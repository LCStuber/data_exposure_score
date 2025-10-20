import os
import json
from datetime import datetime
from collections import defaultdict
from typing import Any, Dict, Optional


try:
    from pymongo import MongoClient, errors as pymongo_errors
except Exception:
    MongoClient = None
    pymongo_errors = None


USER = os.getenv("MONGO_USER")
PASS = os.getenv("MONGO_PASS")
HOST = os.getenv("MONGO_HOST")
PORT = os.getenv("MONGO_PORT")
AUTH_DB = os.getenv("MONGO_AUTH_DB")
DB_NAME = os.getenv("MONGO_DB")
COL_REPORT = os.getenv("MONGO_COLLECTION_REPORTS", "reports")

ageRanges = [
  { "label": "Todos", "min": 0, "max": 999 },
  { "label": "< 18", "min": 0, "max": 17 },
  { "label": "18-24", "min": 18, "max": 24 },
  { "label": "25-34", "min": 25, "max": 34 },
  { "label": "35-44", "min": 35, "max": 44 },
  { "label": "45-54", "min": 45, "max": 54 },
  { "label": "55-64", "min": 55, "max": 64 },
  { "label": "65+", "min": 65, "max": 999 },
]

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
    "MencoesAoProprioHistoricoFinanceiroDoAutor",
    "MencoesDoAutorAProprioHistoricoCriminal",
    "MencaoDoAutorAPosseDeChavePix"
]

TOTAL_FIELDS = len(CAMPO_LIST)


def parse_iso_month(dt_str: Optional[str]) -> str:
    """Return 'YYYY-MM' for an ISO datetime string; 'unknown' for None/invalid."""
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

def normalize_gender(g: Optional[str]) -> str:
    if not g:
        return "Outros"
    g = g.strip().lower()
    if g in {"masculino", "m", "male", "homem"}:
        return "Masculino"
    if g in {"feminino", "f", "female", "mulher"}:
        return "Feminino"
    return "Outros"

def age_range_label(age: Optional[int]) -> str:
    try:
        if age is None:
            return "Outros"
        age = int(age)
    except Exception:
        return "Outros"
    for rng in ageRanges:
        if rng["min"] <= age <= rng["max"]:
            return rng["label"]
    return "Outros"

def compute_des_from_informacoes(iniciais: Dict[str, Any]) -> float:
    """
    Simple DES calculation:
      - count how many CAMPO_LIST fields are marked as 'VERDADEIRO'
      - DES = (count / TOTAL_FIELDS) * 100  (score 0..100)
    This follows the structure in your sample test.json (InformacoesIniciais containing VERDADEIRO/FALSO).
    If you want the precise formula from des.ipynb, paste that function and I will integrate it exactly.
    """
    if not isinstance(iniciais, dict):
        return 0.0
    true_count = 0
    for key in CAMPO_LIST:
        val = iniciais.get(key)
        if val is None:
            continue
        if isinstance(val, str):
            if val.strip().upper() == "VERDADEIRO":
                true_count += 1
        elif isinstance(val, (list, tuple)):
            if any((isinstance(x, str) and x.strip().upper() == "VERDADEIRO") or x is True for x in val):
                true_count += 1
        elif isinstance(val, bool):
            if val:
                true_count += 1
        elif isinstance(val, (int, float)) and val != 0:
            true_count += 1
    return (true_count / TOTAL_FIELDS) * 100.0 if TOTAL_FIELDS > 0 else 0.0


def make_acc():
    return {"count": 0, "sum_des": 0.0}

def combine(acc, des_val):
    acc["count"] += 1
    acc["sum_des"] += des_val

def finalize(acc):
    if acc["count"] == 0:
        return {"count": 0, "avg_des": None}
    return {"count": acc["count"], "avg_des": acc["sum_des"] / acc["count"]}


def process_reports_from_iterable(iter_reports):
    overall = make_acc()
    by_age = defaultdict(make_acc) 
    by_gender = defaultdict(make_acc)

    monthly_general = defaultdict(make_acc)
    monthly_by_age = defaultdict(lambda: defaultdict(make_acc))   
    monthly_by_gender = defaultdict(lambda: defaultdict(make_acc))

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

        iniciais = report.get("InformacoesIniciais", {})
        adicionais = report.get("InformacoesAdicionais", {})

        des_score = compute_des_from_informacoes(iniciais)

        combine(overall, des_score)

        idade = adicionais.get("Idade") if isinstance(adicionais, dict) else None
        genero = adicionais.get("Genero") if isinstance(adicionais, dict) else None

        age_label = age_range_label(idade)
        gen_label = normalize_gender(genero)

        combine(by_age[age_label], des_score)
        combine(by_gender[gen_label], des_score)

        dt = adicionais.get("DataUltimoTweet") if isinstance(adicionais, dict) else None
        month = parse_iso_month(dt)
        combine(monthly_general[month], des_score)
        combine(monthly_by_age[month][age_label], des_score)
        combine(monthly_by_gender[month][gen_label], des_score)

    result = {
        "overall": finalize(overall),
        "by_age": {k: finalize(v) for k, v in by_age.items()},
        "by_gender": {k: finalize(v) for k, v in by_gender.items()},
        "monthly_general": {k: finalize(v) for k, v in monthly_general.items()},
        "monthly_by_age": {
            month: {age: finalize(acc) for age, acc in age_map.items()}
            for month, age_map in monthly_by_age.items()
        },
        "monthly_by_gender": {
            month: {g: finalize(acc) for g, acc in gen_map.items()}
            for month, gen_map in monthly_by_gender.items()
        },
    }
    return result


def main():
    use_db = all([USER, PASS, HOST, PORT, AUTH_DB, DB_NAME]) and MongoClient is not None
    docs_iter = None
    client = None
    connected_to_db = False

    if use_db:
        try:
            tls_ca = os.getenv("MONGO_TLS_CA_FILE", "rds-combined-ca-bundle.pem")
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
            print("[INFO] Connected to MongoDB. Reading reports collection.")
        except Exception as e:
            print(f"[WARN] Could not connect to MongoDB: {e}. Falling back to local file (test.json).")

    if not connected_to_db:
        fallback_path = "/mnt/data/test.json"
        if not os.path.exists(fallback_path):
            raise RuntimeError(f"DB unavailable and fallback file not found at {fallback_path}.")
        with open(fallback_path, "r", encoding="utf-8") as fh:
            sample = json.load(fh)
            if isinstance(sample, dict) and "InformacoesIniciais" in sample:
                docs_iter = [{"report": sample}]
            elif isinstance(sample, list):
                docs_iter = [{"report": x} if not isinstance(x, dict) or "report" not in x else x for x in sample]
            else:
                docs_iter = [{"report": sample}]
        print(f"[INFO] Using fallback file: {fallback_path} (example/test data).")

    agg = process_reports_from_iterable(docs_iter)

    print(json.dumps(agg, ensure_ascii=False, indent=2))

    if connected_to_db and client is not None:
        try:
            summary_coll = db.get_collection("reports_aggregates")
            doc = {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "aggregates": agg
            }
            summary_coll.insert_one(doc)
            print("[INFO] Aggregates stored to `reports_aggregates` collection.")
        except Exception as e:
            print(f"[WARN] Could not write aggregates to DB: {e}")


if __name__ == "__main__":
    main()
