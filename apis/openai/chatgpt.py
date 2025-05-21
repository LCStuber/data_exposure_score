import os
import openai

def gerar_relatorio(api_key: str, tweets_json: str) -> str:
    """
    Envia o JSON de tweets ao GPT para gerar um relatório CSV completo,
    incluindo colunas de fonte primária e IDs de tweets.
    Retorna o CSV como string.
    """
    openai.api_key = api_key
    campos_csv = '''
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


    prompt = (
        f"Você é um analista de perfis de Twitter. Gere um relatório CSV completo "
        f"com o seguinte cabeçalho e preencha uma linha com dados extraídos dos tweets."
        f"As colunas de Fonte devem ser 'certo' quando baseadas em dados diretos "
        f"e 'inferido' quando extraídas por NLP. IDs separados por ';'.\n\n"
        f"Cabeçalho:\n{campos_csv}\n\n"
        f"Dados JSON de tweets:\n{tweets_json}"
    )
    response = openai.ChatCompletion.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": "Analista de perfis de Twitter"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()