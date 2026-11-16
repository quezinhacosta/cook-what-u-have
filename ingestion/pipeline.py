"""
Pipeline Orquestrador de Ingestão de Dados (ingestion/pipeline.py)
Responsabilidade: Orquestrar o fluxo funcional conectando as bordas de I/O
(rede e disco via io_gateway) com o núcleo computacional 100% puro
(parser.py e normalizer.py), mapeando receitas recomendadas para as
categorias do TudoGostoso e gerando pratos.json padronizados.
"""

import sys
from collections.abc import Callable
from pathlib import Path

from ingestion.io_gateway import baixar_html, salvar_categoria_json
from ingestion.models import CategoryResult, CategoryTarget
from ingestion.normalizer import processar_receita
from ingestion.parser import (
    deduplicar_preservando_ordem,
    extrair_links_categoria_html,
    extrair_receita_html,
    gerar_url_pagina,
)

# Diretório base de persistência dos dados: ingestion/data/
DATA_DIR: Path = Path(__file__).parent / "data"

# Mapeamento imutável das 8 categorias oficiais do TudoGostoso
CATEGORIAS_PADRAO: tuple[CategoryTarget, ...] = (
    CategoryTarget("aves", "https://www.tudogostoso.com.br/categorias/1009-aves"),
    CategoryTarget("bolos e tortas", "https://www.tudogostoso.com.br/categorias/1000-bolos-e-tortas-doces"),
    CategoryTarget("carnes", "https://www.tudogostoso.com.br/categorias/1004-carnes"),
    CategoryTarget("doces e sobremesas", "https://www.tudogostoso.com.br/categorias/1037-doces-e-sobremesas"),
    CategoryTarget("massas", "https://www.tudogostoso.com.br/categorias/1028-massas"),
    CategoryTarget("peixes e frutos do mar", "https://www.tudogostoso.com.br/categorias/1014-peixes-e-frutos-do-mar"),
    CategoryTarget("saladas e molhos", "https://www.tudogostoso.com.br/categorias/1023-saladas-molhos-e-acompanhamentos"),
    CategoryTarget("sopas", "https://www.tudogostoso.com.br/categorias/1027-sopas"),
)

# ==============================================================================
# FUNÇÕES PURAS DE FILTRAGEM E FORMATAÇÃO
# ==============================================================================

filtrar_alvos_por_nome = lambda alvos, filtro: (
    tuple(filter(lambda alvo: filtro.strip().lower() in alvo.nome.lower(), alvos))
    if filtro
    else alvos
)

formatar_linha_resumo = lambda resultado: (
    f"  - {resultado.nome:<22}: {len(resultado.receitas):>2} receitas salvas em {resultado.destino.name}"
)

# ==============================================================================
# ORQUESTRAÇÃO FUNCIONAL DO PIPELINE
# ==============================================================================

extrair_e_processar_url = lambda url, categoria: (
    (
        lambda html: (
            (
                lambda raw_recipe: processar_receita(raw_recipe, categoria_alvo=categoria)
                if raw_recipe
                else None
            )(extrair_receita_html(html, url, tipo_padrao=categoria))
            if html
            else None
        )
    )(baixar_html(url))
)

coletar_urls_categoria: Callable[..., tuple[str, ...]] = (
    lambda base_url, limite=50, pagina_atual=1, acumuladas=(), max_paginas=6: (
        acumuladas[:limite]
        if len(acumuladas) >= limite or pagina_atual > max_paginas
        else (
            (
                lambda html: (
                    acumuladas[:limite]
                    if not html
                    else (
                        (
                            lambda links_pagina: (
                                acumuladas[:limite]
                                if not links_pagina
                                else (
                                    (
                                        lambda combinados: (
                                            combinados[:limite]
                                            if len(combinados) == len(acumuladas)
                                            else coletar_urls_categoria(
                                                base_url,
                                                limite=limite,
                                                pagina_atual=pagina_atual + 1,
                                                acumuladas=combinados,
                                                max_paginas=max_paginas,
                                            )
                                        )
                                    )(deduplicar_preservando_ordem(acumuladas + links_pagina))
                                )
                            )
                        )(extrair_links_categoria_html(html, limite=limite))
                    )
                )
            )(baixar_html(gerar_url_pagina(base_url, pagina_atual)))
        )
    )
)

processar_categoria = lambda alvo, base_dir, limite=50: (
    (
        lambda destino: (
            print(f"\n[CATEGORIA: {alvo.nome.upper()}] Buscando ate {limite} receitas recomendadas..."),
            (
                lambda urls_recomendadas: (
                    (
                        print(f"   [AVISO] Nenhuma URL encontrada para a categoria '{alvo.nome}'."),
                        (lambda r_vazio: (salvar_categoria_json(r_vazio), r_vazio)[-1])(
                            CategoryResult(nome=alvo.nome, destino=destino, receitas=())
                        ),
                    )[-1]
                    if not urls_recomendadas
                    else (
                        print(f"   -> {len(urls_recomendadas)} URLs encontradas. Extraindo e normalizando..."),
                        (
                            lambda validas: (
                                (
                                    lambda res: (
                                        print(
                                            f"   [OK] {salvar_categoria_json(res)} receitas salvas em: {destino}"
                                        ),
                                        res,
                                    )[-1]
                                )(CategoryResult(nome=alvo.nome, destino=destino, receitas=validas))
                            )
                        )(
                            tuple(
                                r
                                for u in urls_recomendadas
                                if (r := extrair_e_processar_url(u, alvo.nome)) is not None
                            )
                        ),
                    )[-1]
                )
            )(coletar_urls_categoria(alvo.url, limite=limite)),
        )[-1]
    )(base_dir / alvo.nome / "pratos.json")
)

executar_pipeline = lambda alvos=CATEGORIAS_PADRAO, base_dir=DATA_DIR, limite_por_categoria=50: (
    print(f"[PIPELINE] Iniciando Ingestao Funcional (limite: {limite_por_categoria} receitas/categoria)..."),
    print(f"Categorias selecionadas: {list(map(lambda a: a.nome, alvos))}"),
    (
        lambda resultados: (
            print("\n" + "=" * 70),
            print("[SUCESSO] Pipeline de Ingestao Concluido!"),
            print(f"Total geral de receitas padronizadas: {sum(map(lambda res: len(res.receitas), resultados))}"),
            print("\n".join(map(formatar_linha_resumo, resultados))),
            print("=" * 70),
            resultados,
        )[-1]
    )(tuple(map(lambda alvo: processar_categoria(alvo, base_dir, limite=limite_por_categoria), alvos))),
)[-1]

_obter_limite_cli = lambda: (
    int(sys.argv[2])
    if len(sys.argv) > 2 and sys.argv[2].isdigit()
    else int(sys.argv[1])
    if len(sys.argv) > 1 and sys.argv[1].isdigit()
    else 50
)

_obter_filtro_cli = lambda: (
    sys.argv[1].strip()
    if len(sys.argv) > 1 and not sys.argv[1].isdigit()
    else None
)

main = lambda: (
    (
        lambda alvos: (
            (
                print(f"[ERRO] Nenhuma categoria encontrada correspondente ao filtro: '{_obter_filtro_cli()}'"),
                print(f"Categorias disponiveis: {list(map(lambda a: a.nome, CATEGORIAS_PADRAO))}"),
                sys.exit(1),
            )
            if not alvos
            else executar_pipeline(alvos=alvos, limite_por_categoria=_obter_limite_cli())
        )
    )(filtrar_alvos_por_nome(CATEGORIAS_PADRAO, _obter_filtro_cli()))
)

if __name__ == "__main__":
    main()
