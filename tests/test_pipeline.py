"""
Suíte de testes de Integração e Orquestração do Pipeline (implementation/pipeline.py).

Verifica a composição pura das etapas de recomendação:
poda de alérgenos -> filtro de categoria -> cálculo de cobertura -> corte por tolerância -> ordenação multicritério.
"""

from implementation.graph import build_recipe_graph
from implementation.models import Dish, UserPreferences
from implementation.pipeline import criterio_ordenacao, obter_pratos_bloqueados, run_recommendation


def criar_cenario_pipeline() -> any:  # type: ignore[valid-type]
    d1 = Dish(
        id="d1",
        name="Arroz com Alho",
        category="acompanhamentos",
        recipe=("Refogar alho", "Cozinhar arroz"),
        raw_ingredients=("arroz", "alho", "óleo"),
        clean_ingredients=frozenset({"arroz", "alho", "oleo"}),
    )
    d2 = Dish(
        id="d2",
        name="Arroz com Frango",
        category="aves",
        recipe=("Refogar frango", "Adicionar arroz"),
        raw_ingredients=("arroz", "frango", "alho", "cebola"),
        clean_ingredients=frozenset({"arroz", "frango", "alho", "cebola"}),
    )
    d3 = Dish(
        id="d3",
        name="Moqueca de Camarão",
        category="peixes",
        recipe=("Cozinhar camarão no leite de coco",),
        raw_ingredients=("camarão fresco", "leite de coco", "dendê"),
        clean_ingredients=frozenset({"camarao", "leite de coco", "azeite de dende"}),
    )
    d4 = Dish(
        id="d4",
        name="Batata com Alho",
        category="acompanhamentos",
        recipe=("Assar batatas com alho",),
        raw_ingredients=("batata", "alho"),
        clean_ingredients=frozenset({"batata", "alho"}),
    )
    return build_recipe_graph((d1, d2, d3, d4))


def test_run_recommendation_ordenacao_multicriterio() -> None:
    """
    Testa a ordenação determinística de 3 critérios:
    1. Maior percentual de cobertura descrescente
    2. Menor número de ingredientes faltantes crescente
    3. Nome em ordem alfabética
    """
    grafo = criar_cenario_pipeline()
    # Despensa possui arroz, alho e batata.
    # d4 (Batata com Alho, clean={'batata', 'alho'}): cobertura 100% (2/2), faltando 0
    # d1 (Arroz com Alho, clean={'arroz', 'alho', 'oleo'}): cobertura 66.67% (2/3), faltando 1
    # d2 (Arroz com Frango, clean={'arroz', 'frango', 'alho', 'cebola'}): cobertura 50% (2/4), faltando 2
    # d3 possui camarao, mas despensa nao tem.
    prefs = UserPreferences(
        pantry=frozenset({"arroz", "alho", "batata"}),
        allergens=frozenset(),
        max_missing=2,
        category_filter=None,
    )

    resultados = run_recommendation(grafo, prefs)

    assert len(resultados) == 3
    # 1º lugar: Batata com Alho (100%)
    assert resultados[0].dish.name == "Batata com Alho"
    assert resultados[0].match_percentage == 100.0

    # 2º lugar: Arroz com Alho (66.67%)
    assert resultados[1].dish.name == "Arroz com Alho"
    assert resultados[1].match_percentage == 66.67

    # 3º lugar: Arroz com Frango (50.0%)
    assert resultados[2].dish.name == "Arroz com Frango"
    assert resultados[2].match_percentage == 50.0


def test_run_recommendation_filtro_categoria() -> None:
    """Verifica restrição dos resultados à categoria especificada pelo usuário."""
    grafo = criar_cenario_pipeline()
    prefs = UserPreferences(
        pantry=frozenset({"arroz", "alho", "batata", "oleo"}),
        allergens=frozenset(),
        max_missing=3,
        category_filter="acompanhamentos",
    )

    resultados = run_recommendation(grafo, prefs)
    assert len(resultados) == 2
    for r in resultados:
        assert r.dish.category == "acompanhamentos"


