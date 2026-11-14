"""
Pacote de Interface e Adaptadores de E/S (interface/__init__.py)
Exporta carregador de pratos, formatador de relatórios e ponto de entrada da CLI.
"""

from interface.io_adapter import carregar_pratos
from interface.formatter import formatar_relatorio_completo
from interface.cli import parse_input_set, parse_int, executar_consulta, iniciar_aplicacao

__all__ = (
    "carregar_pratos",
    "formatar_relatorio_completo",
    "parse_input_set",
    "parse_int",
    "executar_consulta",
    "iniciar_aplicacao",
)
