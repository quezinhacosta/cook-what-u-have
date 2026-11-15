import tkinter as tk
import unicodedata
from collections import Counter
from functools import reduce
from itertools import chain
from tkinter import font as tkfont

from implementation.graph import build_recipe_graph
from implementation.models import UserPreferences
from implementation.pipeline import obter_pratos_bloqueados, run_recommendation
from interface.formatter import CATEGORIAS_DISPONIVEIS
from interface.io_adapter import DEFAULT_DATA_DIR, carregar_pratos

FONTE = "Segoe UI"

COR = {
    "fundo": "#33200F",
    "fundo_claro": "#4A2C18",
    "creme": "#FBF3E6",
    "creme_escuro": "#EEE1CC",
    "ambar": "#EFA93F",
    "ambar_claro": "#F7C377",
    "ambar_escuro": "#D98B24",
    "texto": "#2E1B0E",
    "suave": "#A08870",
    "chip": "#E6D8C1",
    "chip_texto": "#6B5741",
    "perigo": "#BC4B28",
    "perigo_bg": "#F6DFD4",
    "branco": "#FFFFFF",
}

# Quantos itens podem faltar: valor inicial e opções oferecidas no formulário
TOLERANCIA_PADRAO = 0
OPCOES_TOLERANCIA = (0, 1, 2, 3, 4, 5, 10)

# Quantidade máxima de receitas buscadas
LIMITE_RESULTADOS = 30

# Atalhos de alergias comuns
SUGESTOES_ALERGENOS = ("leite", "ovo", "trigo", "amendoim", "camarao", "peixe", "castanha", "soja")

# Opções de categoria, com None representando busca global
OPCOES_CATEGORIA = ((None, "Todas"),) + tuple(map(lambda categoria: (categoria, categoria.title()), CATEGORIAS_DISPONIVEIS))

# Texto reafirmando a quantidade máxima de ingredientes faltando
DICA_BUSCA = lambda est: (
    f"As receitas poderão ter até {est['tolerancia']} ingrediente(s) faltando, "
    "ordenadas pela maior cobertura da sua despensa."
)

# --------------------------------------------------------------------- utilidades

# Executa efeitos em ordem e devolve o último valor da sequência
sequencia = lambda *acoes: acoes[-1]

# Monta tuplas de fonte usadas em toda a interface
fonte = lambda tamanho, peso="normal": (FONTE, tamanho, peso)

# Normaliza um termo digitado: remove acentos, espaços e caixa alta
normalizar = lambda texto: "".join(
    filter(lambda caractere: not unicodedata.combining(caractere), unicodedata.normalize("NFKD", texto))
).strip().lower()

# Mistura uma cor hexadecimal com branco, gerando a variante de destaque
clarear = lambda hexadecimal, fator=0.14: "#" + "".join(
    map(
        lambda canal: f"{int(int(canal, 16) + (255 - int(canal, 16)) * fator):02x}",
        (hexadecimal[1:3], hexadecimal[3:5], hexadecimal[5:7]),
    )
)

# Mede a largura de um texto na fonte indicada
medida_texto = lambda texto, tamanho, peso: tkfont.Font(family=FONTE, size=tamanho, weight=peso).measure(texto)

# Vértices de um retângulo de cantos arredondados
pontos_arredondados = lambda x1, y1, x2, y2, raio: (
    x1 + raio, y1, x2 - raio, y1, x2, y1, x2, y1 + raio,
    x2, y2 - raio, x2, y2, x2 - raio, y2, x1 + raio, y2,
    x1, y2, x1, y2 - raio, x1, y1 + raio, x1, y1,
)

# Desenha a forma arredondada em um canvas
desenhar_arredondado = lambda tela, x1, y1, x2, y2, raio, **extra: tela.create_polygon(
    pontos_arredondados(x1, y1, x2, y2, raio), smooth=True, **extra
)

# ------------------------------------------------------------------ componentes

# Repinta um botão ou etiqueta com o estado visual atual
pintar_botao = lambda tela, cor, texto, cor_texto, tamanho, peso: sequencia(
    tela.delete("all"),
    desenhar_arredondado(tela, 0, 0, tela.winfo_reqwidth(), tela.winfo_reqheight(),
                         tela.winfo_reqheight() / 2, fill=cor, outline=""),
    tela.create_text(tela.winfo_reqwidth() / 2, tela.winfo_reqheight() / 2,
                     text=texto, fill=cor_texto, font=fonte(tamanho, peso)),
)

