"""
Pacote de Interface e Adaptadores de E/S (interface/__init__.py)
Exporta carregador de pratos, formatador de relatórios e ponto de entrada da CLI.
"""

from interface.cli import executar_consulta, iniciar_aplicacao, parse_input_set, parse_int
from interface.formatter import formatar_relatorio_completo
from interface.io_adapter import carregar_pratos

__all__ = (
    "carregar_pratos",
    "executar_consulta",
    "formatar_relatorio_completo",
    "iniciar_aplicacao",
    "parse_input_set",
    "parse_int",
)
