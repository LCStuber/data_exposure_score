from textblob import TextBlob
import pymongo as pm
import os
import re
import time
from multiprocessing import Pool, cpu_count
from dotenv import load_dotenv

load_dotenv()

USER       = os.getenv("MONGO_USER")
PASS       = os.getenv("MONGO_PASS")
HOST       = os.getenv("MONGO_HOST")
PORT       = os.getenv("MONGO_PORT")
AUTH_DB    = os.getenv("MONGO_AUTH_DB")
DB_NAME    = os.getenv("MONGO_DB")


uri = f"mongodb://{USER}:{PASS}@{HOST}:{PORT}/?authSource={AUTH_DB}"



keywords_por_tema = {
    "NomeProvavel": [
        "meu nome é",
        "me chamo",
        "chamo-me",
        "sou o",
        "sou a",
        "nome:",
        "eu sou",
        "eu me chamo"
    ],
    "IdadeEstimada": [
        "anos",
        "idade",
        "tenho",
        "nascido em",
        "faço",
        "completando",
        "aniversário",
        "ano(s) de idade",
        "faço aniversário"
    ],
    "GeneroEstimado": [
        "sou homem",
        "sou mulher",
        "ele",
        "ela",
        "cara",
        "mina",
        "garoto",
        "garota",
        "trans",
        "não-binár"
    ],
    "OrientacaoSexualSugestiva": [
        "sou gay",
        "sou lésbica",
        "sou bissexual",
        "#gay",
        "#lgbt",
        "#lgbtq",
        "homossexual",
        "homo",
        "lésbica",
        "bissexual",
        "pansexual",
        "asexual"
    ],
    "RelacaoAfetivaSugerida": [
        "namoro",
        "casado",
        "casada",
        "solteiro",
        "solteira",
        "viúvo",
        "viúva",
        "noivo",
        "noiva",
        "fica com",
        "ficando com",
        "amor",
        "namorada",
        "namorado",
        "esposa",
        "marido",
        "relacionamento"
    ],
    "ProfissaoOcupacao": [
        "sou estudante",
        "estudante de",
        "trabalho como",
        "empregado",
        "empregada",
        "funcionário",
        "funcionária",
        "engenheiro",
        "engenheira",
        "programador",
        "programadora",
        "desenvolvedor",
        "desenvolvedora",
        "médico",
        "médica",
        "professor",
        "professora",
        "advogado",
        "advogada",
        "arquiteto",
        "arquiteta",
        "analista",
        "técnico",
        "técnica",
        "autônomo",
        "autônoma",
        "freelancer",
        "freelance"
    ],
    "EscolaridadeIndicada": [
        "faculdade",
        "universidade",
        "graduação",
        "bacharelado",
        "licenciatura",
        "mestrado",
        "doutorado",
        "ensino médio",
        "ensino técnico",
        "colegial",
        "técnico em",
        "estudando em",
        "cursando",
        "formado em",
        "formada em",
        "EAD",
        "curso superior"
    ],
    "LocalizacaoProvavel": [
        "moro em",
        "resido em",
        "vivo em",
        "na cidade de",
        "no bairro",
        "no estado de",
        "em São Paulo",
        "no Rio de Janeiro",
        "em Belo Horizonte",
        "em Porto Alegre",
        "em Salvador",
        "no Brasil",
        "em Brasília"
    ],
    "CidadesMencionadas": [
        "São Paulo",
        "Rio de Janeiro",
        "Belo Horizonte",
        "Porto Alegre",
        "Salvador",
        "Brasília",
        "Curitiba",
        "Fortaleza",
        "Recife",
        "Manaus",
        "Buenos Aires",
        "Lisboa",
        "Madri",
        "Londres",
        "Nova York",
        "Paris",
        "Tóquio"
    ],
    "ReligiaoSugerida": [
        "sou católico",
        "sou evangélico",
        "sou protestante",
        "sou budista",
        "sou judeu",
        "igreja",
        "oração",
        "Deus",
        "fé",
        "ré",
        "rezando",
        "mesquita",
        "sinagoga",
        "Deus abençoe",
        "rabino",
        "padre",
        "bispo"
    ],
    "PosicionamentoPolitico": [
        "bolsonarista",
        "petista",
        "de direita",
        "de esquerda",
        "centro-direita",
        "centro-esquerda",
        "PT",
        "PSL",
        "PSDB",
        "MDB",
        "PSOL",
        "candidato",
        "eleições",
        "voto",
        "ideologia",
        "Greve Geral",
        "golpista",
        "miliciano",
        "antifascista",
        "fascista"
    ],
    "SaudeFisicaCitacoes": [
        "academia",
        "corrida",
        "treino",
        "malhando",
        "saúde",
        "doença",
        "gripado",
        "resfriado",
        "gripe",
        "COVID-19",
        "covid",
        "tive pneumonia",
        "alérgico",
        "hipertensão",
        "diabetes",
        "consulta médica",
        "hospital",
        "médico",
        "vacina",
        "checando pressão"
    ],
    "SaudeMentalCitacoes": [
        "ansiedade",
        "depressão",
        "estou ansioso",
        "estou deprimido",
        "transtorno bipolar",
        "psicólogo",
        "terapia",
        "psicose",
        "stress",
        "trauma",
        "autismo",
        "TDAH",
        "boa noite,  insônia",
        "descansar",
        "medicação",
        "psiquiatra",
        "crise",
        "solidão"
    ],
    "UsoDeSubstancias": [
        "bebo",
        "álcool",
        "cerveja",
        "vodka",
        "whisky",
        "dorgas",
        "maconha",
        "cigarro",
        "fumo",
        "trago",
        "cheiro",
        "cheirando",
        "safada",
        "drogado",
        "ué, chapado",
        "bebida",
        "desintoxicação",
        "reabilitação"
    ],
    "TopicosRelevantes": [
        "filme",
        "série",
        "música",
        "tecnologia",
        "ciência",
        "esporte",
        "política",
        "economia",
        "games",
        "livros",
        "cinema",
        "teatro",
        "arte",
        "história",
        "fotografia",
        "viajar",
        "aventura",
        "investimentos",
        "criptomoedas",
        "educação"
    ],
    "HobbiesEInteresses": [
        "jogar",
        "jogando",
        "jogos",
        "videogame",
        "viajar",
        "fotografia",
        "cozinhar",
        "receita",
        "treinar",
        "corrida",
        "dançar",
        "pintura",
        "desenho",
        "tocar violão",
        "guitarra",
        "piano",
        "futebol",
        "tênis",
        "natação",
        "pescar",
        "leitura",
        "música",
        "cantando",
        "assisto",
        "DIY",
        "faço artesanato"
    ],
    "ReferenciasAFamilia": [
        "mãe",
        "mamãe",
        "pai",
        "papai",
        "filho",
        "filha",
        "irmão",
        "irmã",
        "tio",
        "tia",
        "avô",
        "avó",
        "primo",
        "príma",
        "sogra",
        "sogro",
        "cunhada",
        "cunhado",
        "tiazinha",
        "tiozão"
    ],
    "ExposicaoDeRelacionamentos": [
        "namorada",
        "namorado",
        "casada",
        "casado",
        "solteira",
        "solteiro",
        "noiva",
        "noivo",
        "casamento",
        "divórcio",
        "separado",
        "viúva",
        "viúvo",
        "ficando com",
        "ficando",
        "relacionad",
        "marido",
        "esposa"
    ],
    "PadraoDePostagem": [
        "RT",
        "retweet",
        "reply",
        "resposta",
        "respondi",
        "thread",
        "citação",
        "quote",
        "favorito",
        "curtido",
        "print",
        "screenshots"
    ],
    "HorariosDeAtividade": [
        "cedo",
        "de manhã",
        "tarde",
        "noite",
        "madrugada",
        "às 8h",
        "às 10h",
        "às 14h",
        "às 18h",
        "às 22h",
        "hoje de manhã",
        "amanhã à tarde",
        "ontem à noite"
    ],
    "FrequenciaDeMidia": [
        "vídeo",
        "foto",
        "imagem",
        "link",
        "GIF",
        "anexo",
        "retweet com mídia",
        "tweet multimídia",
        "vídeo postado",
        "foto postada",
        "stories",
        "publicado com link"
    ],
    "TipoDeMidiaCompartilhada": [
        "imagens",
        "fotos",
        "vídeos",
        "links",
        "GIFs",
        "enquetes",
        "tags",
        "memes"
    ],
    "TipoDeLinguagem": [
        "vc",
        "você",
        "tá",
        "ta",
        "to",
        "tô",
        "ñ",
        "não",
        "rs",
        "kkk",
        "hahaha",
        "aff",
        "mano",
        "véi",
        "bro",
        "bora",
        "crush",
        "lol"
    ],
    "Fonte_Das_Informacoes": [
        # Não se aplica diretamente a texto de posts (campo meta). 
    ],
    "IDs_Posts_Relevantes": [
        # IDs extraídos do JSON de cada tweet (não keywords de texto).
    ],
    "PossuiInformacaoCPF": [
        "CPF",
        "cpf:",
        "cpf é",
        "cadastro de pessoa física",
        "insira seu cpf"
    ],
    "PossuiInformacaoRG": [
        "RG",
        "rg:",
        "registro geral",
        "carteira de identidade"
    ],
    "PossuiPassaporte": [
        "passaporte",
        "passport",
        "Passaporte nº",
        "Passaporte n.º",
        "Número do passaporte",
        "Viaje com passaporte",
        "documento de viagem"
    ],
    "PossuiTituloEleitor": [
        "título de eleitor",
        "titulo eleitoral",
        "título eleitoral",
        "nº do título",
        "zona eleitoral",
        "secção eleitoral"
    ],
    "NomeDaMaePresente": [
        "minha mãe",
        "meu pai",
        "mamãe",
        "paizão",
        "mãe",
        "pai",
        "chamo minha mãe"
    ],
    "NomeDoPaiPresente": [
        "meu pai",
        "papai",
        "pai",
        "filho de",
        "filha de"
    ],
    "NacionalidadeMencionada": [
        "brasileiro",
        "brasileira",
        "português",
        "portuguesa",
        "argentino",
        "argentina",
        "cidadão",
        "cidadã",
        "natural de",
        "nacionalidade"
    ],
    "EtniaOuRacaMencionada": [
        "negro",
        "negra",
        "branco",
        "branca",
        "pardo",
        "parda",
        "indígena",
        "afro",
        "afrodescendente",
        "raça"
    ],
    "EnderecoMencionado": [
        "rua",
        "avenida",
        "bairro",
        "cidade",
        "CEP",
        "endereço",
        "logradouro",
        "nº",
        "numero",
        "apto",
        "apartamento",
        "bloco",
        "casa",
        "residência"
    ],
    "TelefoneOuEmailMencionado": [
        "@" , 
        "gmail.com",
        "hotmail.com",
        "yahoo.com",
        "telefone",
        "whatsapp",
        "zap",
        "celular"
    ],
    "PossuiInformacaoBancaria": [
        "Banco do Brasil",
        "Itaú",
        "Bradesco",
        "Caixa Econômica",
        "Nubank",
        "agência",
        "conta",
        "saldo",
        "PIX",
        "transferência",
        "chave pix",
        "fatura",
        "boleto"
    ],
    "PossuiCartaoDeEmbarque": [
        "embarque",
        "cartão de embarque",
        "boarding pass",
        "voo",
        "flight",
        "embarcar",
        "check-in",
        "bilhete aéreo"
    ],
    "IndicacaoDeRenda": [
        "salário",
        "ganho",
        "renda",
        "fatura",
        "contracheque",
        "recebo",
        "receita",
        "rendimentos",
        "pro labore"
    ],
    "ClasseSocialInferida": [
        "classe média",
        "classe alta",
        "classe baixa",
        "classe média alta",
        "classe média baixa",
        "rico",
        "pobre",
        "média alta",
        "baixa renda"
    ],
    "PossuiPatrimonioMencionado": [
        "carro",
        "casa",
        "apartamento",
        "imóvel",
        "terreno",
        "propriedade",
        "mansão",
        "chácara",
        "fazenda"
    ],
    "EmpregoOuEmpresaMencionada": [
        "trabalho em",
        "emprego",
        "empresa",
        "contratado",
        "funcionário da",
        "funcionária da",
        "LinkedIn",
        "estágio em",
        "CLT",
        "PJ",
        "CNPJ",
        "abracei a vaga",
        "contratado pela"
    ],
    "BeneficioSocialMencionado": [
        "Bolsa Família",
        "auxílio emergencial",
        "BPC",
        "INSS",
        "aposentadoria",
        "benefício",
        "pensão",
        "auxílio",
        "cadúnico"
    ],
    "HistoricoFinanceiroMencionado": [
        "dívida",
        "dívidas",
        "financiamento",
        "emprestimo",
        "empréstimo",
        "cheque especial",
        "protestado",
        "fiador",
        "fatura atrasada",
        "boleto atrasado"
    ],
    "ScoreCreditoInferido": [
        "score",
        "Serasa",
        "SPC",
        "Boa Vista",
        "limite",
        "score de crédito",
        "pontuação de crédito"
    ],
    "FilhosOuDependentesMencionados": [
        "filho",
        "filha",
        "bebê",
        "criança",
        "dependente",
        "gestante",
        "maternidade",
        "tive filho",
        "meu filho"
    ],
    "RelatoDeViolenciaOuAbuso": [
        "abuso",
        "violência",
        "assédio",
        "sofri",
        "estupro",
        "agressão",
        "trauma",
        "violento",
        "espancamento",
        "machucado",
        "machucada",
        "bateram em",
        "gritei",
        "gritada"
    ],
    "HistoricoCriminalMencionado": [
        "prisão",
        "prisões",
        "cadeia",
        "fui preso",
        "fui presa",
        "crime",
        "polícia",
        "réu",
        "acusado",
        "processo",
        "penal",
        "delegacia",
        "juiz",
        "sentença"
    ]
}


