#classes imutaveis

from dataclasses import dataclass

@dataclass(frozen=True)
class Dish:
    """Entidade imutável que representa um prato cadastrado."""
    id: str
    name: str
    category: str
    ingredients: frozenset[str]
    recipe: str

@dataclass(frozen=True)
class UserPreferences:
    """Entrada imutável com preferências do usuário."""
    pantry: frozenset[str] #o que tem disponivel na dispensa
    allergens: frozenset[str]
    max_missing_threshold: int = 0

@dataclass(frozen=True)
class MatchResult:
    """Projeção analítica do resultado de correspondência de um prato."""
    dish: Dish
    match_percentage: float
    available_ingredients: frozenset[str]
    missing_ingredients: frozenset[str]