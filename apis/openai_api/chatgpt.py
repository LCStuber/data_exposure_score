import os
import sys
import json
import time
import tempfile
from datetime import datetime, timezone
from typing import List, Dict

from openai import OpenAI
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


# ENVIRONMENT VARIABLES & GLOBALS

USER = os.getenv("MONGO_USER")
PASS = os.getenv("MONGO_PASS")
HOST = os.getenv("MONGO_HOST")
PORT = os.getenv("MONGO_PORT")
AUTH_DB = os.getenv("MONGO_AUTH_DB")
DB_NAME = os.getenv("MONGO_DB")
COL_DATA = os.getenv("MONGO_COLLECTION_DATA")
COL_REPORT = os.getenv("MONGO_COLLECTION_REPORTS")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

if not all([USER, PASS, HOST, PORT, AUTH_DB, DB_NAME, COL_DATA, COL_REPORT, OPENAI_KEY]):
    raise RuntimeError("Verifique se todas as variáveis de ambiente Mongo e OPENAI_API_KEY estão configuradas no .env")

# MongoDB client/collections
uri = f"mongodb://{USER}:{PASS}@{HOST}:{PORT}/?authSource={AUTH_DB}"
clientDB = MongoClient(uri)
db = clientDB[DB_NAME]
data_coll = db[COL_DATA]
reports_coll = db[COL_REPORT]


openai_client = OpenAI(api_key=OPENAI_KEY)


DEFAULT_BATCH_SIZE = int(os.getenv("BATCH_SIZE", 500))  # linhas por arquivo .jsonl para Batch API
MODEL_NAME = "gpt-4o-mini"
CAMPO_LIST = (
    "NomeDeclaradoOuSugeridoPeloAutor,"
    "IdadeDeclaradaOuInferidaDoAutor,"
    "GeneroAutoDeclaradoOuInferidoDoAutor,"
    "OrientacaoSexualDeclaradaOuSugeridaPeloAutor,"
    "StatusDeRelacionamentoDeclaradoOuSugeridoPeloAutor,"
    "ProfissaoOcupacaoDeclaradaPeloAutor,"
    "NivelEducacionalDeclaradoOuInferidoPeloAutor,"
    "LocalizacaoPrincipalDeclaradaOuInferidaDoAutor,"
    "CidadesComRelevanciaPessoalParaOAutor,"
    "CrencaReligiosaDeclaradaOuSugeridaPeloAutor,"
    "OpinioesPoliticasExpressasPeloAutor,"
    "ExposicaoDeRelacionamentosPessoaisPeloAutor,"
    "MencaoDoAutorAPosseDeCPF,"
    "MencaoDoAutorAPosseDeRG,"
    "MencaoDoAutorAPosseDePassaporte,"
    "MencaoDoAutorAPosseDeTituloEleitor,"
    "EtniaOuRacaAutoDeclaradaPeloAutor,"
    "MencaoDoAutorAEnderecoResidencial,"
    "MencaoDoAutorAContatoPessoal_TelefoneEmail,"
    "MencaoDoAutorADadosBancarios,"
    "MencaoDoAutorACartaoDeEmbarque,"
    "IndicadoresDeRendaPropriaMencionadosPeloAutor,"
    "MencoesAPatrimonioPessoalDoAutor,"
    "LocalDeTrabalhoOuEstudoDeclaradoPeloAutor,"
    "MencaoDoAutorARecebimentoDeBeneficioSocial,"
    "MencoesAoProprioHistoricoFinanceiroPeloAutor,"
    "MencoesDoAutorAProprioHistoricoCriminal,"
    "MencaoDoAutorAPosseDeChavePix"
)

def build_prompt(tweets_json: str) -> str:
    return (
        "Você é um analista especializado em perfis do Twitter. "
        "Analise os tweets fornecidos e produza um JSON contendo apenas informações sobre o autor. "
        "Cada campo deve indicar se o autor mencionou ou sugeriu algo relacionado a ele mesmo. "
        "Use apenas dois valores possíveis: VERDADEIRO ou FALSO. "
        "Não inclua texto explicativo, apenas o JSON final. "
        "O JSON deve conter duas seções: "
        "InformacoesIniciais (com todos os campos listados) e "
        "InformacoesAdicionais (contendo Idade, Genero e DataUltimoTweet, quando inferíveis). "
        f"Campos: {CAMPO_LIST}. "
        f"Tweets: {tweets_json}"
    )



def doc_to_batch_line(doc: Dict) -> Dict:
    """Transforma um documento Mongo em uma linha JSONL para o Batch API"""
    source_id = str(doc["_id"])
    tweets_pt = [p for p in doc.get("posts", []) if p.get("lang") == "pt"]
    tweets_json = json.dumps(tweets_pt, ensure_ascii=False)

    prompt = build_prompt(tweets_json)

    body = {
        "model": MODEL_NAME,
        "input": [
            {"role": "system", "content": "Analista de perfis de Twitter"},
            {"role": "user", "content": prompt}
        ],
        "store": False,
    }

    return {
        "custom_id": source_id,
        "method": "POST",
        "url": "/v1/responses",
        "body": body,
    }