keywords_lists = list(keywords_por_tema.values())
keywords = []
for sublista in keywords_lists:
    keywords.extend(sublista)


NEWS_KEYWORDS_TO_BLOCK = [
    "g1", "uol", "folha", "estadão", "cnn", "globonews", "record news", "bandnews", "r7", "metropoles",
    "anuncia", "comunicado", "informa", "reportagem", "entrevista coletiva", "nota oficial", 
    "segundo a assessoria", "divulgou nesta", "publicado no diário oficial",
    "prefeitura", "governo do estado", "ministério da", "secretaria de", "polícia civil", "polícia militar",
    "cotação", "ibovespa", "dólar", "selic", "ipca", "inflação", "mercado financeiro",
    "edital", "decreto", "lei nº", "portaria nº"
]


PERSONAL_WORDS_LIST = [
    "eu",
    "meu", "minha", "meus", "minhas",
    "mim", "comigo",
    "me",  "sou"

    "eu acho", "eu penso", "eu sinto", "eu acredito", "eu vejo",
    "eu quero", "eu queria", "eu quis",
    "eu preciso", "eu precisei",
    "eu gosto", "eu gostei", "eu adoraria", "eu amaria",
    "eu vou", "eu fui", "eu era", "eu estou", "eu estava", "eu estive",
    "eu tenho", "eu tive", "eu teria",
    "eu faço", "eu fiz", "eu faria",
    "eu digo", "eu disse",
    "eu sei", "eu soube",
    "eu posso", "eu pude",
    "eu devo", "eu devia",
    "eu espero", 
    "eu imagino", "eu imaginava",
    "eu costumo", "eu costumava",
    "eu aprendi", "eu descobri",
    "eu decidi", "eu resolvi",
    "eu notei", "eu percebi",

    "me sinto", "me senti", "me sentirei",
    "me acho", "me achei",
    "me lembro", "me lembrei",
    "me pergunto", "me perguntei",
    "me preocupo", "me preocupei",
    "me arrependo", "me arrependi",
    "me divirto", "me diverti",
    "me cuido", "me cuidei",
    "me expresso", "me expressei",
    "me identifico", "me identifiquei",
    "me esforço", "me esforcei",
    "me dedico", "me dediquei",
    "me orgulho", "me orgulhei",
    "me permito", "me permiti",
    "me surpreendo", "me surpreendi",
    "me interesso", "me interessei",
    "me apaixono", "me apaixonei",
    "me formei", "me mudei", "me casei", "me divorciei",
    "me demiti", "me candidatei", "me inscrevi",
    "me preparei", "me apresento", "me apresentei",
    "me considero", "me considerei",
    "me perdi", "me encontrei", 
    "me machuquei", "me curei",
    "me ferro", "me lasco",
    "me irrito", "me irritei",
    "me acalmo", "me acalmei",
    "me motivo", "me motivei",
    "me decepciono", "me decepcionei",
    "me cobro", "me cobrei",
    "me viro", 

    "na minha opinião", "do meu ponto de vista",
    "pra mim", "para mim",
    "em minha defesa",
    "sinceramente eu",
    "honestamente eu",
    "eu particularmente",

    "minha vida", "meu dia", "meu cotidiano",
    "minha família", "meus pais", "minha mãe", "meu pai",
    "meu filho", "minha filha", "meus filhos",
    "meu irmão", "minha irmã", "meus irmãos",
    "meu amigo", "minha amiga", "meus amigos", "minhas amigas",
    "meu amor", "meu namorado", "minha namorada", "meu marido", "minha esposa", "meu cônjuge",
    "meu corpo", "minha mente", "minha alma", "meu coração", # Coração no sentido figurado
    "meus sentimentos", "minhas emoções", "meus pensamentos", "minhas ideias",
    "meus sonhos", "meus medos", "minhas esperanças", "meus desejos",
    "minhas experiências", "minhas memórias", "minhas lembranças",
    "meu objetivo", "minha meta", "meu propósito",
    "meu problema", "minha dificuldade", "meu desafio",
    "minha casa", "meu lar", "meu quarto",
    "meu trabalho", "minha carreira", "meus estudos",
    "meu jeito", "minha maneira",
    "minha vez",
    "minha culpa", "meu erro", "meu acerto",
    "meu aniversário",
    "meu passado", "meu presente", "meu futuro",
    "minha jornada",
    "meu limite",
    "meu deus",
    "meu bem", 
    "minha cabeça", 

    "amo", "amei", "amarei", "amava",
    "odeio", "odiei",
    "gosto", "gostei", "gostaria", "gostava",
    "quero", "quis", "queria",
    "sinto", "senti", "sentia",
    "penso", "pensei", "pensava",
    "preciso", "precisei", "precisava",
    "acredito", "acreditei", "acreditava",
    "espero", "esperei", "esperava",
    "lembro-me", 
    "vi", "via", 
    "ouvi", "ouvia",
    "falei", "falava",
    "chorei", "chorava",
    "sorri", "sorria",
    "aprendi", "aprendia",
    "consegui", "conseguia",
    "tentei", "tentava",
    "decidi", "decidia",
    "morei", "morava",
    "trabalhei", "trabalhava",
    "estudei", "estudava",
    "viajei", "viajava",
    "sonhei", "sonhava",

    "quando eu era", "quando eu tinha",
    "lembro quando",
    "cresci",
    "nasci",

    "nossa", "poxa", "caramba", "eita", "putz", "aff", "ufa", "graças a deus",
    "que bom que", "ainda bem que",
    "infelizmente eu", "felizmente eu",
    "pra ser honesto", "pra ser sincero",

    "a meu ver",
    "confesso que",
    "pra falar a verdade",
    "no meu caso",
    "comigo acontece", "comigo foi assim",
    "estou sentindo", "estava sentindo",
    "estou pensando", "estava pensando",
    "estou fazendo", "estava fazendo",
    "eu mesmo", "eu mesma",
    "de minha parte",
    "minhas coisas",
    "meu momento",
    "meu cantinho",
    "meu refúgio",
    "minha rotina",
    "meu ponto fraco", "meu ponto forte",
    "meu maior medo", "meu maior sonho",
    "sou uma pessoa", "me considero uma pessoa",
    "tenho a impressão", "tive a impressão",
    "sinto falta", "senti falta"
]


