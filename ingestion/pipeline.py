"""
Pipeline de Ingestão de Dados por Categoria (ingestion/pipeline.py)
Responsabilidade: Mapear até 15 receitas recomendadas do TudoGostoso
para cada categoria presente na pasta data/, salvando cada pratos.json
em sua respectiva subpasta (ex: data/massas/pratos.json).
"""

import sys
import json
from pathlib import Path
from ingestion.extractor import (
    RawRecipe,
    obter_urls_recomendadas_categoria,
    extrair_all,
)

# Diretório base dos dados: ingestion/data/
DATA_DIR = Path(__file__).parent / "data"

# Mapeamento declarativo imutável: (Nome da Pasta, URL da Categoria no TudoGostoso)
CATEGORIAS_TUDOGOSTOSO: tuple[tuple[str, str], ...] = (
    ("aves", "https://www.tudogostoso.com.br/categorias/1009-aves"),
    ("bolos e tortas", "https://www.tudogostoso.com.br/categorias/1000-bolos-e-tortas-doces"),
    ("carnes", "https://www.tudogostoso.com.br/categorias/1004-carnes"),
    ("doces e sobremesas", "https://www.tudogostoso.com.br/categorias/1037-doces-e-sobremesas"),
    ("massas", "https://www.tudogostoso.com.br/categorias/1028-massas"),
    ("peixes e frutos do mar", "https://www.tudogostoso.com.br/categorias/1014-peixes-e-frutos-do-mar"),
    ("saladas e molhos", "https://www.tudogostoso.com.br/categorias/1023-saladas-molhos-e-acompanhamentos"),
    ("sopas", "https://www.tudogostoso.com.br/categorias/1027-sopas"),
)


def recipe_to_dict(recipe: RawRecipe) -> dict:
    """Função pura: converte a tupla imutável RawRecipe em dicionário para o JSON."""
    return {
        "titulo": recipe.titulo,
        "tipo": recipe.tipo,
        "receita": recipe.receita,
        "ingredientes": list(recipe.ingredientes),
    }


def salvar_pratos_categoria(receitas: tuple[RawRecipe, ...], destino: Path) -> int:
    """Função que projeta as receitas para dicionários e salva no pratos.json de destino."""
    destino.parent.mkdir(parents=True, exist_ok=True)

    dados_serializaveis = list(map(recipe_to_dict, receitas))

    with open(destino, "w", encoding="utf-8") as f:
        json.dump(dados_serializaveis, f, ensure_ascii=False, indent=2)

    return len(dados_serializaveis)


def processar_categoria(categoria_nome: str, categoria_url: str, limite: int = 15) -> tuple[str, int]:
    """
    Processa uma única categoria:
    1. Obtém as primeiras `limite` URLs recomendadas da categoria.
    2. Extrai os dados completos via extractor.
    3. Salva em data/<categoria_nome>/pratos.json.
    """
    destino = DATA_DIR / categoria_nome / "pratos.json"

    print(f"\n [{categoria_nome.upper()}] Buscando até {limite} receitas recomendadas...")
    urls = obter_urls_recomendadas_categoria(categoria_url, limite=limite)

    if not urls:
        print(f" Nenhuma URL encontrada para a categoria '{categoria_nome}'.")
        return (categoria_nome, 0)

    print(f"   ↳ {len(urls)} URLs recomendadas identificadas. Extraindo dados...")
    receitas_extraidas = extrair_all(urls)

    total_salvo = salvar_pratos_categoria(receitas_extraidas, destino)
    print(f" {total_salvo} receitas salvas em: {destino.relative_to(Path.cwd())}")

    return (categoria_nome, total_salvo)


def executar_ingestao_categorias(
    categorias: tuple[tuple[str, str], ...] = CATEGORIAS_TUDOGOSTOSO,
    limite_por_categoria: int = 15,
) -> dict[str, int]:
    """
    Orquestra funcionalmente o processamento de todas as categorias mapeadas:
    Utiliza map() para transformar cada categoria em seu resultado salvo, sem loops imperativos.
    """
    print(f" Iniciando mapeamento de receitas recomendadas (limite: {limite_por_categoria}/categoria)...")
    print(f"Categorias a processar: {[cat[0] for cat in categorias]}")

    # Encadeamento puro com map
    resultados = tuple(
        map(
            lambda cat: processar_categoria(cat[0], cat[1], limite=limite_por_categoria),
            categorias,
        )
    )

    resumo = dict(resultados)
    total_geral = sum(resumo.values())

    print("\n" + "=" * 60)
    print(f"Processamento concluído!")
    print(f"Total de receitas salvas: {total_geral}")
    for cat_nome, qtd in resumo.items():
        print(f"  • {cat_nome}: {qtd} receitas")
    print("=" * 60)

    return resumo


def main() -> None:
    """
    Ponto de entrada:
    - Sem argumentos: Processa todas as 8 categorias da pasta data/.
    - Com argumento: Processa apenas a categoria informada (ex: 'python -m ingestion.pipeline massas').
    """
    filtro_categoria = sys.argv[1].lower().strip() if len(sys.argv) > 1 else None

    if filtro_categoria:
        categorias_selecionadas = tuple(
            filter(lambda cat: filtro_categoria in cat[0].lower(), CATEGORIAS_TUDOGOSTOSO)
        )
        if not categorias_selecionadas:
            print(f" Categoria '{filtro_categoria}' não encontrada.")
            print(f"Opções disponíveis: {[cat[0] for cat in CATEGORIAS_TUDOGOSTOSO]}")
            return
        executar_ingestao_categorias(categorias_selecionadas, limite_por_categoria=15)
    else:
        executar_ingestao_categorias(CATEGORIAS_TUDOGOSTOSO, limite_por_categoria=15)


if __name__ == "__main__":
    main()
