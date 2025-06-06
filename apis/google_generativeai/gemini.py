import os
import sys
import json
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv
from google import genai
from google.genai import types
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.genai import errors
import re

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

def gerar_relatorio_gemini(api_key: str, tweets: str) -> str:
    campos = '''NomeDeclaradoOuSugeridoPeloAutor,IdadeDeclaradaOuInferidaDoAutor,
GeneroAutoDeclaradoOuInferidoDoAutor,OrientacaoSexualDeclaradaOuSugeridaPeloAutor,StatusDeRelacionamentoDeclaradoOuSugeridoPeloAutor,
ProfissaoOcupacaoDeclaradaPeloAutor,NivelEducacionalDeclaradoOuInferidoPeloAutor,LocalizacaoPrincipalDeclaradaOuInferidaDoAutor,
CidadesComRelevanciaPessoalParaOAutor,CrencaReligiosaDeclaradaOuSugeridaPeloAutor,OpinioesPoliticasExpressasPeloAutor,
MencoesASaudeFisicaDoAutor,MencoesASaudeMentalDoAutor,MencoesAUsoDeSubstanciasPeloAutor,
MencoesAFamiliaresDoAutor,ExposicaoDeRelacionamentosPessoaisPeloAutor,
MencaoDoAutorAPosseDeCPF,MencaoDoAutorAPosseDeRG,MencaoDoAutorAPosseDePassaporte,
MencaoDoAutorAPosseDeTituloEleitor,MencaoDoAutorAoNomeDaMae,MencaoDoAutorAoNomeDoPai,
EtniaOuRacaAutoDeclaradaPeloAutor,MencaoDoAutorAEnderecoResidencial,
MencaoDoAutorAContatoPessoal_TelefoneEmail,MencaoDoAutorADadosBancarios,MencaoDoAutorACartaoDeEmbarque,
IndicadoresDeRendaPropriaMencionadosPeloAutor,MencoesAPatrimonioPessoalDoAutor,
LocalDeTrabalhoOuEstudoDeclaradoPeloAutor,MencaoDoAutorARecebimentoDeBeneficioSocial,
MencoesAoProprioHistoricoFinanceiroPeloAutor,MencoesDoAutorAFilhosOuDependentes,
MencoesDoAutorAProprioHistoricoCriminal,MencaoDoAutorAPosseDeChavePix'''

    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        return f'{{"erro": "Falha na configuração da API Gemini: {str(e)}", "detalhes": "Verifique a API Key."}}'


    prompt_completo = f"""Você é um analista de perfis de Twitter focado na extração precisa de informações sobre o AUTOR dos tweets. Sua tarefa é criar uma ficha JSON do usuário, analisando seus tweets e preenchendo os campos fornecidos.

Diretrizes Rígidas:

1.  Saída: APENAS o JSON final. Sem nenhum texto adicional.
2.  Foco no Autor: Toda informação DEVE ser sobre o autor ou declarada por ele.
3.  Lógica de Preenchimento (VERDADEIRO/OUTROS/FALSO):
    * Para CADA campo, o valor deve ser:
        * Uma lista contendo a string "VERDADEIRO" se o autor fizer uma menção sobre si mesmo relacionada ao campo.
        * Uma lista contendo a string "OUTROS" se o autor fizer uma menção sobre um conhecido/terceiro relacionada ao campo.
        * Se houver menções sobre o autor E sobre outros para o mesmo campo, a lista deve conter ambas as strings: ["VERDADEIRO", "OUTROS"].
        * A string "FALSO" se não houver nenhuma menção relevante ao campo nos tweets, ou se a informação for inconclusiva.
    * Cada string ("VERDADEIRO", "OUTROS") deve aparecer no máximo uma vez na lista para cada campo.
    * Exemplo de campo com dados sobre o autor: "IdadeDeclaradaOuInferidaDoAutor": ["VERDADEIRO"]
    * Exemplo de campo com dados sobre outros: "IdadeDeclaradaOuInferidaDoAutor": ["OUTROS"]
    * Exemplo de campo com dados sobre ambos: "IdadeDeclaradaOuInferidaDoAutor": ["VERDADEIRO", "OUTROS"]
    * Exemplo de campo sem dados ou inconclusivo: "MencaoDoAutorAPosseDeCPF": ["FALSO"]

Entradas:
campos: {campos}
tweets: {tweets}""".strip()


    config = types.GenerateContentConfig(
        # 1) Direciona o modelo a obedecer o formato solicitado
        system_instruction=types.Content(
            parts=[types.Part(
                text=(
                    "Responda exclusivamente com JSON válido, sem texto extra. "
                    "Use (VERDADEIRO/OUTROS/FALSO) como nas diretrizes."
                )
            )]
        ),

        # 3) Mantém apenas uma variação de saída
        candidate_count=1,

        # 7) Formato da resposta
        response_mime_type="application/json",

        # 8) (Opcional, mas útil) Esquema reforça a estrutura esperada
        response_schema = {
            "type": "object",
            "properties": {
                campo: {"type": "string"} for campo in [
                    "NomeDeclaradoOuSugeridoPeloAutor","IdadeDeclaradaOuInferidaDoAutor","GeneroAutoDeclaradoOuInferidoDoAutor","OrientacaoSexualDeclaradaOuSugeridaPeloAutor","StatusDeRelacionamentoDeclaradoOuSugeridoPeloAutor","ProfissaoOcupacaoDeclaradaPeloAutor","NivelEducacionalDeclaradoOuInferidoPeloAutor","LocalizacaoPrincipalDeclaradaOuInferidaDoAutor","CidadesComRelevanciaPessoalParaOAutor","CrencaReligiosaDeclaradaOuSugeridaPeloAutor","OpinioesPoliticasExpressasPeloAutor","MencoesASaudeFisicaDoAutor","MencoesASaudeMentalDoAutor","MencoesAUsoDeSubstanciasPeloAutor","MencoesAFamiliaresDoAutor","ExposicaoDeRelacionamentosPessoaisPeloAutor","MencaoDoAutorAPosseDeCPF","MencaoDoAutorAPosseDeRG","MencaoDoAutorAPosseDePassaporte","MencaoDoAutorAPosseDeTituloEleitor","MencaoDoAutorAoNomeDaMae","MencaoDoAutorAoNomeDoPai","EtniaOuRacaAutoDeclaradaPeloAutor","MencaoDoAutorAEnderecoResidencial","MencaoDoAutorAContatoPessoal_TelefoneEmail","MencaoDoAutorADadosBancarios","MencaoDoAutorACartaoDeEmbarque","IndicadoresDeRendaPropriaMencionadosPeloAutor","MencoesAPatrimonioPessoalDoAutor","LocalDeTrabalhoOuEstudoDeclaradoPeloAutor","MencaoDoAutorARecebimentoDeBeneficioSocial","MencoesAoProprioHistoricoFinanceiroPeloAutor","MencoesDoAutorAFilhosOuDependentes","MencoesDoAutorAProprioHistoricoCriminal","MencaoDoAutorAPosseDeChavePix"
                ]
            }
        },


        # 9) Mantém seu budget de “thinking” zerado
        thinking_config=types.ThinkingConfig(thinking_budget=0)
    )

    try:
        resp: types.GenerateContentResponse = client.models.generate_content(
            model="gemini-2.5-flash-preview-05-20",
            contents=prompt_completo,
            config=config
        )
    except errors.APIError as api_err:  # 4xx / 5xx
        return {
            "erro": "APIError",
            "detalhes": f"{api_err.code} {api_err.message}",
        }

    # Verifica bloqueio de conteúdo
    fb = getattr(resp, "prompt_feedback", None)
    if fb and fb.block_reason:
        return {
            "erro": "Conteúdo bloqueado",
            "motivo": fb.block_reason.name,  # SAFETY, PROHIBITED_CONTENT, OTHER…
        }

    return resp.text

