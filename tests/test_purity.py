"""
Suíte de testes de Pureza e Determinismo Funcional.

Garante que as funções do motor (engine) não possuem efeitos colaterais,
são puramente determinísticas (mesma entrada -> mesma saída) e preservam o estado dos argumentos.
"""

from implementation.engine import (
    calculate_match,
    ingrediente_coberto,
    is_within_tolerance,
    matches_category,
    obter_ingredientes_disponiveis,
)
from implementation.models import Dish, MatchResult


def criar_prato_exemplo(id_: str = "p1", ingredientes: tuple[str, ...] = ("tomate", "alho", "azeite")) -> Dish:
    return Dish(
        id=id_,
        name="Molho Rápido",
        category="molhos",
        recipe=("Picar alho", "Refogar no azeite", "Adicionar tomate"),
        raw_ingredients=tuple(f"1 unidade de {i}" for i in ingredientes),
        clean_ingredients=frozenset(ingredientes),
    )


def test_calculate_match_purity_and_determinism() -> None:
    """Verifica que calculate_match sempre produz resultados idênticos sem alterar as entradas."""
    prato = criar_prato_exemplo()
    despensa = frozenset({"tomate", "azeite"})

    resultado1 = calculate_match(prato, despensa)
    resultado2 = calculate_match(prato, despensa)

    assert resultado1 == resultado2
    assert resultado1.available_ingredients == frozenset({"tomate", "azeite"})
    assert resultado1.missing_ingredients == frozenset({"alho"})
    assert resultado1.match_percentage == 66.67

    # Entradas não sofreram mutação
    assert prato.clean_ingredients == frozenset({"tomate", "alho", "azeite"})
    assert despensa == frozenset({"tomate", "azeite"})


def test_calculate_match_empty_dish() -> None:
    """Prato sem ingredientes limpos deve ter score zero e coleções vazias."""
    prato_vazio = Dish(
        id="vazio",
        name="Prato Vazio",
        category="geral",
        recipe=(),
        raw_ingredients=(),
        clean_ingredients=frozenset(),
    )
    resultado = calculate_match(prato_vazio, frozenset({"sal"}))
    assert resultado.match_percentage == 0.0
    assert len(resultado.available_ingredients) == 0
    assert len(resultado.missing_ingredients) == 0


def test_calculate_match_with_flexible_substrings() -> None:
    """Testa se calculate_match emprega ingrediente_coberto para despensas com termos compostos."""
    prato = criar_prato_exemplo(ingredientes=("farinha de trigo", "leite integral"))
    despensa = frozenset({"trigo", "leite"})

    resultado = calculate_match(prato, despensa)
    assert resultado.match_percentage == 100.0
    assert resultado.available_ingredients == frozenset({"farinha de trigo", "leite integral"})
    assert len(resultado.missing_ingredients) == 0


def test_ingrediente_coberto_logic() -> None:
    """Valida as regras de contenção e equivalência semântica de ingrediente_coberto."""
    despensa = frozenset({"leite", "azeite extra virgem", "cebola"})

    assert ingrediente_coberto("leite integral", despensa) is True
    assert ingrediente_coberto("creme de leite", despensa) is True
    assert ingrediente_coberto("azeite", despensa) is True
    assert ingrediente_coberto("cebola picada", despensa) is True
    assert ingrediente_coberto("camarao", despensa) is False
    assert ingrediente_coberto("pimenta do reino", despensa) is False


def test_is_within_tolerance_boundaries() -> None:
    """Verifica os limites de tolerância para ingredientes faltantes."""
    prato = criar_prato_exemplo()
    res_faltando_1 = MatchResult(
        dish=prato,
        match_percentage=66.67,
        available_ingredients=frozenset({"tomate", "alho"}),
        missing_ingredients=frozenset({"azeite"}),
    )

    assert is_within_tolerance(res_faltando_1, 1) is True
    assert is_within_tolerance(res_faltando_1, 2) is True
    assert is_within_tolerance(res_faltando_1, 0) is False
    assert is_within_tolerance(res_faltando_1, -1) is False


def test_matches_category_purity() -> None:
    """Verifica filtros de categoria sem distinção entre maiúsculas/minúsculas e busca ampla."""
    prato_carnes = Dish("1", "Picanha", "carnes", (), (), frozenset())
    prato_aves = Dish("2", "Frango", "aves", (), (), frozenset())

    # Categoria vazia ou None permite todas
    assert matches_category(prato_carnes, "") is True
    assert matches_category(prato_carnes, None) is True  # type: ignore[arg-type]

    # Busca exata ou substring insensível
    assert matches_category(prato_carnes, "carnes") is True
    assert matches_category(prato_carnes, "CARNES") is True
    assert matches_category(prato_carnes, "carne") is True
    assert matches_category(prato_carnes, "aves") is False
    assert matches_category(prato_aves, "aves") is True


def test_obter_ingredientes_disponiveis() -> None:
    """Verifica extração imutável de ingredientes presentes em um prato com base na despensa."""
    ingredientes = frozenset({"arroz", "feijao", "alho", "sal"})
    despensa = frozenset({"arroz", "alho", "azeite"})

    disponiveis = obter_ingredientes_disponiveis(ingredientes, despensa)
    assert disponiveis == frozenset({"arroz", "alho"})
    assert isinstance(disponiveis, frozenset)
