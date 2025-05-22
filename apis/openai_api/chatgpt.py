import os
from openai import OpenAI

def gerar_relatorio(api_key: str, tweets_json: str) -> str:

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

    client = OpenAI(api_key=api_key)    

    prompt = f'''
        Você é um analista de perfis de Twitter. Quero que você crie uma ficha que contenha
        todas as informações dos posts que eu te passar. Caso tenha alguma informação que você
        não consiga identificar com certeza, pode deixar o campo como inserto. Além disso,
        vou te passar uma lista de campos que você deve identificar, assim como os tweets em
        um formato json. Apenas o Json. Não deixe nada em negrito. Mande no formato JSON.

        Campos: {campos}
        Tweets (JSON): {tweets_json}
    '''
    response = client.responses.create(
        model="gpt-4o",
        input=[
            {"role": "system", "content": "Analista de perfis de Twitter"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.output_text