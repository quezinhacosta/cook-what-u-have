#logica da analise de pratos
#deduzido apartir da teoria dos conjuntos

from ingestion.data.aves import pratos 
from functools import partial


def allergens()


def calcule_match(dish: Dish, pantry: frozenset[str]) -> MatchResult: #recebe o que tem na dispensa e o prato
    return dish.ingredients.isdisjoint(allergens)

