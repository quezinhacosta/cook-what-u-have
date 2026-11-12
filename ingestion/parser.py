"""
Módulo de Parsing Funcional de HTML (ingestion/parser.py)
Responsabilidade: Transformar strings HTML em entidades de dados imutáveis
através de funções 100% puras (sem requisições HTTP e sem E/S de arquivos).
"""

import functools
from typing import Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from recipe_scrapers import scrape_html
from ingestion.models import RawRecipe


# ==============================================================================
# FUNÇÕES PURAS DE VALIDAÇÃO E RESOLUÇÃO DE URL
# ==============================================================================

def tudogostoso(url: str) -> bool:
    """Função pura: verifica se a URL pertence estritamente a uma receita do TudoGostoso."""
    try:
        parsed = urlparse(url.lower())
        e_dominio = "tudogostoso.com.br" in parsed.netloc
        e_receita = parsed.path.startswith("/receita/")
        return e_dominio and e_receita
    except Exception:
        return False


def normalizar_url_relativa(link: str) -> str:
    """Função pura: transforma links relativos em URLs absolutas completas."""
    link_limpo = link.strip()
    return link_limpo if link_limpo.startswith("http") else f"https://www.tudogostoso.com.br{link_limpo}"


def deduplicar_preservando_ordem(sequencia: tuple[str, ...]) -> tuple[str, ...]:
    """Função pura: deduplica uma tupla imutável preservando a ordem original via reduce."""
    def acumular_unico(acc: tuple[str, ...], item: str) -> tuple[str, ...]:
        return acc if item in acc else acc + (item,)

    return functools.reduce(acumular_unico, sequencia, ())


# ==============================================================================
# FUNÇÕES PURAS DE PARSING DE HTML
# ==============================================================================

def formatar_passos_receita(instructions: str) -> tuple[str, ...]:
    """
    Função pura: divide a string de instruções em passos individuais limpos,
    eliminando linhas vazias e espaços redundantes.
    """
    if not instructions:
        return ()
    linhas = instructions.splitlines()
    passos_limpos = map(str.strip, linhas)
    passos_validos = filter(lambda p: len(p) > 0, passos_limpos)
    return tuple(passos_validos)


def extrair_links_categoria_html(html_content: str, limite: int = 15) -> tuple[str, ...]:
    """
    Função pura: analisa o HTML da página de uma categoria e extrai as URLs
    das primeiras receitas recomendadas/populares.
    Retorna até `limite` URLs únicas preservando a ordem do topo.
    """
    if not html_content:
        return ()

    try:
        soup = BeautifulSoup(html_content, "html.parser")
        raw_links = (
            a.get("href") for a in soup.find_all("a", href=True)
            if "/receita/" in a.get("href", "") and a.get("href", "").endswith(".html")
        )
        urls_absolutas = tuple(map(normalizar_url_relativa, raw_links))
        urls_unicas = deduplicar_preservando_ordem(urls_absolutas)
        return urls_unicas[:limite]
    except Exception:
        return ()


def extrair_receita_html(html_content: str, url: str, tipo_padrao: str = "") -> Optional[RawRecipe]:
    """
    Função pura de extração:
    Recebe o conteúdo HTML bruto, a URL de origem e uma categoria padrão de fallback.
    Executa o parser do recipe-scrapers sobre a string e retorna uma RawRecipe imutável.
    Se o HTML for inválido ou faltarem dados essenciais, retorna None sem quebrar o fluxo.
    """
    if not html_content or not tudogostoso(url):
        return None

    try:
        scraper = scrape_html(html=html_content, org_url=url)
        titulo = (scraper.title() or "").strip()
        ingredientes_raw = tuple(scraper.ingredients() or ())

        # Prioriza categoria da página; caso vazia, utiliza a categoria da pasta/chamada
        obter_cat = getattr(scraper, "category", lambda: "")
        categoria_site = (obter_cat() or "").strip()
        tipo_final = (tipo_padrao or categoria_site or "Geral").strip()

        # Extração dos passos originais
        obter_lista = getattr(scraper, "instructions_list", None)
        if callable(obter_lista) and obter_lista():
            passos = tuple(filter(lambda s: len(s) > 0, map(str.strip, obter_lista())))
        else:
            instrucoes_str = (scraper.instructions() or "").strip()
            passos = formatar_passos_receita(instrucoes_str)

        # Validação estrita dos campos mandatórios
        if not titulo or not ingredientes_raw or not passos:
            return None

        return RawRecipe(
            titulo=titulo,
            tipo=tipo_final,
            receita=passos,
            ingredientes_originais=ingredientes_raw,
            url=url,
        )
    except Exception:
        return None
