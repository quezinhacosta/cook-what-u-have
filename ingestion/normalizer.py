"""
Módulo de Normalização Funcional de Ingredientes (ingestion/normalizer.py)
Responsabilidade: Transformar strings brutas de ingredientes da web
em termos canônicos padronizados através de funções 100% puras,
sem efeitos colaterais, sem dependência de rede e sem I/O de disco.
"""

import re
import unicodedata
import functools
import hashlib
from typing import Callable
from ingestion.models import RawRecipe, ProcessedRecipe

# Tipo formal de um transformador puro de texto: str -> str
TextTransformer = Callable[[str], str]

# ==============================================================================
# DICIONÁRIOS E CONSTANTES DECLARATIVAS IMUTÁVEIS
# ==============================================================================

# Unidades de medida comuns da culinária brasileira
UNIDADES_CULINARIAS: tuple[str, ...] = (
    "colher", "colheres", "sopa", "cha", "sobremesa", "cafe",
    "xicara", "xicaras", "copo", "copos", "grama", "gramas", "g",
    "quilo", "quilos", "kg", "mililitro", "mililitros", "ml",
    "litro", "litros", "l", "pitada", "pitadas", "dente", "dentes",
    "fatia", "fatias", "lata", "latas", "caixa", "caixas",
    "pacote", "pacotes", "pct", "unidade", "unidades", "un",
    "vidro", "vidros", "pote", "potes", "envelope", "envelopes",
    "tablete", "tabletes", "ramo", "ramos", "folha", "folhas",
    "talo", "talos", "punhado", "punhados", "prato", "pratos",
    "pedaco", "pedacos", "dose", "doses", "porcao", "porcoes"
)

# Modificadores de estado, corte e preparo que devem ser eliminados
MODIFICADORES_PREPARO: tuple[str, ...] = (
    "a gosto", "em cubos", "em rodelas", "em tiras", "em pedacos",
    "picado", "picada", "picados", "picadas",
    "ralado", "ralada", "ralados", "raladas",
    "cozido", "cozida", "cozidos", "cozidas",
    "fatiado", "fatiada", "fatiados", "fatiadas",
    "desfiado", "desfiada", "desfiados", "desfiadas",
    "moido", "moida", "moidos", "moidas",
    "derretido", "derretida", "derretidos", "derretidas",
    "amassado", "amassada", "amassados", "amassadas",
    "esmagado", "esmagada", "esmagados", "esmagadas",
    "lavado", "lavada", "lavados", "lavadas",
    "seco", "seca", "secos", "secas",
    "fresco", "fresca", "frescos", "frescas",
    "congelado", "congelada", "congelados", "congeladas",
    "peneirado", "peneirada", "peneirados", "peneiradas",
    "temperado", "temperada", "temperados", "temperadas",
    "medio", "media", "medios", "medias",
    "grande", "grandes", "pequeno", "pequena", "pequenos", "pequenas",
    "fino", "fina", "finos", "finas", "grosso", "grossa", "grossos", "grossas",
    "sem pele", "sem casca", "sem semente", "sem sementes", "com casca",
    "opcional", "morna", "morno", "quente", "gelado", "gelada",
    "extra virgem", "virgem"
)

# Preposições conectivas nas pontas das expressões
CONECTIVOS_BORDAS: frozenset[str] = frozenset((
    "de", "do", "da", "dos", "das", "e", "a", "ao", "aos",
    "com", "sem", "para", "em", "por"
))

# Mapeamento estático para formas singulares dos alimentos mais frequentes
PLURAIS_CANONICOS: dict[str, str] = {
    "ovos": "ovo",
    "cenouras": "cenoura",
    "batatas": "batata",
    "tomates": "tomate",
    "cebolas": "cebola",
    "bananas": "banana",
    "macas": "maca",
    "morangos": "morango",
    "limoes": "limao",
    "pimentoes": "pimentao",
    "laranjas": "laranja",
    "mangas": "manga",
    "abobrinhas": "abobrinha",
    "berinjelas": "berinjela",
}

# Expressões Regulares compiladas uma única vez
_REGEX_PARENTESES = re.compile(r"\([^)]*\)|\[[^\]]*\]")
_REGEX_FRAC_UNICODE = re.compile(r"[½¼¾⅓⅔⅛⅜⅝⅞]")
_REGEX_NUMEROS = re.compile(r"\b\d+\s+e\s+\d+/\d+\b|\b\d+/\d+\b|\b\d+[.,]?\d*\b")
_REGEX_UNIDADES = re.compile(r"\b(" + "|".join(UNIDADES_CULINARIAS) + r")\b")
_REGEX_MODIFICADORES = re.compile(r"\b(" + "|".join(MODIFICADORES_PREPARO) + r")\b")
_REGEX_SIMBOLOS = re.compile(r"[^a-z\s]")

# ==============================================================================
# FUNÇÕES PURAS DE TRANSFORMAÇÃO ATÔMICA
# ==============================================================================

def to_lower(text: str) -> str:
    """Função pura: converte string para caixa baixa."""
    return text.lower()


def strip_accents(text: str) -> str:
    """Função pura: remove acentos normalizando caracteres Unicode NFD."""
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def remove_parenteses(text: str) -> str:
    """Função pura: remove conteúdos entre parênteses e colchetes."""
    return _REGEX_PARENTESES.sub(" ", text)


