"""
Módulo de Parsing Funcional de HTML (ingestion/parser.py)
Responsabilidade: Transformar strings HTML em entidades de dados imutáveis
através de funções 100% puras (sem requisições HTTP e sem E/S de arquivos).
"""

import functools
from collections.abc import Callable
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from ingestion.io_gateway import executar_scraper_seguro
from ingestion.models import RawRecipe

# ==============================================================================
# FUNÇÕES PURAS DE VALIDAÇÃO E RESOLUÇÃO DE URL
# ==============================================================================

_tudogostoso_valido = lambda parsed: (
    "tudogostoso.com.br" in parsed.netloc and parsed.path.startswith("/receita/")
)

tudogostoso = lambda url: (
    bool(url and isinstance(url, str) and _tudogostoso_valido(urlparse(url.lower())))
)

normalizar_url_relativa = lambda link: (
    link.strip() if link.strip().startswith("http") else f"https://www.tudogostoso.com.br{link.strip()}"
)

_acc_unico: Callable[[tuple[str, ...], str], tuple[str, ...]] = (
    lambda acc, item: acc if item in acc else (*acc, item)
)

deduplicar_preservando_ordem: Callable[[tuple[str, ...]], tuple[str, ...]] = (
    lambda sequencia: functools.reduce(_acc_unico, sequencia, ())
)

# ==============================================================================
# FUNÇÕES PURAS DE PARSING DE HTML
# ==============================================================================

gerar_url_pagina = lambda base_url, pagina: (
    base_url if pagina <= 1 else f"{base_url}?page={pagina}"
)

formatar_passos_receita = lambda instructions: (
    tuple(filter(lambda p: len(p) > 0, map(str.strip, instructions.splitlines())))
    if instructions
    else ()
)

extrair_links_categoria_html = lambda html_content, limite=50: (
    deduplicar_preservando_ordem(
        tuple(
            map(
                normalizar_url_relativa,
                map(
                    lambda a: str(a.get("href")),
                    filter(
                        lambda a: (
                            isinstance(a.get("href"), str)
                            and "/receita/" in str(a.get("href"))
                            and str(a.get("href")).endswith(".html")
                        ),
                        BeautifulSoup(html_content, "html.parser").find_all("a", href=True),
                    ),
                ),
            )
        )
    )[:limite]
    if html_content
    else ()
)

_extrair_passos_scraper = lambda scraper: (
    tuple(filter(lambda s: len(s) > 0, map(str.strip, scraper.instructions_list())))
    if callable(getattr(scraper, "instructions_list", None)) and scraper.instructions_list()
    else formatar_passos_receita((scraper.instructions() or "").strip())
)

_construir_raw_recipe = lambda scraper, url, tipo_padrao: (
    (
        lambda titulo, passos, ingredientes: (
            RawRecipe(
                titulo=titulo,
                tipo=(tipo_padrao or (getattr(scraper, "category", lambda: "")() or "").strip() or "Geral").strip(),
                receita=passos,
                ingredientes_originais=ingredientes,
                url=url,
            )
            if titulo and ingredientes and passos
            else None
        )
    )(
        (scraper.title() or "").strip(),
        _extrair_passos_scraper(scraper),
        tuple(scraper.ingredients() or ()),
    )
)

extrair_receita_html = lambda html_content, url, tipo_padrao="", scraper_fn=executar_scraper_seguro: (
    (
        lambda scraper: _construir_raw_recipe(scraper, url, tipo_padrao)
        if scraper is not None
        else None
    )(scraper_fn(html_content, url))
    if html_content and tudogostoso(url)
    else None
)
