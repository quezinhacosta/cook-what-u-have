"""
Módulo de Extração de Receitas (ingestion/extractor.py)
Responsabilidade: Mapear URLs/HTML para a estrutura de dados imutável RawRecipe.
Separa rigorosamente o parsing puro de dados do I/O de rede.
"""

import functools
from typing import Optional, NamedTuple
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from recipe_scrapers import scrape_html


class RawRecipe(NamedTuple):
    """
    Entidade imutável que guarda o resultado completo da extração:
    - titulo: Nome do prato
    - tipo: Categoria/tipo da comida (ex: Massas, Sobremesas)
    - receita: O modo de preparo/instruções da receita
    - ingredientes: Coleção imutável de ingredientes
    """
    titulo: str
    tipo: str
    receita: str
    ingredientes: tuple[str, ...]


# ==============================================================================
# NÚCLEO FUNCIONAL (FUNÇÕES 100% PURAS)
# ==============================================================================

def tudogostoso(url: str) -> bool:
    """Função pura: verifica se o domínio e rota pertencem validamente ao TudoGostoso."""
    try:
        parsed = urlparse(url.lower())
        return "tudogostoso.com.br" in parsed.netloc and parsed.path.startswith("/receita/")
    except Exception:
        return False


def deduplicar_preservando_ordem(sequencia: tuple[str, ...]) -> tuple[str, ...]:
    """Função pura: deduplica uma tupla imutável de strings preservando a ordem original."""
    def acumular_unico(acc: tuple[str, ...], item: str) -> tuple[str, ...]:
        return acc if item in acc else acc + (item,)

    return functools.reduce(acumular_unico, sequencia, ())


def normalizar_url_relativa(link: str) -> str:
    """Função pura: transforma links relativos em URLs absolutas completas."""
    return link if link.startswith("http") else f"https://www.tudogostoso.com.br{link}"


def extrair_de_html(html_content: str, url: str) -> Optional[RawRecipe]:
    """
    Função pura: extrai a receita a partir de conteúdo HTML já carregado.
    Dada a mesma string HTML e URL, sempre retornará exatamente a mesma RawRecipe.
    """
    if not html_content or not tudogostoso(url):
        return None

    try:
        scraper = scrape_html(html=html_content, org_url=url)
        titulo = scraper.title()
        ingredientes = scraper.ingredients()
        tipo = (getattr(scraper, "category", lambda: "Geral")() or "Geral").strip()
        receita_instrucoes = (getattr(scraper, "instructions", lambda: "")() or "").strip()

        if not titulo or not ingredientes:
            return None

        return RawRecipe(
            titulo=titulo.strip(),
            tipo=tipo,
            receita=receita_instrucoes,
            ingredientes=tuple(ingredientes)  # Coleção imutável
        )
    except Exception:
        return None


def processar_links_categoria_html(html_content: str, limite: int) -> tuple[str, ...]:
    """Função pura: extrai e filtra URLs de receitas a partir do HTML da categoria."""
    if not html_content:
        return ()

    soup = BeautifulSoup(html_content, "html.parser")
    
    # Gerador declarativo para capturar links de receitas
    raw_links = (
        a.get("href") for a in soup.find_all("a", href=True)
        if "/receita/" in a.get("href", "") and a.get("href", "").endswith(".html")
    )
    
    urls_absolutas = tuple(map(normalizar_url_relativa, raw_links))
    urls_unicas = deduplicar_preservando_ordem(urls_absolutas)
    
    return urls_unicas[:limite]


# ==============================================================================
# CASCA DE EFEITOS COLATERAIS (I/O ISOLADO DE REDE)
# ==============================================================================

def baixar_html_pagina(url: str, timeout: int = 15) -> str:
    """Efeito colateral isolado: realiza requisição HTTP e retorna o HTML da página."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resposta = requests.get(url, headers=headers, timeout=timeout)
        return resposta.text if resposta.status_code == 200 else ""
    except Exception:
        return ""


def obter_urls_recomendadas_categoria(url_categoria: str, limite: int = 15) -> tuple[str, ...]:
    """Efeito colateral de borda: baixa o HTML da categoria e chama a extração pura."""
    html = baixar_html_pagina(url_categoria)
    return processar_links_categoria_html(html, limite)


def extrair_receita(url: str) -> Optional[RawRecipe]:
    """Efeito colateral de borda: baixa o HTML de uma receita e executa a transformação pura."""
    if not tudogostoso(url):
        return None
    html = baixar_html_pagina(url)
    return extrair_de_html(html, url)


def extrair_all(urls: tuple[str, ...]) -> tuple[RawRecipe, ...]:
    """
    Orquestra o mapeamento de múltiplas URLs de forma funcional:
    Filtra URLs válidas -> Mapeia extração -> Filtra resultados não nulos.
    """
    urls_validas = filter(tudogostoso, urls)
    receitas_extraidas = map(extrair_receita, urls_validas)
    receitas_validas = filter(lambda r: r is not None, receitas_extraidas)

    return tuple(receitas_validas)