def write_jsonl(lines: List[Dict]) -> str:
    """Escreve as linhas da batch em um arquivo temporário .jsonl e retorna o caminho"""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl", mode="w", encoding="utf-8")
    for line in lines:
        tmp.write(json.dumps(line, ensure_ascii=False) + "\n")
    tmp.close()
    return tmp.name


def wait_batch(batch_id: str, poll_seconds: int = 60):
    """Aguarda até que o batch mude para estado 'completed' ou 'failed'/'cancelled'"""
    print(f"[INFO] Aguardando conclusão do batch {batch_id}...")
    while True:
        batch = openai_client.batches.retrieve(batch_id)
        status = batch.status
        if status in {"completed", "failed", "cancelled", "expired"}:
            return batch
        print(f"    status: {status} | concluído: {batch.request_counts.completed} / {batch.request_counts.total}")
        time.sleep(poll_seconds)


def processar_resultados(batch):
    """Baixa o arquivo de saída do batch e processa cada linha para Mongo"""
    output_file_id = batch.output_file_id
    error_file_id = batch.error_file_id

    if not output_file_id:
        print(f"[ERRO] Batch {batch.id} não possui output_file_id. Status: {batch.status}")
        return

    file_resp = openai_client.files.content(output_file_id)
    # O método .text carrega tudo na memória; se o arquivo for grande considere stream
    conteudo = file_resp.text

    for line in conteudo.splitlines():
        registro = json.loads(line)
        source_id = registro["custom_id"]
        resposta_body = registro["response"]["body"]
        relatorio = resposta_body["choices"][0]["message"]["content"].strip()

        # Insere reporte e atualiza source
        try:
            resultado = reports_coll.insert_one({
                "source_id": source_id,
                "report": relatorio,
                "analyzed_at": datetime.now(timezone.utc)
            })
            inserted_id = resultado.inserted_id
            data_coll.update_one({"_id": data_coll.codec_options.document_class(source_id)}, {"$set": {"report_id": inserted_id}})
            print(f"[SALVO] Relatório para {source_id} (_id={inserted_id})")
        except Exception as e:
            print(f"[ERRO] Falha ao salvar relatório/atualizar doc {source_id}: {e}")

    if error_file_id:
        err_resp = openai_client.files.content(error_file_id)
        print("[AVISO] Existem erros no batch. Confira o arquivo de erro:")
        print(err_resp.text[:1000])  # imprime os primeiros 1000 chars


def processar_bsky_docs():
    filtro = {"significant": True, "report_id": {"$exists": False}}

    cursor = data_coll.find(filtro, projection={"posts": 1})
    total = data_coll.count_documents(filtro)
    print(f"[INFO] Encontrados {total} documentos pendentes em `{COL_DATA}`")

    batch_lines: List[Dict] = []
    count = 0

    for doc in cursor:
        # Apenas documentos com tweets em 'pt'
        if not any(p.get("lang") == "pt" for p in doc.get("posts", [])):
            continue
        batch_lines.append(doc_to_batch_line(doc))
        count += 1

        # Quando atingirmos DEFAULT_BATCH_SIZE linhas ou for o último doc, executamos um batch
        if count % DEFAULT_BATCH_SIZE == 0:
            execute_batch(batch_lines)
            batch_lines.clear()

    # Processa o restante
    if batch_lines:
        execute_batch(batch_lines)


def execute_batch(lines: List[Dict]):
    """Executa um batch dado uma lista de linhas JSONL"""
    print(f"[INFO] Criando batch com {len(lines)} requisições...")
    jsonl_path = write_jsonl(lines)

    # 1) Upload do arquivo
    file_obj = openai_client.files.create(file=open(jsonl_path, "rb"), purpose="batch")
    print(f"    Arquivo enviado: {file_obj.id}")

    # 2) Criação do batch
    batch_obj = openai_client.batches.create(
        input_file_id=file_obj.id,
        endpoint="/v1/responses",
        completion_window="24h",
        metadata={"origin": "twitter-bsky-script"}
    )
    print(f"    Batch iniciado: {batch_obj.id} | status: {batch_obj.status}")

    # 3) Aguardar conclusão
    batch_final = wait_batch(batch_obj.id, poll_seconds=60)

    # 4) Processar resultados e atualizar Mongo
    if batch_final.status == "completed":
        processar_resultados(batch_final)
    else:
        print(f"[ERRO] Batch {batch_final.id} terminou com status {batch_final.status}")


if __name__ == "__main__":
    try:
        processar_bsky_docs()
    except KeyboardInterrupt:
        print("[INFO] Execução interrompida pelo usuário.")