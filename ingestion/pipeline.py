"""
Pipeline de Ingestão de Dados por Categoria (ingestion/pipeline.py)
Responsabilidade: Mapear até 15 receitas recomendadas do TudoGostoso
para cada categoria presente na pasta data/, salvando cada pratos.json
em sua respectiva subpasta (ex: data/massas/pratos.json).
"""

import sys
import json
from pathlib import Path
from typing import NamedTuple
from ingestion.extractor import (
    RawRecipe,
    obter_urls_recomendadas_categoria,
    extrair_all,
)

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

class CategoriaResultado(NamedTuple):
    """Estrutura imutável para transportar os dados processados."""
    nome: str
    destino: Path
    receitas_dict: tuple[dict, ...]


# ==============================================================================
# NÚCLEO FUNCIONAL (FUNÇÕES 100% PURAS)
# ==============================================================================

def recipe_to_dict(recipe: RawRecipe) -> dict:
    """Função pura: converte RawRecipe para estrutura de dicionário imutável em conceito."""
    return {
        "titulo": recipe.titulo,
        "tipo": recipe.tipo,
        "receita": recipe.receita,
        "ingredientes": tuple(recipe.ingredientes),
    }


def mapear_categoria_para_resultado(
    categoria: tuple[str, str],
    receitas: tuple[RawRecipe, ...],
    base_dir: Path
) -> CategoriaResultado:
    """Função pura: projeta receitas em objetos CategoriaResultado sem tocar no disco ou E/S."""
    nome, _ = categoria
    destino = base_dir / nome / "pratos.json"
    dados_dict = tuple(map(recipe_to_dict, receitas))
    return CategoriaResultado(nome=nome, destino=destino, receitas_dict=dados_dict)


def filtrar_categorias(
    filtro: str | None,
    categorias: tuple[tuple[str, str], ...]
) -> tuple[tuple[str, str], ...]:
    """Função pura: filtra a tupla imutável de categorias baseada em uma query."""
    if not filtro:
        return categorias
    return tuple(filter(lambda cat: filtro.lower() in cat[0].lower(), categorias))


def formatar_linha_resumo(item: tuple[str, int]) -> str:
    """Função pura: formata cada item do resultado final para exibição."""
    return f"  • {item[0]}: {item[1]} receitas"


# ==============================================================================
# CASCA DE EFEITOS COLATERAIS (I/O ISOLADO NAS BORDAS)
# ==============================================================================

def efetuar_persistencia(resultado: CategoriaResultado) -> int:
    """Efeito colateral isolado: cria diretórios e grava os dados no disco."""
    resultado.destino.parent.mkdir(parents=True, exist_ok=True)
    with open(resultado.destino, "w", encoding="utf-8") as f:
        json.dump(list(resultado.receitas_dict), f, ensure_ascii=False, indent=2)
    return len(resultado.receitas_dict)


def processar_e_salvar_categoria(
    categoria: tuple[str, str],
    base_dir: Path,
    limite: int = 15
) -> tuple[str, int]:
    """Efeito colateral isolado: busca na web, chama transformação pura e persiste."""
    nome, url = categoria
    print(f"\n [{nome.upper()}] Buscando até {limite} receitas recomendadas...")
    urls = obter_urls_recomendadas_categoria(url, limite=limite)

    if not urls:
        print(f" Nenhuma URL encontrada para a categoria '{nome}'.")
        return (nome, 0)

    print(f"   ↳ {len(urls)} URLs encontradas. Extraindo dados...")
    receitas_extraidas = extrair_all(urls)

    resultado_puro = mapear_categoria_para_resultado(categoria, receitas_extraidas, base_dir)
    total_salvo = efetuar_persistencia(resultado_puro)

    print(f" {total_salvo} receitas salvas em: {resultado_puro.destino}")
    return (nome, total_salvo)


def main() -> None:
    base_dir = Path(__file__).parent / "data"
    filtro_categoria = sys.argv[1].strip() if len(sys.argv) > 1 else None

    cats_para_processar = filtrar_categorias(filtro_categoria, CATEGORIAS_TUDOGOSTOSO)

    if not cats_para_processar:
        print(f" Categoria '{filtro_categoria}' não encontrada.")
        print(f"Opções disponíveis: {[cat[0] for cat in CATEGORIAS_TUDOGOSTOSO]}")
        return

    print(f" Iniciando mapeamento de receitas recomendadas...")
    
    # Processamento encadeado declarativamente via map
    resultados = tuple(
        map(
            lambda cat: processar_e_salvar_categoria(cat, base_dir, limite=15),
            cats_para_processar
        )
    )

    total_geral = sum(map(lambda r: r[1], resultados))
    linhas_resumo = "\n".join(map(formatar_linha_resumo, resultados))

    print("\n" + "=" * 60)
    print("Processamento concluído!")
    print(f"Total de receitas salvas: {total_geral}")
    print(linhas_resumo)
    print("=" * 60)


if __name__ == "__main__":
    main()