USER       = os.getenv("MONGO_USER")
PASS       = os.getenv("MONGO_PASS")
HOST       = os.getenv("MONGO_HOST")
PORT       = os.getenv("MONGO_PORT")
AUTH_DB    = os.getenv("MONGO_AUTH_DB")
DB_NAME    = os.getenv("MONGO_DB")
COL_DATA   = os.getenv("MONGO_COLLECTION_DATA")
COL_REPORT = os.getenv("MONGO_COLLECTION_REPORTS")
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")


if not all([USER, PASS, HOST, PORT, AUTH_DB, DB_NAME, COL_DATA, COL_REPORT, GOOGLE_KEY]):
    raise RuntimeError("Por favor, verifique se todas as variáveis de ambiente Mongo e GOOGLE_API_KEY estão configuradas no .env")

uri = f"mongodb://{USER}:{PASS}@{HOST}:{PORT}/?authSource={AUTH_DB}"
clientDB = MongoClient(uri)
db       = clientDB[DB_NAME]
data_coll   = db[COL_DATA]
reports_coll = db[COL_REPORT]


def processar_doc(doc):
    """
    Processa um único documento:
    - Filtra posts em 'pt'
    - Chama Gemini
    - Insere em reports_coll
    - Atualiza data_coll com report_id
    """
    source_id = doc["_id"]
    posts = doc.get("posts", [])
    tweets_pt = [post for post in posts if post.get("lang") == "pt"]
    if not tweets_pt:
        print(f"[SKIP] Documento {source_id} não tem posts em 'pt'.")
        return

    tweets_json = json.dumps(tweets_pt, ensure_ascii=False)
    try:
        relatório = gerar_relatorio_gemini(GOOGLE_KEY, tweets_json)
    except Exception as e:
        print(f"[ERRO] Ao gerar relatório para {source_id}: {e}")
        sys.exit(1)

    try:
        resultado = reports_coll.insert_one({
            "source_id": source_id,
            "report": relatório,
            "analyzed_at": datetime.now(timezone.utc)
        })
        inserted_id = resultado.inserted_id
        print(f"[SALVO] Relatório para {source_id} inserido em `{COL_REPORT}` como _id={inserted_id}")
    except Exception as e:
        print(f"[ERRO] Ao salvar relatório de {source_id} em `{COL_REPORT}`: {e}")
        print(relatório)
        print(source_id)
        sys.exit(1)

    try:
        data_coll.update_one(
            {"_id": source_id},
            {"$set": {"report_id": inserted_id}}
        )
        print(f"[ATUALIZADO] Documento {source_id} em `{COL_DATA}` marcado com report_id={inserted_id}")
    except Exception as e:
        print(f"[ERRO] Ao adicionar report_id em `{COL_DATA}` para {source_id}: {e}")
        print(relatório)
        print(source_id)
        print(inserted_id)
        sys.exit(1)