# Cria um botão/etiqueta em formato de pílula com destaque no ponteiro
criar_botao = lambda mestre, texto, comando=None, cor=COR["chip"], cor_texto=COR["chip_texto"], \
    altura=40, padding=22, tamanho=10, peso="bold", bg=None: (
    lambda fundo, largura: (
        lambda tela: sequencia(
            pintar_botao(tela, cor, texto, cor_texto, tamanho, peso),
            tela.bind("<Button-1>", lambda _e: comando() if comando else None),
            tela.bind("<Enter>", lambda _e: pintar_botao(tela, clarear(cor), texto, cor_texto, tamanho, peso)),
            tela.bind("<Leave>", lambda _e: pintar_botao(tela, cor, texto, cor_texto, tamanho, peso)),
            tela,
        )
    )(tk.Canvas(mestre, width=largura, height=altura, bg=fundo, highlightthickness=0,
                cursor="hand2" if comando else "arrow"))
)(bg or mestre.cget("bg"), medida_texto(texto, tamanho, peso) + padding * 2)

# Cria o selo circular numerado usado nos cartões
criar_selo = lambda mestre, texto, tamanho=30: (
    lambda selo: sequencia(
        desenhar_arredondado(selo, 0, 0, tamanho, tamanho, tamanho / 2, fill=COR["ambar"], outline=""),
        selo.create_text(tamanho / 2, tamanho / 2, text=texto, fill=COR["texto"], font=fonte(10, "bold")),
        selo,
    )
)(tk.Canvas(mestre, width=tamanho, height=tamanho, bg=mestre.cget("bg"), highlightthickness=0))

# Calcula a posição de um chip e do cursor da linha seguinte
proxima_posicao = lambda estado, par, largura: (
    ((0, estado[1] + estado[2] + 6, par[2]), (0, estado[1] + estado[2] + 6))
    if estado[0] + par[1] > largura and estado[0] > 0 else
    ((estado[0] + par[1] + 6, estado[1], max(estado[2], par[2])), (estado[0], estado[1]))
)

# Reduz a lista de chips ao layout final: estado do cursor e posições
calcular_layout = lambda pares, largura: reduce(
    lambda acumulado, par: (
        lambda passo: (passo[0], acumulado[1] + (passo[1],))
    )(proxima_posicao(acumulado[0], par, largura)),
    pares,
    ((0, 0, 0), ()),
)

# Reposiciona os chips em linhas dentro da largura disponível
reorganizar_fluxo = lambda fluxo, largura: (
    lambda util: (
        lambda pares: (
            lambda layout: sequencia(
                tuple(map(
                    lambda par: par[0][0].place(x=par[1][0], y=par[1][1], width=par[0][1], height=par[0][2]),
                    zip(pares, layout[1]),
                )),
                fluxo.configure(height=max(layout[0][1] + layout[0][2], 1)),
            )
        )(calcular_layout(pares, util))
    )(tuple(map(lambda chip: (chip, chip.winfo_reqwidth(), chip.winfo_reqheight()), fluxo.chips)))
)(largura if largura > 40 else (fluxo.winfo_width() or 600))

# Cria uma faixa que distribui chips automaticamente
criar_fluxo = lambda mestre, bg: (
    lambda fluxo: sequencia(
        setattr(fluxo, "chips", []),
        fluxo.bind("<Configure>", lambda evento: reorganizar_fluxo(fluxo, evento.width)),
        fluxo,
    )
)(tk.Frame(mestre, bg=bg, height=1))

# Insere um chip no fluxo e recalcula as linhas
adicionar_chip = lambda fluxo, chip: sequencia(
    fluxo.chips.append(chip),
    reorganizar_fluxo(fluxo, fluxo.winfo_width()),
    chip,
)

# Remove todos os chips de uma faixa
limpar_fluxo = lambda fluxo: sequencia(
    tuple(map(lambda chip: chip.destroy(), fluxo.chips)),
    fluxo.chips.clear(),
    fluxo.configure(height=1),
)

# Reajusta moldura e conteúdo de um cartão arredondado
ajustar_cartao = lambda tela: (
    lambda largura, altura: sequencia(
        tela.configure(height=altura),
        tela.itemconfigure(tela.janela, width=max(largura - tela.padding * 2, 60)),
        tela.delete("moldura"),
        desenhar_arredondado(tela, 0, 0, largura, altura, tela.raio,
                             fill=tela.cor, outline="", tags="moldura"),
        tela.tag_lower("moldura"),
    )
)(max(tela.winfo_width(), 240), tela.corpo.winfo_reqheight() + tela.padding * 2)

# Cria um painel claro com cantos arredondados e área interna
criar_cartao = lambda mestre, fundo, cor=COR["creme"], raio=24, padding=24: (
    lambda tela: (
        lambda corpo: sequencia(
            setattr(tela, "corpo", corpo),
            setattr(tela, "cor", cor),
            setattr(tela, "raio", raio),
            setattr(tela, "padding", padding),
            setattr(tela, "janela", tela.create_window(padding, padding, window=corpo, anchor="nw")),
            tela.bind("<Configure>", lambda _e: ajustar_cartao(tela)),
            corpo.bind("<Configure>", lambda _e: ajustar_cartao(tela)),
            tela,
        )
    )(tk.Frame(tela, bg=cor))
)(tk.Canvas(mestre, bg=fundo, highlightthickness=0, height=10))

