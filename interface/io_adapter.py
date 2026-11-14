"""
Adaptador de E/S para Carga de Pratos (interface/io_adapter.py)
Responsabilidade: Efetuar a leitura do disco dos arquivos pratos.json
gerados na ingestão e projetar em instâncias imutáveis Dish.
Desenvolvido estritamente com lambdas e composição funcional.
"""

import json
from pathlib import Path
from implementation.models import Dish
from implementation.loader import load_dishes_from_records

# Diretório padrão onde repousam as 8 categorias de pratos
DEFAULT_DATA_DIR: Path = Path(__file__).parent.parent / "ingestion" / "data"

# Lê de forma segura o conteúdo de um arquivo JSON do disco
ler_json_seguro = lambda caminho_arquivo: (
    json.loads(caminho_arquivo.read_text(encoding="utf-8")) if caminho_arquivo.exists() else []
)

# Filtra as subpastas válidas do diretório de dados respeitando filtro opcional de categoria
obter_subpastas_validas = lambda base_dir, filtro=None: tuple(
    filter(
        lambda d: d.is_dir() and not d.name.startswith(".") and (not filtro or filtro.lower() in d.name.lower()),
        sorted(base_dir.iterdir()),
    )
)

# Concatena os registros brutos de todas as categorias selecionadas em uma tupla imutável
carregar_registros_categorias = lambda base_dir, filtro=None: tuple(
    registro
    for subpasta in obter_subpastas_validas(base_dir, filtro)
    for registro in ler_json_seguro(subpasta / "pratos.json")
)

# Função principal de carregamento que entrega os pratos prontos para o motor do grafo
carregar_pratos = lambda base_dir=DEFAULT_DATA_DIR, filtro=None: load_dishes_from_records(
    carregar_registros_categorias(base_dir, filtro)
)
