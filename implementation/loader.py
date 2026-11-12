"""
Carregador Funcional de Pratos (implementation/loader.py)
Transforma registros de dicionários em entidades imutáveis Dish.
Implementado integralmente com funções lambda e mapeamentos de ordem superior.
"""

import hashlib
from implementation.models import Dish

# Gera um ID único refinado combinando o ID base com o hash dos ingredientes centrais
gerar_id_dish = lambda d: (
    f"{d['id']}_{hashlib.sha256(' '.join(sorted(d.get('ingredientes_centrais', ()))).encode('utf-8')).hexdigest()[:4]}"
)

# Projeta um dicionário com os campos de pratos.json em uma instância imutável Dish
dict_to_dish = lambda d: Dish(
    id=gerar_id_dish(d),
    name=d["titulo"],
    category=d["tipo"],
    recipe=tuple(d.get("receita", ())),
    raw_ingredients=tuple(d.get("ingredientes_originais", ())),
    clean_ingredients=frozenset(d.get("ingredientes_centrais", ())),
)

# Converte uma coleção imutável de dicionários em uma tupla imutável de Dish
load_dishes_from_records = lambda records: tuple(map(dict_to_dish, records))