# Cria uma região com rolagem vertical e registra as referências no estado
criar_area = lambda est: (
    lambda area: sequencia(
        area.pack(fill="both", expand=True, padx=(38, 24), pady=(0, 20)),
        (lambda canvas, barra: (
            lambda interior: sequencia(
                canvas.configure(yscrollcommand=barra.set),
                barra.configure(command=canvas.yview),
                canvas.pack(side="left", fill="both", expand=True),
                barra.pack(side="right", fill="y"),
                canvas.create_window(0, 0, window=interior, anchor="nw", tags="janela"),
                interior.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all"))),
                canvas.bind("<Configure>", lambda evento: canvas.itemconfigure("janela", width=max(evento.width, 100))),
                est.update({"area": area, "canvas": canvas, "interior": interior}),
                interior,
            )
        )(tk.Frame(canvas, bg=COR["fundo"])))(
            tk.Canvas(area, bg=COR["fundo"], highlightthickness=0),
            tk.Scrollbar(area, orient="vertical", bg=COR["fundo_claro"], troughcolor=COR["fundo"],
                         activebackground=COR["ambar"], borderwidth=0, highlightthickness=0, width=10),
        ),
    )
)(tk.Frame(est["corpo"], bg=COR["fundo"]))

# Cria um cartão de seção com selo numerado e devolve (cartão, área de conteúdo)
cartao_secao = lambda mestre, numero, titulo, subtitulo: (
    lambda cartao: (
        lambda cabeca, conteudo: sequencia(
            cartao.pack(fill="x", pady=(0, 14)),
            cabeca.pack(fill="x"),
            criar_selo(cabeca, numero).pack(side="left", padx=(0, 12)),
            (lambda textos: sequencia(
                textos.pack(side="left"),
                tk.Label(textos, text=titulo, font=fonte(13, "bold"), fg=COR["texto"],
                         bg=COR["creme"]).pack(anchor="w"),
                tk.Label(textos, text=subtitulo, font=fonte(9), fg=COR["chip_texto"],
                         bg=COR["creme"]).pack(anchor="w"),
            ))(tk.Frame(cabeca, bg=COR["creme"])),
            conteudo.pack(fill="x", pady=(14, 0)),
            (cartao, conteudo),
        )
    )(tk.Frame(cartao.corpo, bg=COR["creme"]), tk.Frame(cartao.corpo, bg=COR["creme"]))
)(criar_cartao(mestre, COR["fundo"]))

# Cria a linha de digitação com o botão de adicionar
criar_entrada = lambda mestre, acao: (
    lambda linha: (
        lambda entrada: sequencia(
            linha.pack(fill="x", pady=(0, 12)),
            entrada.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10)),
            criar_botao(linha, "Adicionar", acao, cor=COR["ambar"], cor_texto=COR["texto"],
                        altura=38, padding=18, bg=COR["creme"]).pack(side="left"),
            entrada.bind("<Return>", lambda _e: acao()),
            entrada,
        )
    )(tk.Entry(linha, font=fonte(11), bg=COR["branco"],
               fg=COR["texto"], relief="flat", insertbackground=COR["texto"], highlightthickness=1,
               highlightbackground=COR["creme_escuro"], highlightcolor=COR["ambar"]))
)(tk.Frame(mestre, bg=COR["creme"]))

# Rótulo auxiliar dentro dos cartões
rotulo = lambda mestre, texto: tk.Label(mestre, text=texto, font=fonte(9), fg=COR["chip_texto"],
                                        bg=COR["creme"]).pack(anchor="w", pady=(0, 8))

# Liga o clique a um widget e a todos os seus filhos
vincular_clique = lambda widget, comando: sequencia(
    widget.bind("<Button-1>", lambda _e: comando()),
    widget.configure(cursor="hand2"),
    tuple(map(lambda filho: vincular_clique(filho, comando), widget.winfo_children())),
)

# Faixa de chips já pronta para exibição
grupo_chips = lambda mestre, itens, cor, cor_texto: (
    lambda fluxo: sequencia(
        fluxo.pack(fill="x", pady=(0, 12)),
        tuple(map(
            lambda item: adicionar_chip(fluxo, criar_botao(fluxo, item, cor=cor, cor_texto=cor_texto,
                                                           altura=32, padding=14, bg=COR["creme"])),
            itens,
        )),
    )
)(criar_fluxo(mestre, COR["creme"]))

# ------------------------------------------------------------------------ estado

# Calcula os ingredientes mais frequentes da base para as sugestões rápidas
sugestoes_da_base = lambda pratos: tuple(
    map(lambda par: par[0], Counter(chain.from_iterable(map(lambda prato: prato.clean_ingredients, pratos))).most_common(10))
)

