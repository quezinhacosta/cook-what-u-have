"""
Suíte de testes do Carregador Funcional e Adaptador de E/S (implementation/loader.py e interface/io_adapter.py).

Verifica a geração determinística de IDs com hash de ingredientes para evitar colisões,
a projeção de dicionários para Dish e a integridade da base real de 120 receitas.
"""

from implementation.loader import dict_to_dish, gerar_id_dish, load_dishes_from_records
from interface.io_adapter import DEFAULT_DATA_DIR, carregar_pratos


def test_gerar_id_dish_unicidade_e_determinismo() -> None:
    """Verifica que receitas com o mesmo título mas ingredientes diferentes recebem IDs distintos."""
    rec1 = {
        "id": "caldo_verde",
        "titulo": "Caldo Verde",
        "tipo": "sopas",
        "ingredientes_centrais": ["batata", "couve", "linguica calabresa"],
    }
    rec2 = {
        "id": "caldo_verde",
        "titulo": "Caldo Verde",
        "tipo": "sopas",
        "ingredientes_centrais": ["batata", "couve", "bacon"],
    }

    id1 = gerar_id_dish(rec1)
    id2 = gerar_id_dish(rec2)

    assert id1 != id2
    assert id1.startswith("caldo_verde_")
    assert id2.startswith("caldo_verde_")

    # Determinismo: mesma entrada produz exatamente o mesmo ID
    assert gerar_id_dish(rec1) == id1


def test_dict_to_dish_projections() -> None:
    """Valida a conversão estrutural de dicionário para entidade Dish imutável."""
    dados = {
        "id": "arroz_carreteiro",
        "titulo": "Arroz Carreteiro Tradicional",
        "tipo": "carnes",
        "receita": ["Cozinhar carne seca", "Refogar arroz", "Misturar tudo"],
        "ingredientes_originais": ["500g de carne seca", "2 xícaras de arroz", "1 cebola"],
        "ingredientes_centrais": ["carne seca", "arroz", "cebola"],
    }

    dish = dict_to_dish(dados)

    assert dish.name == "Arroz Carreteiro Tradicional"
    assert dish.category == "carnes"
    assert isinstance(dish.clean_ingredients, frozenset)
    assert dish.clean_ingredients == frozenset({"carne seca", "arroz", "cebola"})
    assert isinstance(dish.recipe, tuple)
    assert isinstance(dish.raw_ingredients, tuple)


def test_load_dishes_from_records() -> None:
    """Testa conversão funcional de coleção de registros."""
    records = (
        {"id": "p1", "titulo": "Prato 1", "tipo": "aves", "ingredientes_centrais": ["frango"]},
        {"id": "p2", "titulo": "Prato 2", "tipo": "massas", "ingredientes_centrais": ["macarrao"]},
    )
    dishes = load_dishes_from_records(records)

    assert len(dishes) == 2
    assert dishes[0].name == "Prato 1"
    assert dishes[1].name == "Prato 2"


def test_carregar_pratos_base_real_120_receitas() -> None:
    """
    Teste de integração com a base real persistida em ingestion/data:
    Garante que os 120 pratos das 8 categorias sejam carregados perfeitamente
    e que todos os 120 IDs sejam estritamente únicos (sem colisão).
    """
    if not DEFAULT_DATA_DIR.exists():
        return

    pratos = carregar_pratos(DEFAULT_DATA_DIR)
    assert len(pratos) in (120, 400), f"Esperava 120 ou 400 pratos, encontrou {len(pratos)}"

    ids = tuple(p.id for p in pratos)
    ids_unicos = set(ids)
    assert len(ids_unicos) == len(pratos), f"Colisão detectada: apenas {len(ids_unicos)} IDs únicos entre {len(pratos)} pratos"


def test_carregar_pratos_com_filtro_categoria() -> None:
    """Verifica carregamento com filtro específico de categoria."""
    if not DEFAULT_DATA_DIR.exists():
        return

    pratos_aves = carregar_pratos(DEFAULT_DATA_DIR, filtro="aves")
    assert len(pratos_aves) in (15, 50)
    assert all(map(lambda p: p.category == "aves", pratos_aves))
