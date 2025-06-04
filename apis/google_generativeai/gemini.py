from google import genai
from google.genai import types
import json
import os
from dotenv import load_dotenv

load_dotenv()

def gerar_relatorio_gemini(api_key: str, tweets: str) -> str:
    campos = '''Usuario,NomeProvavel,IdadeEstimada,
GeneroEstimado,OrientacaoSexualSugestiva,RelacaoAfetivaSugerida,
ProfissaoOcupacao,EscolaridadeIndicada,LocalizacaoProvavel,
CidadesMencionadas,ReligiaoSugerida,PosicionamentoPolitico,
SaudeFisicaCitacoes,SaudeMentalCitacoes,UsoDeSubstancias,
TopicosRelevantes,HobbiesEInteresses,ReferenciasAFamilia,
ExposicaoDeRelacionamentos, PossuiInformacaoCPF,PossuiInformacaoRG,PossuiPassaporte,
PossuiTituloEleitor,NomeDaMaePresente,NomeDoPaiPresente,
NacionalidadeMencionada,EtniaOuRacaMencionada,EnderecoMencionado,
TelefoneOuEmailMencionado,PossuiInformacaoBancaria, PossuiCartaoDeEmbarque,
IndicacaoDeRenda,ClasseSocialInferida,PossuiPatrimonioMencionado,
EmpregoOuEmpresaMencionada,BeneficioSocialMencionado,
HistoricoFinanceiroMencionado,ScoreCreditoInferido,
FilhosOuDependentesMencionados,HistoricoCriminalMencionado, PossuiPixMencionado'''

    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        return f'{{"erro": "Falha na configuração da API Gemini: {str(e)}", "detalhes": "Verifique a API Key."}}'


    prompt_completo = f'''Você é um analista de perfis de Twitter. Quero que você crie uma ficha que contenha
todas as informações dos posts que eu te passar. Caso tenha alguma informação que você
não consiga identificar com certeza, pode deixar o campo como INCERTO. 
Deixe como INCERTO caso não encontrar alguma informação. Além disso,
vou te passar uma lista de campos que você deve identificar, assim como os tweets em
um formato json. Apenas o Json. Não deixe nada em negrito. Mande no formato JSON.
Além disso, as menções devem se referir ao USUÁRIO que está fazendo as publicações,
não a eventos ou pessoas de maneira geral. Caso não tenha uma referência direta ao usuário
você deve colocar o valor do campo como INCERTO.
Campos: {campos}
Tweets: {tweets}'''


    try:
        response: types.GenerateContentResponse = client.models.generate_content(
            model="gemini-2.5-flash-preview-04-17",
            contents=prompt_completo,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                thinking_budget=0
                ),
                response_mime_type="application/json"
            )
        )
        return response.text
    except genai.types.BlockedPromptException as e:
        return f'{{"erro": "Prompt bloqueado", "detalhes": "{str(e)}"}}'
    except genai.types.StopCandidateException as e:
        return f'{{"erro": "Geração interrompida", "detalhes": "{str(e)}"}}'
    except Exception as e:
        error_details = str(e)
        if hasattr(e, 'message'):
            error_details = e.message
        return f'{{"erro": "Falha ao gerar relatório com Gemini", "detalhes": "{error_details}"}}'


if __name__ == "__main__":
    api_key = os.getenv("GOOGLE_API_KEY")
    with open("C:\\github\\data_exposure_score\\apis\\google_generativeai\\tweet.json", "r", encoding="utf-8") as file:
        tweets_data = file.read()

    resultado = gerar_relatorio_gemini(api_key, tweets=tweets_data)
    print(resultado)