# Limpa a tela atual e desativa os campos do formulário
limpar_corpo = lambda est: sequencia(
    est.update({"area": None, "canvas": None, "interior": None, "formulario_ativo": False}),
    tuple(map(lambda filho: filho.destroy(), est["corpo"].winfo_children())),
)

# Prepara uma nova área rolável para a tela seguinte
nova_area = lambda est: sequencia(limpar_corpo(est), criar_area(est))

# Adiciona um termo ao conjunto informado, substituindo a coleção congelada
adicionar_valor = lambda est, bruto, chave: sequencia(
    (lambda termo: est.update({chave: est[chave] | {termo}} if termo else {}))(normalizar(bruto)),
    renderizar_formulario(est) if est["formulario_ativo"] else None,
)

# Remove um termo do conjunto informado
remover_valor = lambda est, termo, chave: sequencia(
    est.update({chave: est[chave] - {termo}}),
    renderizar_formulario(est) if est["formulario_ativo"] else None,
)

# Define o tipo de comida selecionado
selecionar_categoria = lambda est, valor: sequencia(
    est.update({"categoria": valor}),
    renderizar_formulario(est) if est["formulario_ativo"] else None,
)

# Define quantos ingredientes podem faltar nas sugestões
selecionar_tolerancia = lambda est, valor: sequencia(
    est.update({"tolerancia": valor}),
    renderizar_formulario(est) if est["formulario_ativo"] else None,
)

# Lê o campo de texto e adiciona o valor digitado
adicionar_termo = lambda est, chave_entrada, chave_destino: (
    lambda entrada: (
        None if not entrada.get().strip() else sequencia(
            adicionar_valor(est, entrada.get(), chave_destino),
            entrada.delete(0, "end"),
        )
    )
)(est[chave_entrada])

# Termos ainda não selecionados, exibidos como sugestão
filtro_sugestoes = lambda est, termos, chave: tuple(filter(lambda termo: termo not in est[chave], termos))

# Chip selecionado com o marcador de remoção
chip_removivel = lambda est, fluxo, termo, chave, cor, cor_texto: criar_botao(
    fluxo, f"{termo}   ×", lambda alvo=termo: remover_valor(est, alvo, chave),
    cor=cor, cor_texto=cor_texto, altura=32, padding=14, bg=COR["creme"],
)

# Chip clicável de sugestão
chip_sugestao = lambda est, fluxo, termo, chave, cor, cor_texto: criar_botao(
    fluxo, termo, lambda alvo=termo: adicionar_valor(est, alvo, chave),
    cor=cor, cor_texto=cor_texto, altura=32, padding=14, bg=COR["creme"],
)

# ------------------------------------------------------------------- formulário

# Redesenha todos os chips e o aviso do formulário
renderizar_formulario = lambda est: sequencia(
    limpar_fluxo(est["fluxo_despensa"]),
    limpar_fluxo(est["fluxo_alergenos"]),
    limpar_fluxo(est["fluxo_categoria"]),
    limpar_fluxo(est["fluxo_tolerancia"]),
    limpar_fluxo(est["fluxo_sugestoes"]),
    limpar_fluxo(est["fluxo_sugestoes_alergenos"]),
    tuple(map(
        lambda termo: adicionar_chip(est["fluxo_despensa"], chip_removivel(
            est, est["fluxo_despensa"], termo, "despensa", COR["ambar"], COR["texto"])),
        sorted(est["despensa"]),
    )),
    tuple(map(
        lambda termo: adicionar_chip(est["fluxo_alergenos"], chip_removivel(
            est, est["fluxo_alergenos"], termo, "alergenos", COR["perigo_bg"], COR["perigo"])),
        sorted(est["alergenos"]),
    )),
    tuple(map(
        lambda opcao: adicionar_chip(est["fluxo_categoria"], criar_botao(
            est["fluxo_categoria"], opcao[1],
            lambda valor=opcao[0]: selecionar_categoria(est, valor),
            cor=COR["ambar"] if est["categoria"] == opcao[0] else COR["chip"],
            cor_texto=COR["texto"] if est["categoria"] == opcao[0] else COR["chip_texto"],
            altura=32, padding=14, bg=COR["creme"])),
        OPCOES_CATEGORIA,
    )),
    tuple(map(
        lambda valor: adicionar_chip(est["fluxo_tolerancia"], criar_botao(
            est["fluxo_tolerancia"], f"até {valor}",
            lambda escolha=valor: selecionar_tolerancia(est, escolha),
            cor=COR["ambar"] if est["tolerancia"] == valor else COR["chip"],
            cor_texto=COR["texto"] if est["tolerancia"] == valor else COR["chip_texto"],
            altura=32, padding=14, bg=COR["creme"])),
        OPCOES_TOLERANCIA,
    )),
    tuple(map(
        lambda termo: adicionar_chip(est["fluxo_sugestoes"], chip_sugestao(
            est, est["fluxo_sugestoes"], termo, "despensa", COR["chip"], COR["chip_texto"])),
        filtro_sugestoes(est, est["sugestoes"], "despensa"),
    )),
    tuple(map(
        lambda termo: adicionar_chip(est["fluxo_sugestoes_alergenos"], chip_sugestao(
            est, est["fluxo_sugestoes_alergenos"], termo, "alergenos", COR["perigo_bg"], COR["perigo"])),
        filtro_sugestoes(est, SUGESTOES_ALERGENOS, "alergenos"),
    )),
    est["aviso"].configure(text=DICA_BUSCA(est)),
)

