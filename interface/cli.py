"""
Interface de Linha de Comando Declarativa (interface/cli.py)
Ponto de entrada interativo para consulta de refeições viáveis.
Implementado integralmente com funções lambda e encadeamento funcional,
sem utilizar a instrução imperativa de definição.
"""

from implementation.graph import build_recipe_graph
from implementation.models import UserPreferences
from implementation.pipeline import obter_pratos_bloqueados, run_recommendation
from interface.formatter import (
    CATEGORIAS_DISPONIVEIS,
    formatar_detalhes_receita,
    formatar_menu_categorias,
    formatar_relatorio_completo,
)
from interface.io_adapter import DEFAULT_DATA_DIR, carregar_pratos

# Converte texto delimitado por vírgula em conjunto imutável de strings limpas
parse_input_set = lambda text: frozenset(
    filter(
        lambda s: len(s) > 0,
        map(str.strip, map(str.lower, text.split(","))),
    )
)

# Converte a entrada de categoria do usuário (numérica ou textual) na categoria canônica
resolver_categoria_input = lambda text, categorias=CATEGORIAS_DISPONIVEIS: (
    (lambda s: (
        None if not s or s == "0" or s in ("todas", "todos") else
        categorias[int(s) - 1] if s.isdigit() and 1 <= int(s) <= len(categorias) else
        s
    ))(text.strip().lower())
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
            category_filter=resolver_categoria_input(cat_raw),
        ),
    )
)

# Conduz a navegação interativa entre a lista de sugestões e a inspeção detalhada de receitas
loop_navegacao_pratos = lambda resultados, relatorio, reiniciar_busca: (
    print(relatorio),
    (
        print("\n[INFO] Nenhuma sugestao disponivel para detalhar.")
        if not resultados else
        (lambda loop_detalhe: loop_detalhe(loop_detalhe))(
            lambda self_detalhe: (
                (lambda opcao: (
                    (lambda num: (
                        (
                            print(formatar_detalhes_receita(resultados[num - 1])),
                            (lambda loop_pos_receita: loop_pos_receita(loop_pos_receita))(
                                lambda self_pos: (
                                    (lambda escolha: (
                                        (print("\n" + relatorio), self_detalhe(self_detalhe))
                                        if escolha in ("v", "voltar", "1") else
                                        reiniciar_busca()
                                        if escolha in ("n", "nova", "2") else
                                        print("\nObrigado por usar o Cook What U Have! Bom apetite!\n")
                                        if escolha in ("s", "sair", "q", "3") else
                                        (
                                            print("[AVISO] Opcao invalida. Digite [V] para voltar, [N] para nova consulta ou [S] para sair."),
                                            self_pos(self_pos),
                                        )
                                    ))(input("\nEscolha: [V] Voltar para as sugestões | [N] Nova consulta | [S] Sair: ").strip().lower())
                                )
                            ),
                        )
                        if 1 <= num <= len(resultados) else
                        (
                            print(f"[AVISO] Numero invalido. Escolha um prato entre 1 e {len(resultados)}."),
                            self_detalhe(self_detalhe),
                        )
                    ))(int(opcao))
                    if opcao.isdigit() else
                    reiniciar_busca()
                    if opcao in ("n", "nova") else
                    print("\nObrigado por usar o Cook What U Have! Bom apetite!\n")
                    if opcao in ("s", "sair", "q") else
                    (
                        print(f"[AVISO] Entrada nao reconhecida. Digite o numero do prato (1 a {len(resultados)}), 'n' para nova consulta ou 's' para sair."),
                        self_detalhe(self_detalhe),
                    )
                ))(input(f"\nDigite o numero do prato para ver o modo de preparo (1-{len(resultados)}) ou [N] Nova consulta / [S] Sair: ").strip().lower())
            )
        )
    )
)

# Conduz a sessão interativa completa com suporte a reinício de busca puramente recursivo
executar_sessao = lambda pratos: (
    (lambda loop_sessao: loop_sessao(loop_sessao))(
        lambda self_sessao: (
            print("\n" + "=" * 80),
            print("COOK WHAT U HAVE — SISTEMA FUNCIONAL DE RECOMENDACAO DE REFEICOES"),
            print("=" * 80),
            print(f"Base de dados: {len(pratos)} pratos carregados em memória.\n"),
            print(formatar_menu_categorias()),
            (lambda d_raw: (
                (
                    print("\n[AVISO] A despensa precisa conter pelo menos 2 ingredientes para gerar recomendações viáveis.\n"),
                    self_sessao(self_sessao),
                )
                if len(parse_input_set(d_raw)) < 2 else
                (lambda a_raw, t_raw, c_raw: (
                    print("\nProcessando cruzamento no Grafo Bipartido..."),
                    (lambda grafo, prefs: (
                        (lambda resultados, bloqueados: (
                            loop_navegacao_pratos(
                                resultados,
                                formatar_relatorio_completo(resultados, bloqueados, prefs),
                                lambda: self_sessao(self_sessao),
                            )
                        ))(
                            run_recommendation(grafo, prefs),
                            obter_pratos_bloqueados(grafo, prefs.allergens, prefs.category_filter),
                        )
                    ))(
                        build_recipe_graph(pratos),
                        UserPreferences(
                            pantry=parse_input_set(d_raw),
                            allergens=parse_input_set(a_raw),
                            max_missing=parse_int(t_raw, 0),
                            category_filter=resolver_categoria_input(c_raw),
                            min_matched=2,
                        ),
                    ),
                ))(
                    input("\n2. Alérgenos a banir com tolerância zero (ou Enter para nenhum): "),
                    input("\n3. Quantidade máxima de ingredientes em falta aceitável (padrão 0): "),
                    input("\n4. Escolha a categoria culinária [0-8 ou nome] (Enter para todas): "),
                )
            ))(
                input("\n1. Ingredientes na sua despensa (pelo menos 2, separados por vírgula): "),
            ),
        )
    )
)

# Fluxo interativo no console
executar_interativo = lambda pratos: executar_sessao(pratos)

# Ponto de entrada do módulo
iniciar_aplicacao = lambda base_dir=DEFAULT_DATA_DIR: (
    executar_sessao(carregar_pratos(base_dir))
)

if __name__ == "__main__":
    iniciar_aplicacao()
