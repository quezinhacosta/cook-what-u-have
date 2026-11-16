"""
Módulo de Gateway de E/S e Efeitos Colaterais (ingestion/io_gateway.py)
Responsabilidade: Centralizar de forma estrita todas as operações impuras de
entrada e saída (requisições HTTP via rede e persistência/leitura de arquivos no disco),
blindando as camadas de domínio, modelos, normalizador e parser contra side-effects.
"""

import json
from collections.abc import Callable
from typing import Any

import requests
from recipe_scrapers import scrape_html

from ingestion.models import recipe_to_dict

# Headers HTTP padrão simulando navegador comum
DEFAULT_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def safe_run(fn: Callable[[], Any], default: Any = None) -> Any:
    """Barreira de proteção: intercepta falhas de rede, disco ou scraping em operações de E/S."""
    try:
        return fn()
    except Exception:
        return default


baixar_html = lambda url, timeout=15: safe_run(
    lambda: (
        resp := requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout),
        resp.text if resp.status_code == 200 else "",
    )[-1],
    default="",
)

executar_scraper_seguro = lambda html, url: safe_run(
    lambda: scrape_html(html=html, org_url=url),
    default=None,
)

salvar_categoria_json = lambda resultado: (
    resultado.destino.parent.mkdir(parents=True, exist_ok=True),
    resultado.destino.write_text(
        json.dumps(list(map(recipe_to_dict, resultado.receitas)), ensure_ascii=False, indent=2),
        encoding="utf-8",
    ),
    len(resultado.receitas),
)[-1]

ler_categoria_json = lambda caminho_arquivo: (
    safe_run(
        lambda: (
            tuple(dados)
            if isinstance(dados := json.loads(caminho_arquivo.read_text(encoding="utf-8")), list)
            else ()
        ),
        default=(),
    )
    if caminho_arquivo.exists()
    else ()
)