# Monta a tela inicial de preferências
montar_formulario = lambda est: (
    lambda col: sequencia(
        tk.Label(col, text="Olá! O que vamos cozinhar hoje?", font=fonte(17, "bold"),
                 fg=COR["creme"], bg=COR["fundo"]).pack(anchor="w", pady=(2, 2)),
        tk.Label(col, text="Informe os ingredientes, o tipo de comida e suas alergias. "
                           "Mostramos as receitas que combinam com o que você tem.",
                 font=fonte(10), fg=COR["suave"], bg=COR["fundo"], justify="left",
                 wraplength=820).pack(anchor="w", pady=(0, 18)),

        (lambda par: sequencia(
            est.update({"entrada_ingrediente": criar_entrada(
                par[1], lambda: adicionar_termo(est, "entrada_ingrediente", "despensa"))}),
            est.update({"fluxo_despensa": criar_fluxo(par[1], COR["creme"])}),
            est["fluxo_despensa"].pack(fill="x", pady=(0, 12)),
            rotulo(par[1], "Sugestões rápidas — clique para adicionar:"),
            est.update({"fluxo_sugestoes": criar_fluxo(par[1], COR["creme"])}),
            est["fluxo_sugestoes"].pack(fill="x"),
        ))(cartao_secao(col, "1", "Seus ingredientes", "Digite um item e pressione Enter")),

        (lambda par: sequencia(
            est.update({"fluxo_categoria": criar_fluxo(par[1], COR["creme"])}),
            est["fluxo_categoria"].pack(fill="x"),
        ))(cartao_secao(col, "2", "Tipo de comida", "Escolha uma categoria ou busque em todas")),

        (lambda par: sequencia(
            est.update({"fluxo_tolerancia": criar_fluxo(par[1], COR["creme"])}),
            est["fluxo_tolerancia"].pack(fill="x"),
        ))(cartao_secao(col, "3", "Ingredientes faltando", "Quantos itens você aceita comprar")),

        (lambda par: sequencia(
            est.update({"entrada_alergeno": criar_entrada(
                par[1], lambda: adicionar_termo(est, "entrada_alergeno", "alergenos"))}),
            est.update({"fluxo_alergenos": criar_fluxo(par[1], COR["creme"])}),
            est["fluxo_alergenos"].pack(fill="x", pady=(0, 12)),
            rotulo(par[1], "Alergias comuns — clique para adicionar:"),
            est.update({"fluxo_sugestoes_alergenos": criar_fluxo(par[1], COR["creme"])}),
            est["fluxo_sugestoes_alergenos"].pack(fill="x"),
        ))(cartao_secao(col, "4", "Você tem alguma alergia?", "Esses itens são banidos das receitas")),

        est.update({"aviso": tk.Label(col, text=DICA_BUSCA(est), font=fonte(10, "bold"), fg=COR["ambar_claro"],
                                      bg=COR["fundo"], justify="left", wraplength=820)}),
        est["aviso"].pack(anchor="w", pady=(0, 10)),

        (lambda acoes: sequencia(
            acoes.pack(fill="x", pady=(0, 10)),
            criar_botao(acoes, "Buscar receitas", lambda: buscar(est), altura=52, padding=40,
                        tamanho=12, bg=COR["fundo"]).pack(side="left"),
        ))(tk.Frame(col, bg=COR["fundo"])),

        est.update({"formulario_ativo": True}),
        renderizar_formulario(est),
        est["canvas"].yview_moveto(0),
    )
)(nova_area(est))

# --------------------------------------------------------------------- receitas

# Monta o título exibido na lista de sugestões
titulo_resultados = lambda total: (
    f"{total} receita" + ("s" if total != 1 else "") + " para você"
    + (f"  ·  as {LIMITE_RESULTADOS} melhores" if total > LIMITE_RESULTADOS else "")
)

# Resumo dos filtros aplicados
resumo_busca = lambda est: (
    "Despensa: " + ", ".join(sorted(est["despensa"]))
    + ("   ·   Sem: " + ", ".join(sorted(est["alergenos"])) if est["alergenos"] else "")
    + ("   ·   " + est["categoria"].title() if est["categoria"] else "")
)

