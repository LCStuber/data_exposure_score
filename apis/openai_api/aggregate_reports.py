import os
import json
from datetime import datetime
from collections import defaultdict
from typing import Any, Dict, Optional

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
TOTAL_FIELDS = len(CAMPO_LIST)

categorias = {
    "Informação Financeira": {"Impacto": 10, "Explorabilidade": 8},
    "Documentos Pessoais": {"Impacto": 10, "Explorabilidade": 7},
    "Localização em Tempo Real": {"Impacto": 8, "Explorabilidade": 9},
    "Contato Pessoal": {"Impacto": 8, "Explorabilidade": 10},
    "Rotina/Hábitos": {"Impacto": 6, "Explorabilidade": 6},
    "Posicionamento e Características Pessoais": {"Impacto": 4, "Explorabilidade": 5}
}

exposicao_autor = {
    "NomeDeclaradoOuSugeridoPeloAutor": categorias["Posicionamento e Características Pessoais"],
    "IdadeDeclaradaOuInferidaDoAutor": categorias["Posicionamento e Características Pessoais"],
    "GeneroAutoDeclaradoOuInferidoDoAutor": categorias["Posicionamento e Características Pessoais"],
    "OrientacaoSexualDeclaradaOuSugeridaPeloAutor": categorias["Posicionamento e Características Pessoais"],
    "StatusDeRelacionamentoDeclaradoOuSugeridoDoAutor": categorias["Posicionamento e Características Pessoais"],
    "ProfissaoOcupacaoDeclaradaPeloAutor": categorias["Rotina/Hábitos"],
    "NivelEducacionalDeclaradoOuInferidoDoAutor": categorias["Posicionamento e Características Pessoais"],
    "LocalizacaoPrincipalDeclaradaOuInferidaDoAutor": categorias["Localização em Tempo Real"],
    "CidadesComRelevanciaPessoalParaOAutor": categorias["Localização em Tempo Real"],
    "CrencaReligiosaDeclaradaOuSugeridaPeloAutor": categorias["Posicionamento e Características Pessoais"],
    "OpinioesPoliticasExpressasPeloAutor": categorias["Posicionamento e Características Pessoais"],
    "ExposicaoDeRelacionamentosPessoaisPeloAutor": categorias["Posicionamento e Características Pessoais"],
    "MencaoDoAutorAPosseDeCPF": categorias["Documentos Pessoais"],
    "MencaoDoAutorAPosseDeRG": categorias["Documentos Pessoais"],
    "MencaoDoAutorAPosseDePassaporte": categorias["Documentos Pessoais"],
    "MencaoDoAutorAPosseDeTituloEleitor": categorias["Documentos Pessoais"],
    "EtniaOuRacaAutoDeclaradaPeloAutor": categorias["Posicionamento e Características Pessoais"],
    "MencaoDoAutorAEnderecoResidencial": categorias["Localização em Tempo Real"],
    "MencaoDoAutorAContatoPessoal_TelefoneEmail": categorias["Contato Pessoal"],
    "MencaoDoAutorADadosBancarios": categorias["Informação Financeira"],
    "MencaoDoAutorACartaoDeEmbarque": categorias["Documentos Pessoais"],
    "IndicadoresDeRendaPropriaMencionadosPeloAutor": categorias["Informação Financeira"],
    "MencoesAPatrimonioPessoalDoAutor": categorias["Informação Financeira"],
    "LocalDeTrabalhoOuEstudoDeclaradoPeloAutor": categorias["Rotina/Hábitos"],
    "MencaoDoAutorARecebimentoDeBeneficioSocial": categorias["Informação Financeira"],
    "MencoesAoProprioHistoricoFinanceiroPeloAutor": categorias["Informação Financeira"],
    "MencoesDoAutorAProprioHistoricoCriminal": categorias["Documentos Pessoais"],
    "MencaoDoAutorAPosseDeChavePix": categorias["Informação Financeira"]
}

DES_MAX = sum(v["Impacto"] * v["Explorabilidade"] for v in exposicao_autor.values())

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