def test_run_recommendation_exclusao_estrita_alergenos() -> None:
    """Garante que pratos contendo alérgenos são completamente eliminados dos resultados."""
    grafo = criar_cenario_pipeline()
    # Mesmo com despensa completa para Moqueca de Camarão, ela deve ser podada por segurança
    prefs = UserPreferences(
        pantry=frozenset({"camarao", "leite de coco", "azeite de dende", "arroz", "alho", "batata", "oleo"}),
        allergens=frozenset({"camarao"}),
        max_missing=5,
        category_filter=None,
    )

    resultados = run_recommendation(grafo, prefs)
    nomes_recomendados = tuple(r.dish.name for r in resultados)

    assert "Moqueca de Camarão" not in nomes_recomendados
    assert "Arroz com Alho" in nomes_recomendados
    assert "Batata com Alho" in nomes_recomendados


def test_run_recommendation_filtro_tolerancia() -> None:
    """Verifica descarte de receitas quando faltam mais ingredientes do que max_missing permite."""
    grafo = criar_cenario_pipeline()
    # Despensa só tem alho.
    # d4 precisa de 1 faltante (batata)
    # d1 precisa de 2 faltantes (arroz, oleo)
    # d2 precisa de 3 faltantes (arroz, frango, cebola)
    prefs_tol_0 = UserPreferences(pantry=frozenset({"alho"}), allergens=frozenset(), max_missing=0)
    assert len(run_recommendation(grafo, prefs_tol_0)) == 0

    prefs_tol_1 = UserPreferences(pantry=frozenset({"alho"}), allergens=frozenset(), max_missing=1, min_matched=1)
    res_1 = run_recommendation(grafo, prefs_tol_1)
    assert len(res_1) == 1
    assert res_1[0].dish.name == "Batata com Alho"


def test_run_recommendation_descarta_pratos_sem_ingredientes_em_comum() -> None:
    """Garante que pratos com 0 ingredientes em comum nunca são sugeridos, mesmo com alta tolerância."""
    grafo = criar_cenario_pipeline()
    # Despensa possui apenas cenoura e pimentao (nenhum prato do grafo usa ambos)
    prefs = UserPreferences(
        pantry=frozenset({"cenoura", "pimentao"}),
        allergens=frozenset(),
        max_missing=10,  # Alta tolerância
        min_matched=2,
    )
    resultados = run_recommendation(grafo, prefs)
    # Nenhum prato deve ser sugerido pois nenhum possui pelo menos 2 ingredientes da despensa
    assert len(resultados) == 0


def test_obter_pratos_bloqueados_respeita_categoria() -> None:
    """Valida o resgate de pratos bloqueados por alérgenos com ou sem filtro de categoria culinária."""
    grafo = criar_cenario_pipeline()

    # Bloqueio geral
    bloqueados_geral = obter_pratos_bloqueados(grafo, frozenset({"camarao"}))
    assert len(bloqueados_geral) == 1
    assert bloqueados_geral[0].name == "Moqueca de Camarão"

    # Bloqueio filtrando por categoria peixes (onde a moqueca reside)
    bloqueados_peixes = obter_pratos_bloqueados(grafo, frozenset({"camarao"}), category_filter="peixes")
    assert len(bloqueados_peixes) == 1

    # Bloqueio filtrando por categoria aves (onde a moqueca não reside)
    bloqueados_aves = obter_pratos_bloqueados(grafo, frozenset({"camarao"}), category_filter="aves")
    assert len(bloqueados_aves) == 0


def test_criterio_ordenacao_comparador() -> None:
    """Valida a tupla do comparador funcional de ordenação."""
    d = Dish("id", "Abobrinha", "legumes", (), (), frozenset())
    class MockMatch:
        match_percentage = 80.0
        missing_ingredients = frozenset({"sal"})
        dish = d

    crit = criterio_ordenacao(MockMatch)  # type: ignore[arg-type]
    assert crit == (-80.0, 1, "Abobrinha")