# Resumo das receitas removidas por segurança alimentar
resumo_bloqueados = lambda est: (
    ", ".join(map(lambda prato: prato.name, est["bloqueados"][:8]))
    + (f" e mais {len(est['bloqueados']) - 8}" if len(est["bloqueados"]) > 8 else "")
)

# Bloco "falta comprar" (ou aviso de despensa completa) do cartão de sugestão
bloco_faltantes = lambda mestre, resultado: (
    tk.Label(mestre, text="Você tem todos os ingredientes em casa.", font=fonte(9, "bold"),
             fg=COR["ambar_escuro"], bg=COR["creme"]).pack(anchor="w", pady=(12, 0))
    if not resultado.missing_ingredients else
    sequencia(
        tk.Label(mestre, text="Falta comprar:", font=fonte(9, "bold"), fg=COR["chip_texto"],
                 bg=COR["creme"]).pack(anchor="w", pady=(12, 6)),
        grupo_chips(mestre, sorted(resultado.missing_ingredients), COR["chip"], COR["chip_texto"]),
    )
)

# Cartão de uma receita sugerida
cartao_receita = lambda est, mestre, indice, resultado: (
    lambda par: (
        lambda cartao, corpo: sequencia(
            (lambda linha: sequencia(
                linha.pack(fill="x"),
                criar_botao(linha, f"{len(resultado.available_ingredients)} de "
                                   f"{len(resultado.dish.clean_ingredients)} ingredientes",
                            cor=COR["chip"], cor_texto=COR["chip_texto"], altura=32,
                            padding=14, bg=COR["creme"]).pack(side="left"),
                criar_botao(linha, f"{resultado.match_percentage:.0f}% de cobertura",
                            cor=COR["ambar"], cor_texto=COR["texto"], altura=32,
                            padding=14, bg=COR["creme"]).pack(side="left", padx=6),
            ))(tk.Frame(corpo, bg=COR["creme"])),
            bloco_faltantes(corpo, resultado),
            criar_botao(corpo, "Ver receita  →", lambda: montar_receita(est, indice),
                        cor=COR["ambar"], cor_texto=COR["texto"], altura=38, padding=20,
                        bg=COR["creme"]).pack(anchor="e", pady=(14, 0)),
            vincular_clique(cartao, lambda alvo=indice: montar_receita(est, alvo)),
            cartao,
        )
    )(par[0], par[1])
)(cartao_secao(mestre, str(indice + 1), resultado.dish.name, resultado.dish.category.title()))

# Bloco de segurança alimentar ao final da lista
nota_alergenos = lambda est, mestre: (
    lambda cartao: sequencia(
        cartao.pack(fill="x", pady=(4, 8)),
        tk.Label(cartao.corpo, text=f"{len(est['bloqueados'])} receita(s) removida(s) por alergia",
                 font=fonte(10, "bold"), fg=COR["ambar_claro"], bg=COR["fundo_claro"]).pack(anchor="w"),
        tk.Label(cartao.corpo, text=resumo_bloqueados(est), font=fonte(9), fg=COR["suave"],
                 bg=COR["fundo_claro"], justify="left", wraplength=760).pack(anchor="w", pady=(4, 0)),
    )
)(criar_cartao(mestre, COR["fundo"], cor=COR["fundo_claro"]))

# Mensagem exibida quando nenhum prato atende aos filtros
estado_vazio = lambda est, mestre: (
    lambda par: sequencia(
        tk.Label(par[1], text="Tente adicionar mais ingredientes, escolher \"Todas\" no tipo de "
                              "comida ou revisar as alergias informadas.",
                 font=fonte(10), fg=COR["chip_texto"], bg=COR["creme"], justify="left",
                 wraplength=760).pack(anchor="w"),
        criar_botao(par[1], "Voltar ao formulário", lambda: montar_formulario(est), cor=COR["ambar"],
                    cor_texto=COR["texto"], altura=40, padding=22, bg=COR["creme"]).pack(anchor="w", pady=(16, 0)),
    )
)(cartao_secao(mestre, "!", "Nenhuma receita encontrada", "Nada combina com esses filtros agora"))

