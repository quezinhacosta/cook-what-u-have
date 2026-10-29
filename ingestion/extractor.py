# Responsável por receber chamada de uma URL e extrair apenas título, tipo, receita e ingredientes

from typing import Optional, NamedTuple
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from recipe_scrapers import scrape_me, scrape_html


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


def tudogostoso(url: str) -> bool:
    """Verifica se o domínio e rota pertencem validamente ao TudoGostoso."""
    try:
        parsed = urlparse(url.lower())
        e_dominio_valido = "tudogostoso.com.br" in parsed.netloc
        e_rota_de_receita = parsed.path.startswith("/receita/")
        return e_dominio_valido and e_rota_de_receita
    except Exception:
        return False


def obter_urls_recomendadas_categoria(url_categoria: str, limite: int = 15) -> tuple[str, ...]:
    """
    Função pura na extração de links:
    Acessa a página de categoria do TudoGostoso e extrai as URLs das
    primeiras receitas recomendadas/populares exibidas no topo da página.
    Retorna uma tupla imutável com até `limite` URLs únicas preservando a ordem.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resposta = requests.get(url_categoria, headers=headers, timeout=15)
        if resposta.status_code != 200:
            return ()

        soup = BeautifulSoup(resposta.text, "html.parser")

        # Coleta os links que apontam para receitas (/receita/... .html)
        links_iter = (
            a.get("href") for a in soup.find_all("a", href=True)
            if "/receita/" in a.get("href", "") and a.get("href", "").endswith(".html")
        )

        # Converte para URLs absolutas completas
        links_completos = (
            link if link.startswith("http") else f"https://www.tudogostoso.com.br{link}"
            for link in links_iter
        )

        # Deduplica funcionalmente preservando a ordem de recomendação original
        urls_unicas = tuple(dict.fromkeys(links_completos))

        return urls_unicas[:limite]
    except Exception:
        return ()


def extrair_receita(url: str) -> Optional[RawRecipe]:
    """Acessa a URL e extrai título, tipo, receita (instruções) e ingredientes."""
    if not tudogostoso(url):
        return None

    try:
        scraper = scrape_me(url)
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
        # Falhas de rede ou páginas inexistentes retornam None de forma segura
        return None


def extrair_de_html(html_content: str, url: str) -> Optional[RawRecipe]:
    """Extrai a receita a partir de conteúdo HTML bruto já carregado."""
    if not tudogostoso(url):
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
            ingredientes=tuple(ingredientes)
        )
    except Exception:
        return None


def extrair_all(urls: tuple[str, ...]) -> tuple[RawRecipe, ...]:
    """Processa múltiplas URLs de forma funcional (filter e map), descartando falhas."""
    urls_tudogostoso = filter(tudogostoso, urls)

    receitas_extraidas = map(extrair_receita, urls_tudogostoso)

    receitas_validas = filter(lambda r: r is not None, receitas_extraidas)

    return tuple(receitas_validas)