def compute_des_from_informacoes(iniciais: Dict[str, Any]) -> float:
    """
    Implementa exatamente a fórmula do des.py:
      - percorre exposicao_autor
      - se campo marcado (VERDADEIRO / True / lista contendo VERDADEIRO / número != 0) -> curr_value = 1
      - curr_value *= Impacto * Explorabilidade
      - des = soma(curr_value)
      - des_scaled = (des / des_max) * 1000
      - des_final = 1000 - des_scaled
    Retorna des_final (valor mais alto = mais "seguro" segundo seu notebook).
    """
    des = 0.0
    if not isinstance(iniciais, dict):
        return 1000.0 
    for campo, weights in exposicao_autor.items():
        present = False
        val = iniciais.get(campo, None)
        if val is None:
            present = False
        elif isinstance(val, str):
            if val.strip().upper() == "VERDADEIRO":
                present = True
        elif isinstance(val, bool):
            present = bool(val)
        elif isinstance(val, (int, float)):
            present = (val != 0)
        elif isinstance(val, (list, tuple)):
            for x in val:
                if (isinstance(x, str) and x.strip().upper() == "VERDADEIRO") or x is True or (isinstance(x, (int,float)) and x!=0):
                    present = True
                    break
        else:
            try:
                if str(val).strip().upper() == "VERDADEIRO":
                    present = True
            except Exception:
                present = False

        if present:
            curr_value = weights["Impacto"] * weights["Explorabilidade"]
            des += curr_value

    if DES_MAX == 0:
        return 1000.0
    des_scaled = (des / DES_MAX) * 1000.0
    des_final = 1000.0 - des_scaled
    if des_final < 0:
        des_final = 0.0
    if des_final > 1000:
        des_final = 1000.0
    return des_final

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

        iniciais = report.get("InformacoesIniciais", {}) or {}
        adicionais = report.get("InformacoesAdicionais", {}) or {}

        des_score = compute_des_from_informacoes(iniciais)

        combine(overall, des_score)

        idade_val = None
        genero_val = None
        if isinstance(adicionais, dict):

            idade_val = adicionais.get("Idade") or adicionais.get("IdadeDeclaradaOuInferidaDoAutor") or adicionais.get("idade")
            genero_val = adicionais.get("Genero") or adicionais.get("GeneroDeclarado") or adicionais.get("GeneroAutoDeclaradoOuInferidoDoAutor") or adicionais.get("genero")

        age_label = age_range_label(idade_val)
        gen_label = normalize_gender(genero_val)

        combine(by_age[age_label], des_score)
        combine(by_gender[gen_label], des_score)

        dt = None
        if isinstance(adicionais, dict):
            dt = adicionais.get("DataUltimoTweet") or adicionais.get("data_ultimo_tweet") or adicionais.get("DataUltimoPost")
        month = parse_iso_month(dt)
        combine(monthly_general[month], des_score)
        combine(monthly_by_age[month][age_label], des_score)
        combine(monthly_by_gender[month][gen_label], des_score)

    agg_overall_final = finalize(overall)
    todos_acc = {"count": agg_overall_final["count"], "sum_des": (agg_overall_final["avg_des"] * agg_overall_final["count"]) if agg_overall_final["avg_des"] is not None else 0.0}

    by_age["Todos"] = todos_acc

    result = {
        "overall": agg_overall_final,
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
            print("[INFO] Conectado ao MongoDB. Lendo coleção 'reports'.")
        except Exception as e:
            print(f"[WARN] Falha ao conectar ao MongoDB: {e}. Irei usar fallback /mnt/data/test.json.")

    if not connected_to_db:
        fallback_path = "/mnt/data/test.json"
        if not os.path.exists(fallback_path):
            raise RuntimeError(f"DB indisponível e fallback não encontrado em {fallback_path}")
        with open(fallback_path, "r", encoding="utf-8") as fh:
            sample = json.load(fh)
            if isinstance(sample, dict) and "InformacoesIniciais" in sample:
                docs_iter = [{"report": sample}]
            elif isinstance(sample, list):
                docs_iter = [{"report": x} if not isinstance(x, dict) or "report" not in x else x for x in sample]
            else:
                docs_iter = [{"report": sample}]
        print(f"[INFO] Usando fallback: {fallback_path}")

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
            print("[INFO] Agregados gravados em 'reports_aggregates'.")
        except Exception as e:
            print(f"[WARN] Não foi possível gravar agregados: {e}")

if __name__ == "__main__":
    main()