def is_significant(text):
    if not text or len(text.strip()) < 40:
        return False 

    sentiment = TextBlob(text).sentiment.polarity
    subjectivity = TextBlob(text).sentiment.subjectivity
    if abs(sentiment) < 0.5:
        return False
    if abs(subjectivity) < 0.25:
        return False
    max_non_keywords = 2
    curr_nkw = 0
    for nkw in NEWS_KEYWORDS_TO_BLOCK:
        if re.search(rf'\b{nkw}\b', text, flags=re.IGNORECASE):
            curr_nkw += 1
        if max_non_keywords == curr_nkw:
            return False
    min_keywords = 4
    curr_kw = 0

    has_pkw = False
    for pkw in PERSONAL_WORDS_LIST:
        if re.search(rf'\b{pkw}\b', text, flags=re.IGNORECASE):
            has_pkw = True
    
    if has_pkw == False:
        return False

    for kw in keywords:
        if re.search(rf'\b{kw}\b', text, flags=re.IGNORECASE):
            curr_kw += 1
        if min_keywords == curr_kw:
            return True
    
    cpf_num_pattern = re.compile(r"\d{3}\.\d{3}\.\d{3}-\d{2}")
    if cpf_num_pattern.search(text):
        return True
    
    rg_num_pattern = re.compile(r"\d{1,2}\.\d{3}\.\d{3}\-\d")
    if rg_num_pattern.search(text):
        return True
    
    tel_num_pattern = re.compile(r"\(\d{2}\)\s?\d{4,5}\-\d{4}")
    if tel_num_pattern.search(text):
        return True
    return False


