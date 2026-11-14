"""
Interface de Linha de Comando Declarativa (interface/cli.py)
Ponto de entrada interativo para consulta de refeições viáveis.
Implementado integralmente com funções lambda e encadeamento funcional,
sem utilizar a instrução imperativa de definição.
"""

from implementation.models import UserPreferences
from implementation.graph import build_recipe_graph
from implementation.pipeline import run_recommendation, obter_pratos_bloqueados
from interface.io_adapter import carregar_pratos, DEFAULT_DATA_DIR
from interface.formatter import formatar_relatorio_completo

# Converte texto delimitado por vírgula em conjunto imutável de strings limpas
parse_input_set = lambda text: frozenset(
    filter(
        lambda s: len(s) > 0,
        map(str.strip, map(str.lower, text.split(","))),
    )
)

# Converte string numérica em inteiro ou retorna valor padrão de fallback
parse_int = lambda text, default=0: (
    int(text.strip()) if text.strip().isdigit() else default
)

# Processa a consulta do usuário contra os pratos carregados e retorna o relatório
executar_consulta = lambda pratos, despensa_raw, alergenos_raw, tol_raw, cat_raw: (
    (lambda grafo, prefs: formatar_relatorio_completo(
        run_recommendation(grafo, prefs),
        obter_pratos_bloqueados(grafo, prefs.allergens, prefs.category_filter),
        prefs,
    ))(
        build_recipe_graph(pratos),
        UserPreferences(
            pantry=parse_input_set(despensa_raw),
            allergens=parse_input_set(alergenos_raw),
            max_missing=parse_int(tol_raw, 0),
            category_filter=cat_raw.strip() or None,
        ),
    )
)

# Fluxo interativo no console: solicita entradas do usuário e imprime os resultados
executar_interativo = lambda pratos: (
    print("\n" + "=" * 80),
    print("🍳 COOK WHAT U HAVE — SISTEMA FUNCIONAL DE RECOMENDAÇÃO DE REFEIÇÕES"),
    print("=" * 80),
    print(f"Base de dados: {len(pratos)} pratos carregados em memória."),
    (lambda d_raw, a_raw, t_raw, c_raw: (
        print("\nProcessando cruzamento no Grafo Bipartido..."),
        print(executar_consulta(pratos, d_raw, a_raw, t_raw, c_raw)),
    ))(
        input("\n1. Ingredientes na sua despensa (separados por vírgula): "),
        input("2. Alérgenos a banir com tolerância zero (ou Enter para nenhum): "),
        input("3. Quantidade máxima de ingredientes em falta aceitável (padrão 0): "),
        input("4. Categoria culinária (ou Enter para buscar em todas as 8): "),
    ),
)

# Ponto de entrada do módulo
iniciar_aplicacao = lambda base_dir=DEFAULT_DATA_DIR: (
    executar_interativo(carregar_pratos(base_dir))
)

if __name__ == "__main__":
    iniciar_aplicacao()
