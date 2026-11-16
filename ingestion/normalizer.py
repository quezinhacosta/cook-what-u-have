"""
Módulo de Normalização Funcional de Ingredientes (ingestion/normalizer.py)
Responsabilidade: Transformar strings brutas de ingredientes da web
em termos canônicos padronizados através de funções 100% puras,
sem efeitos colaterais, sem dependência de rede e sem I/O de disco.
"""

import functools
import hashlib
import re
import unicodedata
from collections.abc import Callable

from ingestion.models import ProcessedRecipe

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

to_lower = lambda text: text.lower()

strip_accents = lambda text: "".join(
    filter(
        lambda c: unicodedata.category(c) != "Mn",
        unicodedata.normalize("NFD", text),
    )
)

remove_parenteses = lambda text: _REGEX_PARENTESES.sub(" ", text)

remove_quantidades_e_fracoes = lambda text: _REGEX_NUMEROS.sub(
    " ",
    _REGEX_FRAC_UNICODE.sub(" ", re.sub(r"(\d+)([a-zA-Z]+)", r"\1 \2", text)),
)

remove_unidades = lambda text: _REGEX_UNIDADES.sub(" ", text)

remove_modificadores = lambda text: _REGEX_MODIFICADORES.sub(" ", text)

limpa_simbolos_e_espacos = lambda text: " ".join(_REGEX_SIMBOLOS.sub(" ", text).split())

podar_inicio: Callable[[tuple[str, ...]], tuple[str, ...]] = lambda palavras: (
    podar_inicio(palavras[1:])
    if palavras and palavras[0] in CONECTIVOS_BORDAS
    else palavras
)

podar_fim: Callable[[tuple[str, ...]], tuple[str, ...]] = lambda palavras: (
    podar_fim(palavras[:-1])
    if palavras and palavras[-1] in CONECTIVOS_BORDAS
    else palavras
)

remove_conectivos_bordas = lambda text: " ".join(
    podar_fim(podar_inicio(tuple(text.split())))
)

singulariza_termos = lambda text: " ".join(
    map(lambda p: PLURAIS_CANONICOS.get(p, p), text.split())
)

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

extrair_ingrediente_central = lambda raw: (
    functools.reduce(lambda acc, fn: fn(acc), PIPELINE_TRANSFORMADORES, raw).strip()
)

normalizar_colecao_ingredientes = lambda ingredientes_originais: tuple(
    sorted(
        frozenset(
            filter(
                lambda ing: len(ing) >= 2,
                map(extrair_ingrediente_central, ingredientes_originais),
            )
        )
    )
)

slugify = lambda text: (
    re.sub(r"[^a-z0-9]+", "-", strip_accents(text.lower())).strip("-") or "item"
)

gerar_id_receita = lambda titulo, tipo: (
    f"{slugify(tipo)}_{slugify(titulo)}_{hashlib.sha256(f'{slugify(tipo)}:{slugify(titulo)}'.encode()).hexdigest()[:8]}"
)

processar_receita = lambda raw, categoria_alvo: ProcessedRecipe(
    id=gerar_id_receita(" ".join(raw.titulo.split()), categoria_alvo.strip().lower()),
    titulo=" ".join(raw.titulo.split()),
    tipo=categoria_alvo.strip().lower(),
    receita=raw.receita,
    ingredientes_originais=raw.ingredientes_originais,
    ingredientes_centrais=normalizar_colecao_ingredientes(raw.ingredientes_originais),
)