def process_user(user_id):
    """
    Função executada em cada processo: conecta no Mongo,
    busca apenas o campo 'posts' do usuário, testa cada post
    com is_significant() e, se encontrar algum, marca 'significant=True'
    e retorna 1. Caso contrário, retorna 0.
    """
    client = pm.MongoClient(uri)
    db = client[DB_NAME]
    data_coll = db[os.getenv("MONGO_COLLECTION_DATA")]

    doc = data_coll.find_one({"_id": user_id}, {"posts": 1})
    if not doc or "posts" not in doc:
        return 0

    for post in doc["posts"]:
        text = post.get("text", "")
        if is_significant(text):
            data_coll.update_one(
                {"_id": user_id},
                {"$set": {"significant": True}}
            )
            client.close()
            return 1

    client.close()
    return 0


if __name__ == "__main__":
    client_main = pm.MongoClient(uri)
    db_main = client_main[DB_NAME]
    data_coll_main = db_main[os.getenv("MONGO_COLLECTION_DATA")]

    cursor = data_coll_main.find(
        {"posts": {"$elemMatch": {"text": {"$ne": ""}, "lang": "pt"}}},
        {"_id": 1}
    )

    user_ids = [doc["_id"] for doc in cursor]
    client_main.close()

    significant_users = 0
    start_time = time.time()

    with Pool(processes=cpu_count()) as pool:
        for resultado in pool.imap_unordered(process_user, user_ids):
            if resultado == 1:
                significant_users += 1
                print(significant_users)
                if significant_users >= 15000:
                    pool.terminate()
                    break

    total_time = time.time() - start_time
    print("\n✅ Processamento concluído!")
    print(f"Tempo total: {total_time:.2f} segundos")