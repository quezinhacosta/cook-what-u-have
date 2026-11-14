"""
Pacote de Interface e Adaptadores de E/S (interface/__init__.py)
Exporta carregador de pratos, formatador de relatórios e ponto de entrada da CLI.
"""

from interface.cli import (
    executar_consulta,
    executar_sessao,
    iniciar_aplicacao,
    loop_navegacao_pratos,
    parse_input_set,
    parse_int,
    resolver_categoria_input,
)
from interface.formatter import (
    CATEGORIAS_DISPONIVEIS,
    formatar_detalhes_receita,
    formatar_menu_categorias,
    formatar_relatorio_completo,
)
from interface.io_adapter import carregar_pratos

__all__ = (
    "CATEGORIAS_DISPONIVEIS",
    "carregar_pratos",
    "executar_consulta",
    "executar_sessao",
    "formatar_detalhes_receita",
    "formatar_menu_categorias",
    "formatar_relatorio_completo",
    "iniciar_aplicacao",
    "loop_navegacao_pratos",
    "parse_input_set",
    "parse_int",
    "resolver_categoria_input",
)