# Monta a tela com as receitas sugeridas
montar_resultados = lambda est: (
    lambda col: sequencia(
        (lambda topo: sequencia(
            topo.pack(fill="x", pady=(2, 14)),
            criar_botao(topo, "←  Editar busca", lambda: montar_formulario(est), cor=COR["fundo_claro"],
                        cor_texto=COR["creme"], altura=36, padding=18, tamanho=10,
                        bg=COR["fundo"]).pack(side="left"),
        ))(tk.Frame(col, bg=COR["fundo"])),
        tk.Label(col, text=titulo_resultados(len(est["resultados"])), font=fonte(20, "bold"),
                 fg=COR["creme"], bg=COR["fundo"]).pack(anchor="w"),
        tk.Label(col, text=resumo_busca(est), font=fonte(10), fg=COR["suave"], bg=COR["fundo"],
                 justify="left", wraplength=820).pack(anchor="w", pady=(4, 18)),
        estado_vazio(est, col) if not est["resultados"] else
        tuple(map(
            lambda par: cartao_receita(est, col, par[0], par[1]),
            enumerate(est["resultados"][:LIMITE_RESULTADOS]),
        )),
        nota_alergenos(est, col) if est["bloqueados"] else None,
        est["canvas"].yview_moveto(0),
    )
)(nova_area(est))

# ---------------------------------------------------------------------- receita

# Linha de ingrediente original
linha_ingrediente = lambda mestre, texto: (
    lambda linha: sequencia(
        linha.pack(fill="x", pady=1),
        tk.Label(linha, text="•", font=fonte(10, "bold"), fg=COR["ambar_escuro"],
                 bg=COR["creme"]).pack(side="left", padx=(0, 8)),
        tk.Label(linha, text=texto, font=fonte(10), fg=COR["texto"], bg=COR["creme"],
                 justify="left", wraplength=700).pack(side="left", anchor="w"),
    )
)(tk.Frame(mestre, bg=COR["creme"]))

# Linha numerada do modo de preparo
linha_passo = lambda mestre, numero, texto: (
    lambda linha: sequencia(
        linha.pack(fill="x", pady=4),
        criar_selo(linha, str(numero), 26).pack(side="left", anchor="n", padx=(0, 12)),
        tk.Label(linha, text=texto, font=fonte(10), fg=COR["texto"], bg=COR["creme"],
                 justify="left", wraplength=700).pack(side="left", anchor="w"),
    )
)(tk.Frame(mestre, bg=COR["creme"]))

# Cartão de ingredientes da receita escolhida
cartao_ingredientes = lambda mestre, resultado: (
    lambda par: sequencia(
        tk.Label(par[1], text="Você já tem", font=fonte(9, "bold"), fg=COR["chip_texto"],
                 bg=COR["creme"]).pack(anchor="w", pady=(0, 6)) if resultado.available_ingredients else None,
        grupo_chips(par[1], sorted(resultado.available_ingredients), COR["ambar"], COR["texto"])
        if resultado.available_ingredients else None,
        tk.Label(par[1], text="Falta comprar", font=fonte(9, "bold"), fg=COR["chip_texto"],
                 bg=COR["creme"]).pack(anchor="w", pady=(0, 6)) if resultado.missing_ingredients else None,
        grupo_chips(par[1], sorted(resultado.missing_ingredients), COR["perigo_bg"], COR["perigo"])
        if resultado.missing_ingredients else None,
        tk.Label(par[1], text="Lista completa da receita", font=fonte(9, "bold"), fg=COR["chip_texto"],
                 bg=COR["creme"]).pack(anchor="w", pady=(4, 6)),
        tuple(map(lambda item: linha_ingrediente(par[1], item), resultado.dish.raw_ingredients))
        if resultado.dish.raw_ingredients else
        tk.Label(par[1], text="Lista de ingredientes não informada.", font=fonte(10),
                 fg=COR["chip_texto"], bg=COR["creme"]).pack(anchor="w"),
    )
)(cartao_secao(mestre, "1", "Ingredientes", "O que vai na receita"))

# Cartão com o passo a passo
cartao_preparo = lambda mestre, resultado: (
    lambda par: (
        tuple(map(lambda par_passo: linha_passo(par[1], par_passo[0] + 1, par_passo[1]),
                  enumerate(resultado.dish.recipe)))
        if resultado.dish.recipe else
        tk.Label(par[1], text="Modo de preparo não disponível para este prato.", font=fonte(10),
                 fg=COR["chip_texto"], bg=COR["creme"]).pack(anchor="w")
    )
)(cartao_secao(mestre, "2", "Modo de preparo", "Passo a passo"))

