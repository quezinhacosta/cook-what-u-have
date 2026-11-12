"""
Módulo de Modelos de Dados Imutáveis (ingestion/models.py)
Define as entidades de domínio e estruturas imutáveis utilizadas
ao longo de todo o pipeline de ingestão e normalização funcional.
"""

from typing import NamedTuple, Any
from pathlib import Path


class RawRecipe(NamedTuple):
    """
    Representação imutável dos dados brutos extraídos diretamente do HTML.
    Mantém as informações originais antes de qualquer higienização profunda.
    """
    titulo: str
    tipo: str
    receita: tuple[str, ...]
    ingredientes_originais: tuple[str, ...]
    url: str


class ProcessedRecipe(NamedTuple):
    """
    Entidade de receita processada e padronizada para persistência e grafo:
    - id: identificador determinístico único (slug/hash baseado em título e tipo)
    - titulo: título sanitizado
    - tipo: categoria canônica da receita (ex: 'massas', 'aves', etc.)
    - receita: passos ordenados originais intactos do modo de preparo
    - ingredientes_originais: strings brutas do site para exibição ao usuário
    - ingredientes_centrais: tupla ordenada de termos canônicos para álgebra de conjuntos
    """
    id: str
    titulo: str
    tipo: str
    receita: tuple[str, ...]
    ingredientes_originais: tuple[str, ...]
    ingredientes_centrais: tuple[str, ...]


class CategoryTarget(NamedTuple):
    """Mapeamento imutável de uma categoria alvo: nome da pasta e URL de raspagem."""
    nome: str
    url: str


class CategoryResult(NamedTuple):
    """Resultado imutável do processamento de uma categoria pronta para persistência."""
    nome: str
    destino: Path
    receitas: tuple[ProcessedRecipe, ...]


def recipe_to_dict(recipe: ProcessedRecipe) -> dict[str, Any]:
    """Função pura: projeta a entidade imutável ProcessedRecipe em dicionário para JSON."""
    return {
        "id": recipe.id,
        "titulo": recipe.titulo,
        "tipo": recipe.tipo,
        "receita": list(recipe.receita),
        "ingredientes_originais": list(recipe.ingredientes_originais),
        "ingredientes_centrais": list(recipe.ingredientes_centrais),
    }
