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

def compute_des_from_informacoes(iniciais: Dict[str, Any]) -> float:
    des = 0.0
    if not isinstance(iniciais, dict):
        return 1000.0
    for campo, weights in exposicao_autor.items():
        if is_exposed(iniciais.get(campo, None)):
            des += weights["Impacto"] * weights["Explorabilidade"]
    if DES_MAX == 0:
        return 1000.0
    des_scaled = (des / DES_MAX) * 1000.0
    des_final = 1000.0 - des_scaled
    des_final = max(0.0, min(1000.0, des_final))
    return des_final

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
    """Maps a DES score to its corresponding range label."""
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


def make_acc():
    """Cria um acumulador com as novas métricas."""
    return {
        "count": 0,
        "sum_des": 0.0,
        "count_gt_800": 0, 
        "des_range_counts": {label: 0 for label in DES_RANGE_LABELS} 
    }

def combine(acc, des_val):
    """Adiciona um valor de DES ao acumulador."""
    acc["count"] += 1
    acc["sum_des"] += des_val
    
    if des_val > 800:
        acc["count_gt_800"] += 1
    
    range_label = get_des_range_label(des_val)
    if range_label and range_label in acc["des_range_counts"]:
        acc["des_range_counts"][range_label] += 1

def finalize(acc):
    """Finaliza o acumulador, calculando médias e percentuais."""
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
    des_range_percents = {
        label: (c / count) * 100.0 
        for label, c in range_counts.items()
    }

    return {
        "count": count,
        "avg_des": avg_des,
        "count_gt_800": count_gt_800,
        "percent_gt_800": percent_gt_800,
        "des_range_counts": range_counts,
        "des_range_percents": des_range_percents
    }