# Monta a tela de detalhes da receita
montar_receita = lambda est, indice: (
    lambda resultado, col: sequencia(
        (lambda topo: sequencia(
            topo.pack(fill="x", pady=(2, 14)),
            criar_botao(topo, "←  Voltar às receitas", lambda: montar_resultados(est), cor=COR["fundo_claro"],
                        cor_texto=COR["creme"], altura=36, padding=18, tamanho=10,
                        bg=COR["fundo"]).pack(side="left"),
            criar_botao(topo, "Próxima sugestão  →",
                        lambda: montar_receita(est, (indice + 1) % len(est["resultados"])),
                        cor=COR["fundo_claro"], cor_texto=COR["creme"], altura=36, padding=18,
                        tamanho=10, bg=COR["fundo"]).pack(side="right")
            if len(est["resultados"]) > 1 else None,
        ))(tk.Frame(col, bg=COR["fundo"])),
        tk.Label(col, text=resultado.dish.name, font=fonte(24, "bold"), fg=COR["creme"], bg=COR["fundo"],
                 justify="left", wraplength=820).pack(anchor="w"),
        (lambda etiquetas: sequencia(
            etiquetas.pack(fill="x", pady=(10, 18)),
            criar_botao(etiquetas, resultado.dish.category.title(), cor=COR["fundo_claro"],
                        cor_texto=COR["creme"], altura=32, padding=14, bg=COR["fundo"]).pack(side="left"),
            criar_botao(etiquetas, f"{resultado.match_percentage:.0f}% de cobertura", cor=COR["ambar"],
                        cor_texto=COR["texto"], altura=32, padding=14, bg=COR["fundo"]).pack(side="left", padx=6),
        ))(tk.Frame(col, bg=COR["fundo"])),
        cartao_ingredientes(col, resultado),
        cartao_preparo(col, resultado),
        (lambda acoes: sequencia(
            acoes.pack(fill="x", pady=(4, 8)),
            criar_botao(acoes, "←  Escolher outra receita", lambda: montar_resultados(est),
                        cor=COR["fundo_claro"], cor_texto=COR["creme"], altura=46, padding=26,
                        tamanho=11, bg=COR["fundo"]).pack(side="left"),
            criar_botao(acoes, "Nova busca", lambda: montar_formulario(est), cor=COR["ambar"],
                        cor_texto=COR["texto"], altura=46, padding=30, tamanho=11,
                        bg=COR["fundo"]).pack(side="left", padx=10),
        ))(tk.Frame(col, bg=COR["fundo"])),
        est["canvas"].yview_moveto(0),
    )
)(est["resultados"][indice], nova_area(est))

# Executa a busca combinando despensa, alergias e tipo de comida
buscar = lambda est: (
    est["aviso"].configure(text="Adicione pelo menos um ingrediente para buscar receitas.")
    if not est["despensa"] else
    sequencia(
        (lambda prefs: est.update({
            "resultados": run_recommendation(est["grafo"], prefs),
            "bloqueados": obter_pratos_bloqueados(est["grafo"], prefs.allergens, prefs.category_filter),
        }))(UserPreferences(
            pantry=est["despensa"],
            allergens=est["alergenos"],
            max_missing=est["tolerancia"],
            category_filter=est["categoria"],
            min_matched=min(2, len(est["despensa"])),
        )),
        montar_resultados(est),
    )
)

# ------------------------------------------------------------------------- janela

# Rola a área visível conforme a roda do mouse
rolar = lambda est, evento: (
    est["canvas"].yview_scroll(-1 * int(evento.delta / 120) * 2, "units")
    if est["canvas"] is not None and est["canvas"].winfo_exists() else None
)

# Cabeçalho fixo da aplicação
cabecalho = lambda raiz: (
    lambda topo: sequencia(
        topo.pack(fill="x", padx=38, pady=(24, 14)),
        tk.Label(topo, text="COOK WHAT U HAVE", font=fonte(27, "bold"), fg=COR["ambar"],
                 bg=COR["fundo"]).pack(anchor="w"),
    )
)(tk.Frame(raiz, bg=COR["fundo"]))

# Monta a janela, o cabeçalho e a primeira tela; devolve o estado compartilhado
abrir = lambda raiz, pratos: (
    lambda base: (
        lambda est: sequencia(
            raiz.title("Cook What U Have"),
            raiz.geometry("1020x800"),
            raiz.minsize(880, 640),
            raiz.configure(bg=COR["fundo"]),
            cabecalho(raiz),
            est["corpo"].pack(fill="both", expand=True),
            raiz.bind_all("<MouseWheel>", lambda evento: rolar(est, evento)),
            montar_formulario(est),
            est,
        )
    )({
        "raiz": raiz,
        "pratos": base,
        "grafo": build_recipe_graph(base),
        "corpo": tk.Frame(raiz, bg=COR["fundo"]),
        "despensa": frozenset(),
        "alergenos": frozenset(),
        "categoria": None,
        "resultados": (),
        "bloqueados": (),
        "sugestoes": sugestoes_da_base(base),
        "tolerancia": TOLERANCIA_PADRAO,
        "area": None,
        "canvas": None,
        "interior": None,
        "formulario_ativo": False,
    })
)(tuple(pratos) if pratos is not None else carregar_pratos(DEFAULT_DATA_DIR))

# Abre a aplicação gráfica
iniciar = lambda pratos=None: (
    lambda raiz: sequencia(abrir(raiz, pratos), raiz.mainloop())
)(tk.Tk())


if __name__ == "__main__":
    iniciar()
