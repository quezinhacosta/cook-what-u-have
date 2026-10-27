"""
Pipeline de Ingestão de Dados (ingestion/pipeline.py)
Responsabilidade: Coordenar a extração das URLs do TudoGostoso
e salvar o arquivo JSON com os 4 campos limpos:
(titulo, tipo, receita, ingredientes) em ingestion/data/pratos.json.
"""

import json
from pathlib import Path
from ingestion.extractor import extrair_all, RawRecipe

# Caminho de saída: ingestion/data/pratos.json
OUTPUT_FILE = Path(__file__).parent / "data" / "pratos.json"

# Exemplos de URLs reais e variadas do TudoGostoso
URLS_TUDOGOSTOSO: tuple[str, ...] = (
    "https://www.tudogostoso.com.br/receita/23-bolo-de-cenoura.html",
    "https://www.tudogostoso.com.br/receita/1023-strogonoff-de-frango.html",
    "https://www.tudogostoso.com.br/receita/1176-panqueca-de-carne-moida.html",
    "https://www.tudogostoso.com.br/receita/1229-mousse-de-maracuja.html",
    "https://www.tudogostoso.com.br/receita/2012-arroz-de-forno-super-rapido.html",
    "https://www.tudogostoso.com.br/receita/1545-pudim-de-leite-condensado.html",
    "https://www.tudogostoso.com.br/receita/241-guacamole.html",
    "https://www.tudogostoso.com.br/receita/1090-omelete-rapido.html",
    "https://www.tudogostoso.com.br/receita/144-moqueca-de-peixe.html",
    "https://www.tudogostoso.com.br/receita/956-salada-de-maionese-tradicional.html",
)


def recipe_to_dict(recipe: RawRecipe) -> dict:
    """
    Função pura: converte a tupla imutável RawRecipe em dicionário para o JSON.
    Mantém os 4 campos essenciais:
    - titulo: Nome do prato
    - tipo: Categoria da comida
    - receita: O modo de preparo/instruções passo a passo
    - ingredientes: A lista de ingredientes
    """
    return {
        "titulo": recipe.titulo,
        "tipo": recipe.tipo,
        "receita": recipe.receita,
        "ingredientes": list(recipe.ingredientes)
    }


def salvar_pratos_json(receitas: tuple[RawRecipe, ...], destino: Path) -> int:
    """Função funcional que mapeia as receitas para dicionários e salva o JSON."""
    destino.parent.mkdir(parents=True, exist_ok=True)

    dados_serializaveis = list(map(recipe_to_dict, receitas))

    with open(destino, "w", encoding="utf-8") as f:
        json.dump(dados_serializaveis, f, ensure_ascii=False, indent=2)

    return len(dados_serializaveis)


def executar_ingestao(urls: tuple[str, ...] = URLS_TUDOGOSTOSO, destino: Path = OUTPUT_FILE) -> int:
    """
    Executa o fluxo funcional completo:
    URLs -> extrair_all() -> map(recipe_to_dict) -> json.dump()
    """
    print(f"Iniciando extração de {len(urls)} receitas do TudoGostoso com 4 campos...")
    receitas_extraidas = extrair_all(urls)

    total_salvo = salvar_pratos_json(receitas_extraidas, destino)
    print(f"Sucesso! {total_salvo} receitas completas salvas em: {destino}")
    return total_salvo


if __name__ == "__main__":
    executar_ingestao()