def process_reports_from_iterable(iter_reports):
    # --- Acumuladores de Score DES ---
    overall = make_acc()
    by_age = defaultdict(make_acc)
    by_gender = defaultdict(make_acc)
    by_age_and_gender = defaultdict(lambda: defaultdict(make_acc))
    monthly_general = defaultdict(make_acc)
    monthly_by_age = defaultdict(lambda: defaultdict(make_acc))
    monthly_by_gender = defaultdict(lambda: defaultdict(make_acc))
    monthly_by_age_and_gender = defaultdict(lambda: defaultdict(lambda: defaultdict(make_acc))) # <<< ADICIONADO NA SUA SOLICITAÇÃO ANTERIOR

    # --- Acumuladores de Contagem de Campos (Field Counts) ---
    field_counts_overall = {c: 0 for c in CAMPO_LIST}
    by_age_field_counts = defaultdict(lambda: {c: 0 for c in CAMPO_LIST})
    by_gender_field_counts = defaultdict(lambda: {c: 0 for c in CAMPO_LIST})
    monthly_field_counts = defaultdict(lambda: {c: 0 for c in CAMPO_LIST})
    
    # <<< INÍCIO: NOVOS ACUMULADORES DE FIELD COUNT ADICIONADOS >>>
    monthly_by_age_field_counts = defaultdict(lambda: defaultdict(lambda: {c: 0 for c in CAMPO_LIST}))
    monthly_by_gender_field_counts = defaultdict(lambda: defaultdict(lambda: {c: 0 for c in CAMPO_LIST}))
    by_age_and_gender_field_counts = defaultdict(lambda: defaultdict(lambda: {c: 0 for c in CAMPO_LIST}))
    monthly_by_age_and_gender_field_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {c: 0 for c in CAMPO_LIST})))
    # <<< FIM: NOVOS ACUMULADORES DE FIELD COUNT ADICIONADOS >>>


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

        # --- Obter dimensões ---
        idade_val = adicionais.get("Idade") or adicionais.get("IdadeDeclaradaOuInferidaDoAutor") or adicionais.get("idade")
        genero_val = adicionais.get("Genero") or adicionais.get("GeneroDeclarado") or adicionais.get("GeneroAutoDeclaradoOuInferidoDoAutor") or adicionais.get("genero")
        age_label = age_range_label(idade_val)
        gen_label = normalize_gender(genero_val)
        
        dt = adicionais.get("DataUltimoTweet") or adicionais.get("data_ultimo_tweet") or adicionais.get("DataUltimoPost")
        month = parse_iso_month(dt)

        # --- Combinar Scores DES ---
        combine(overall, des_score)
        combine(by_age[age_label], des_score)
        combine(by_gender[gen_label], des_score)
        combine(by_age_and_gender[age_label][gen_label], des_score)
        combine(monthly_general[month], des_score)
        combine(monthly_by_age[month][age_label], des_score)
        combine(monthly_by_gender[month][gen_label], des_score)
        combine(monthly_by_age_and_gender[month][age_label][gen_label], des_score) # <<< ADICIONADO NA SUA SOLICITAÇÃO ANTERIOR

        # --- Contagem de Campos (Field Counts) ---
        for campo in CAMPO_LIST:
            present = is_exposed(iniciais.get(campo, None))
            if present:
                # Contagens existentes
                field_counts_overall[campo] += 1
                monthly_field_counts[month][campo] += 1
                by_age_field_counts[age_label][campo] += 1
                by_gender_field_counts[gen_label][campo] += 1
                
                # <<< INÍCIO: NOVAS CONTAGENS ADICIONADAS >>>
                monthly_by_age_field_counts[month][age_label][campo] += 1
                monthly_by_gender_field_counts[month][gen_label][campo] += 1
                by_age_and_gender_field_counts[age_label][gen_label][campo] += 1
                monthly_by_age_and_gender_field_counts[month][age_label][gen_label][campo] += 1
                # <<< FIM: NOVAS CONTAGENS ADICIONADAS >>>

    by_age["Todos"] = overall
    agg_overall_final = finalize(overall)

    result = {
        # --- Resultados de Score DES ---
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
        "monthly_by_age_and_gender": { # <<< ADICIONADO NA SUA SOLICITAÇÃO ANTERIOR
            month: {
                age: {g: finalize(acc) for g, acc in gen_map.items()}
                for age, gen_map in age_map.items()
            }
            for month, age_map in monthly_by_age_and_gender.items()
        },
        
        # --- Resultados de Contagem de Campos (Field Counts) ---
        "field_counts_overall": field_counts_overall,
        "monthly_field_counts": {m: v for m, v in monthly_field_counts.items()},
        "by_age_field_counts": {age: v for age, v in by_age_field_counts.items()},
        "by_gender_field_counts": {g: v for g, v in by_gender_field_counts.items()},
        
        # <<< INÍCIO: NOVOS RESULTADOS DE FIELD COUNT ADICIONADOS >>>
        "monthly_by_age_field_counts": {m: v for m, v in monthly_by_age_field_counts.items()},
        "monthly_by_gender_field_counts": {m: v for m, v in monthly_by_gender_field_counts.items()},
        "by_age_and_gender_field_counts": {a: v for a, v in by_age_and_gender_field_counts.items()},
        "monthly_by_age_and_gender_field_counts": {m: v for m, v in monthly_by_age_and_gender_field_counts.items()},
        # <<< FIM: NOVOS RESULTADOS DE FIELD COUNT ADICIONADOS >>>
    }
    return result

def main():
    # global script_to_run_final # Esta variável não está definida
    script_to_run_final = None # <<< ADICIONADO para evitar NameError

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
                            "MencaoDoAutorAPosseDeCPF": "VERDADEIRO" # <<< DADO ADICIONADO PARA TESTE
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
                     "report": { # <<< DADO ADICIONADO PARA TESTE
                        "InformacoesIniciais": {
                            "MencaoDoAutorAPosseDeCPF": "VERDADEIRO"
                        },
                        "InformacoesAdicionais": {
                            "Idade": 22, # Mesma idade do primeiro
                            "Genero": "Masculino", # Mesmo genero do primeiro
                            "DataUltimoTweet": "2023-02-10T12:00:00Z" # Mes diferente
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
    
    print("[INFO] Resultados da Agregação:")
    print(json.dumps(agg, ensure_ascii=False, indent=2))
    
    if script_to_run_final: # <<< MODIFICADO para checar se a variável não é None
        try:
            with open("aggregate_reports_final.py", "w", encoding="utf-8") as f:
                f.write(script_to_run_final)
            print("[INFO] Script modificado salvo em 'aggregate_reports_final.py'.")
        except Exception as e_save_script:
            print(f"[WARN] Falha ao salvar script modificado: {e_save_script}")
    else:
        print("[INFO] 'script_to_run_final' não definido, pulando salvamento do script.") # <<< MODIFICADO
        
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