def processar_em_batches(batch):
    """
    Processa uma lista de documentos em paralelo usando threads.
    Se qualquer thread lançar exceção, o programa será encerrado.
    """
    max_workers = 1
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(processar_doc, doc) for doc in batch]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"[ERRO NA THREAD] {e}")
                sys.exit(1)

def processar_bsky_docs():
    """
    Itera sobre todos os documentos de data_coll com significant=true e sem 'report_id',
    em lotes de 1000. Após cada lote, aguarda ENTER para continuar ou 'q' para sair.
    Se qualquer erro ocorrer, o script será interrompido imediatamente.
    """
    filtro = {"significant": True, "report_id": {"$exists": False}}

    pipeline = [
        {"$match": filtro},
        {"$project": {
            "posts": {
                "$slice": [
                    {
                        "$sortArray": {
                            "input": "$posts",
                            "sortBy": {"created_at": -1}
                        }
                    },
                    400
                ]
            }
        }}
    ]

    cursor = data_coll.aggregate(pipeline)
    batch_size = 24
    batch = []
    total = data_coll.count_documents(filtro)
    print(f"[INFO] Encontrados {total} documentos com significant=true e sem report_id em `{COL_DATA}`")

    processed = 0
    for doc in cursor:
        batch.append(doc)
        if len(batch) >= batch_size:
            print(f"\n--- Processando lote de {len(batch)} documentos ({processed+1} a {processed+len(batch)} de ~{total}) ---")
            processar_em_batches(batch)
            processed += len(batch)
            batch.clear()

            escolha = input("Pressione ENTER para processar o próximo lote ou digite 'q' + ENTER para sair: ").strip().lower()
            if escolha == 'q':
                print("[INFO] Execução interrompida a pedido do usuário.")
                return
            print()

    # Processa o que sobrou, se houver
    if batch:
        print(f"\n--- Processando lote final de {len(batch)} documentos ({processed+1} a {processed+len(batch)} de ~{total}) ---")
        processar_em_batches(batch)
        print()

    print("[INFO] Todos os documentos foram processados ou o usuário interrompeu.")

if __name__ == "__main__":
    processar_bsky_docs()