def remove_quantidades_e_fracoes(text: str) -> str:
    """Função pura: elimina numerais inteiros, decimais e frações culinárias."""
    sem_unicode = _REGEX_FRAC_UNICODE.sub(" ", text)
    return _REGEX_NUMEROS.sub(" ", sem_unicode)


def remove_unidades(text: str) -> str:
    """Função pura: remove termos de unidades de medida."""
    return _REGEX_UNIDADES.sub(" ", text)


def remove_modificadores(text: str) -> str:
    """Função pura: elimina termos descritivos de técnicas de corte ou preparo."""
    return _REGEX_MODIFICADORES.sub(" ", text)


def limpa_simbolos_e_espacos(text: str) -> str:
    """Função pura: preserva apenas caracteres alfabéticos e colapsa múltiplos espaços."""
    apenas_letras = _REGEX_SIMBOLOS.sub(" ", text)
    return " ".join(apenas_letras.split())


def remove_conectivos_bordas(text: str) -> str:
    """Função pura: remove preposições no início e no fim da expressão."""
    tokens = text.split()

    def podar_inicio(palavras: tuple[str, ...]) -> tuple[str, ...]:
        return podar_inicio(palavras[1:]) if palavras and palavras[0] in CONECTIVOS_BORDAS else palavras

    def podar_fim(palavras: tuple[str, ...]) -> tuple[str, ...]:
        return podar_fim(palavras[:-1]) if palavras and palavras[-1] in CONECTIVOS_BORDAS else palavras

    resultado = podar_fim(podar_inicio(tuple(tokens)))
    return " ".join(resultado)


def singulariza_termos(text: str) -> str:
    """Função pura: mapeia palavras no plural para sua forma singular canônica."""
    palavras = text.split()
    return " ".join(map(lambda p: PLURAIS_CANONICOS.get(p, p), palavras))


# Pipeline imutável de transformações encadeadas
PIPELINE_TRANSFORMADORES: tuple[TextTransformer, ...] = (
    to_lower,
    strip_accents,
    remove_parenteses,
    remove_quantidades_e_fracoes,
    remove_unidades,
    remove_modificadores,
    limpa_simbolos_e_espacos,
    remove_conectivos_bordas,
    singulariza_termos,
)

# ==============================================================================
# FUNÇÕES DE ALTO NÍVEL DO NORMALIZADOR
# ==============================================================================

def extrair_ingrediente_central(raw: str) -> str:
    """
    Função pura de normalização:
    Aplica sucessivamente a sequência de transformadores funcionais via reduce.
    Retorna o termo canônico limpo (ex: '2 xícaras de farinha de trigo' -> 'farinha de trigo').
    """
    return functools.reduce(lambda acc, fn: fn(acc), PIPELINE_TRANSFORMADORES, raw).strip()


def normalizar_colecao_ingredientes(ingredientes_originais: tuple[str, ...]) -> tuple[str, ...]:
    """
    Função pura: recebe uma tupla de strings brutas de ingredientes,
    aplica a extração canônica para cada um, descarta vazios e
    retorna uma tupla imutável com os ingredientes canônicos únicos e ordenados.
    """
    ingredientes_processados = map(extrair_ingrediente_central, ingredientes_originais)
    validos = filter(lambda ing: len(ing) >= 2, ingredientes_processados)
    # Deduplicação imutável através de frozenset e ordenação determinística
    return tuple(sorted(frozenset(validos)))


def slugify(text: str) -> str:
    """Função pura: gera um slug ASCII limpo a partir de qualquer texto."""
    norm = strip_accents(text.lower())
    clean = re.sub(r"[^a-z0-9]+", "-", norm).strip("-")
    return clean or "item"


def gerar_id_receita(titulo: str, tipo: str) -> str:
    """
    Função pura: gera um ID determinístico e legível baseado no tipo e título.
    Exemplo: 'massas_macarrao-a-carbonara_a1b2c3d4'
    """
    slug_tipo = slugify(tipo)
    slug_titulo = slugify(titulo)
    hash_curto = hashlib.sha256(f"{slug_tipo}:{slug_titulo}".encode("utf-8")).hexdigest()[:8]
    return f"{slug_tipo}_{slug_titulo}_{hash_curto}"


def processar_receita(raw: RawRecipe, categoria_alvo: str) -> ProcessedRecipe:
    """
    Função pura de projeção:
    Transforma um RawRecipe bruto em uma ProcessedRecipe pronta para o grafo.
    Gera o identificador único e extrai os ingredientes centrais.
    """
    categoria_final = categoria_alvo.strip().lower()
    titulo_limpo = " ".join(raw.titulo.split())
    ingredientes_centrais = normalizar_colecao_ingredientes(raw.ingredientes_originais)
    id_determinismo = gerar_id_receita(titulo_limpo, categoria_final)

    return ProcessedRecipe(
        id=id_determinismo,
        titulo=titulo_limpo,
        tipo=categoria_final,
        receita=raw.receita,
        ingredientes_originais=raw.ingredientes_originais,
        ingredientes_centrais=ingredientes_centrais,
    )
