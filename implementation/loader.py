"""
Carregador Funcional de Pratos (implementation/loader.py)
Transforma registros de dicionários em entidades imutáveis Dish.
Implementado integralmente com funções lambda e mapeamentos de ordem superior.
"""

from implementation.models import Dish

# Projeta um dicionário com os campos de pratos.json em uma instância imutável Dish
dict_to_dish = lambda d: Dish(
    id=d["id"],
    name=d["titulo"],
    category=d["tipo"],
    recipe=tuple(d.get("receita", ())),
    raw_ingredients=tuple(d.get("ingredientes_originais", ())),
    clean_ingredients=frozenset(d.get("ingredientes_centrais", ())),
)

# Converte uma coleção imutável de dicionários em uma tupla imutável de Dish
load_dishes_from_records = lambda records: tuple(map(dict_to_dish, records))
