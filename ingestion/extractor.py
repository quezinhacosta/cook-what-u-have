#Responsavel por receber chamada de uma URL e extrai apenas o titulo, receitas e ingredientes

from typing import Optional, NamedTuple
from recipe_scrapers import scrape_me
from urllib.parse import urlparse

class RawRecipe(NamedTuple):
    "entidade imutavel que vai guardar os unicos resultados das extrações das paginas"
    titulo: str
    receita: str
    ingredientes: tuple[str, ...] #vários ingredientes

def tudogostoso(url: str) -> bool:
    #verifica se o dominio é valido
    try:
        parsed = urlparse(url.lower())
        e_dominio_valido = "tudogostoso.com.br" in parsed.netloc
        e_rota_de_receita = parsed.path.startswith("/receita/")
        return e_dominio_valido and e_rota_de_receita
    except Exception:
        return False


def extrair_receita(url: str) -> Optional[RawRecipe]:
    #acessa a url e retira os campos necessarios

    if not tudogostoso(url): 
        return None

    try:
        scraper = scrape_me(url)
        ingredientes = scraper.ingredients()
        obter_categoria = getattr(scraper, "category", lambda: "Geral")
        receita_categoria = obter_categoria() or "Geral"

        if not titulo or not ingredientes:
            return None
        return RawRecipe(
            titulo=titulo.strip(),
            receita=receita_categoria.strip(),
            ingredientes=tuple(ingredientes)  # Coleção imutável
        )
    except Exception:
        # Falhas de rede ou páginas inexistentes retornam None de forma segura
        return None

def extrair(html_content: str, url:str) -> Optional[RawRecipe]:
    if not tudogostoso(url):
        return None
    try:
        scraper = scrape_html(html=html_content, org_url=url)
        return RawRecipe(
            titulo=scraper.title().strip(),
            receita=(getattr(scraper, "category", lambda: "Geral")() or "Geral").strip(),
            ingredientes=tuple(scraper.ingredients())
        )
    except Exception:
        return None

def extrair_all(urls: tuple[str, ...]) -> tuple[RawRecipe, ...]:

    urls_tudogostoso = filter(is_tudogostoso_url, urls)

    receitas_extraidas = map(extrair_receita_tudogostoso, urls_tudogostoso)
  
    receitas_validas = filter(lambda r: r is not None, receitas_extraidas)
    
    return tuple(receitas_validas)
