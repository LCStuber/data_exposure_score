import google.generativeai as genai
import json

def gerar_relatorio_gemini(api_key: str, tweets_json: str) -> str:
    campos = '''
            Usuario,NomeProvavel,IdadeEstimada,
            GeneroEstimado,OrientacaoSexualSugestiva,RelacaoAfetivaSugerida,
            ProfissaoOcupacao,EscolaridadeIndicada,LocalizacaoProvavel,
            CidadesMencionadas,ReligiaoSugerida,PosicionamentoPolitico,
            SaudeFisicaCitacoes,SaudeMentalCitacoes,UsoDeSubstancias,
            TopicosRelevantes,HobbiesEInteresses,ReferenciasAFamilia,
            ExposicaoDeRelacionamentos,PadraoDePostagem,HorariosDeAtividade,
            FrequenciaDeMidia,TipoDeMidiaCompartilhada,TipoDeLinguagem,
            Fonte_Das_Informacoes,IDs_Posts_Relevantes,
            PossuiInformacaoCPF,PossuiInformacaoRG,PossuiPassaporte,
            PossuiTituloEleitor,NomeDaMaePresente,NomeDoPaiPresente,
            NacionalidadeMencionada,EtniaOuRacaMencionada,EnderecoMencionado,
            TelefoneOuEmailMencionado,PossuiInformacaoBancaria, PossuiCartaoDeEmbarque,
            IndicacaoDeRenda,ClasseSocialInferida,PossuiPatrimonioMencionado,
            EmpregoOuEmpresaMencionada,BeneficioSocialMencionado,
            HistoricoFinanceiroMencionado,ScoreCreditoInferido,
            FilhosOuDependentesMencionados,RelatoDeViolenciaOuAbuso,
            HistoricoCriminalMencionado
        '''

    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        return f'{{"erro": "Falha na configuração da API Gemini: {str(e)}", "detalhes": "Verifique a API Key."}}'

    model = genai.GenerativeModel(
        'gemini-1.5-flash-8b',
        system_instruction="Você é um analista de perfis de Twitter altamente preciso. Sua tarefa é extrair informações de tweets e retorná-las estritamente em formato JSON."
    )

    prompt_completo = f'''
Analisar os seguintes tweets e gerar um relatório em formato JSON.
O relatório deve conter os campos listados abaixo.
Se uma informação para um campo específico não puder ser encontrada ou inferida com segurança a partir dos tweets fornecidos,
use `null` como valor para esse campo no JSON. Para campos que esperam uma lista (ex: CidadesMencionadas),
use uma lista vazia `[]` se nenhuma informação for encontrada.
Não inclua nenhuma formatação em negrito ou qualquer texto explicativo fora do próprio JSON.
A resposta DEVE ser apenas o objeto JSON.

Campos a serem identificados (estas serão as chaves no objeto JSON):
{campos.strip()}

Tweets fornecidos (em formato JSON):
{tweets_json}

Por favor, gere um único objeto JSON contendo todos os campos acima preenchidos com base na análise dos tweets.
'''

    generation_config = genai.types.GenerationConfig(
        response_mime_type="application/json"
    )

    try:
        response = model.generate_content(
            prompt_completo,
            generation_config=generation_config
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