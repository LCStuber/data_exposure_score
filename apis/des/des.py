# %%
import pandas as pd

# %%
df = pd.read_json('test.json').to_dict()
new_df = df
for k,v in df.items():
    new_df[k] = v[0]
new_df

# %%
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
    "StatusDeRelacionamentoDeclaradoOuSugeridoPeloAutor": categorias["Posicionamento e Características Pessoais"],
    "ProfissaoOcupacaoDeclaradaPeloAutor": categorias["Rotina/Hábitos"],
    "NivelEducacionalDeclaradoOuInferidoPeloAutor": categorias["Posicionamento e Características Pessoais"],
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


# %%
des = 0
for k, v in exposicao_autor.items():
    curr_value = 0
    if new_df[k] == "VERDADEIRO":
        curr_value = 1
    curr_value *= v["Impacto"] * v["Explorabilidade"]
    des += curr_value

des_max = sum(v["Impacto"] * v["Explorabilidade"] for v in exposicao_autor.values())

des_scaled = (des / des_max) * 1000

des_final = 1000 - des_scaled

des, des_final, des_max, des_scaled



