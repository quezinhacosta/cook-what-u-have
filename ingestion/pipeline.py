import sys
import json
from pathlib import Path
from typing import NamedTuple
from ingestion.extractor import (
    RawRecipe,
    obter_urls_recomendadas_categoria,
    extrair_all,
)

DATA_DIR = Path(__file__).parent / "data"

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
    nome: str
    destino: Path
    receitas_dict: tuple[dict, ...]

# --- NÚCLEO FUNCIONAL (100% PURAS) ---

def recipe_to_dict(recipe: RawRecipe) -> dict:
    """Função pura: converte RawRecipe para dicionário imutável em termos de conceito."""
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
    """Função pura: mapeia dados extraídos para o objeto de resultado sem tocar no disco."""
    nome, _ = categoria
    destino = base_dir / nome / "pratos.json"
    dados_dict = tuple(map(recipe_to_dict, receitas))
    return CategoriaResultado(nome=nome, destino=destino, receitas_dict=dados_dict)

def filtrar_categorias(
    filtro: str | None,
    categorias: tuple[tuple[str, str], ...]
) -> tuple[tuple[str, str], ...]:
    """Função pura: filtra a tupla de categorias."""
    if not filtro:
        return categorias
    return tuple(filter(lambda cat: filtro.lower() in cat[0].lower(), categorias))

# --- CASCA DE EFEITOS COLATERAIS (I/O ISOLADO) ---

def efetuar_persistencia(resultado: CategoriaResultado) -> int:
    """Função impura de I/O: isola a gravação no disco."""
    resultado.destino.parent.mkdir(parents=True, exist_ok=True)
    with open(resultado.destino, "w", encoding="utf-8") as f:
        json.dump(list(resultado.receitas_dict), f, ensure_ascii=False, indent=2)
    return len(resultado.receitas_dict)

def main() -> None:
    filtro_categoria = sys.argv[1].strip() if len(sys.argv) > 1 else None
    cats_para_processar = filtrar_categorias(filtro_categoria, CATEGORIAS_TUDOGOSTOSO)

    if not cats_para_processar:
        print(f"Categoria '{filtro_categoria}' não encontrada.")
        return

    # Processamento e E/S encadeados explicitamente na borda do sistema
    def processar_e_salvar(cat: tuple[str, str]) -> tuple[str, int]:
        nome, url = cat
        urls = obter_urls_recomendadas_categoria(url, limite=15)
        receitas = extrair_all(urls) if urls else ()
        resultado_puro = mapear_categoria_para_resultado(cat, receitas, DATA_DIR)
        qtd = efetuar_persistencia(resultado_puro)
        return (nome, qtd)

    resumo = dict(map(processar_e_salvar, cats_para_processar))
    
    # Exibição declarativa usando join em vez de loop for imperativo
    linhas_resumo = "\n".join(map(lambda item: f"  • {item[0]}: {item[1]} receitas", resumo.items()))
    print(f"\n============================================================\n{linhas_resumo}\n============================================================")

if __name__ == "__main__":
    main()