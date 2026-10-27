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

        


