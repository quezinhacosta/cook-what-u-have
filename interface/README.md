# Modulo de Interface do Usuario e Adaptadores de E/S (`interface/`)
### Camada de Interacao, Bordas de Efeitos Colaterais, CLI e GUI Neo-Brutalista

> **Componente do Projeto:** *Cook What U Have (MealMatch)*
> **Responsabilidade:** Gerenciar a interacao com o usuario via terminal (CLI) ou interface grafica desktop mobile (GUI), carregar a base de dados dos pratos a partir do disco e formatar relatorios visuais claros, isolando os efeitos colaterais (*I/O Boundaries*) do nucleo puro do sistema.

---

## 1. Arquitetura e Principio de Bordas de E/S (*I/O Boundaries*)

Na arquitetura de sistemas funcionais, o dominio algoritmico (`implementation/`) permanece 100% puro e sem contato com o mundo externo. O modulo `interface/` desempenha o papel de **casca protetora (*Functional Core, Imperative Shell*)**:

```
[ BORDAS DE EFEITOS COLATERAIS ]                    [ NUCLEO FUNCIONAL PURO ]
       cli.py / gui.py / io_adapter.py                     implementation/
 (Teclado / Tela / Disco / Flet) ── frozenset / Dish ──►  (Grafo Bipartido)
                                                                 │
                                                                 ▼
      formatter.py / gui_theme.py                         MatchResult
 (Formatacao declarativa / Neo-Brutalism) ◄──────────────────────┘
```

1. **Sem Instrucoes Imperativas no Motor:** Toda a logica de carga, conversao e ordenacao matematica e baseada em estruturas imutaveis e funcoes puras.
2. **Coleta e Conversao Segura:** Converte entradas do teclado diretamente para conjuntos imutaveis `frozenset`.
3. **Carga em Lote Controlada:** Le os arquivos `pratos.json` das 8 categorias em `ingestion/data/` (400 receitas coletadas) e instancia as entidades congeladas `Dish`.
4. **Formatacao Declarativa:** Projeta os nós recomendados em cards visuais claros, destacando itens em posse do usuario, a lista de compras automatica e os pratos bloqueados por seguranca alimentar.
5. **Zero Emojis:** Todos os textos, rotulos, badges e telas utilizam estritamente texto limpo, badges geometricos e icones vetoriais minimalistas.

---

## 2. Estrutura Modular da Pasta

```
interface/
├── __init__.py           # Exportacao dos componentes da interface (CLI e GUI)
├── io_adapter.py         # Leitura pura dos JSONs do disco -> tuple[Dish, ...]
├── formatter.py          # Projecao pura: MatchResult -> texto formatado (CLI)
├── cli.py                # Ponto de entrada interativo no console
├── gui_theme.py          # Tokens de design Neo-Brutalism e fabricas de componentes Flet
├── gui.py                # Interface grafica desktop simulando smartphone (410x800px)
└── README.md             # Documentacao tecnica da camada de interface
```

---

## 3. Interface Grafica Desktop Neo-Brutalista (`gui.py`)

A GUI simula com precisao a ergonomia, proporcao e estética de um aplicativo de celular:
- **Viewport Mobile Fixa:** Janela com dimensao fixa de `410x800` pixels, centralizada, com fundo creme suave (`#FAF7F2`).
- **Estilo Neo-Brutalism:** Bordas pretas solidas de `2px` (`#111111`), cantos arredondados (`border_radius` de `14px` a `18px`, e `999px` para botoes pilula), sombras solidas deslocadas sem desfoque (`offset=(4, 4)` / hard shadows) e paleta cromatica vibrante de alto contraste.
- **Paleta de Cores:**
  - Amarelo Mostarda (`#FFD166`): Botoes de acao principal (CTA) e destaques.
  - Verde Menta/Limao (`#B5E48C`): 100% de correspondencia e prontidao para cozinhar.
  - Lilas Suave (`#CDB4DB`): Cards de resumo da sessao e cabecalho de receita.
  - Rosa Chiclete/Coral (`#FF8FA3`): Alertas de validacao, ingredientes faltantes e pratos bloqueados.
  - Laranja Tangerina (`#F4A261`): Chips selecionaveis de categorias culinarias.

### Fluxo de Telas da GUI:
1. **Tela 1 — Consulta da Despensa:**
   - Cabecalho com contador de receitas carregadas.
   - Input textual para despensa com validacao obrigatoria de **no minimo 2 ingredientes** (banner visual amigavel de aviso).
   - Input opcional de alergenos banidos (tolerancia zero).
   - Seletor numerico compacto com botoes `[-]` e `[+]` para tolerancia de faltantes.
   - Carrossel horizontal de chips das 8 categorias culinarias + `[0] Todas`.
   - Botao de acao principal `"BUSCAR RECEITAS"`.
2. **Tela 2 — Resultados e Sugestões:**
   - Barra superior com botao de retorno e badge de total de pratos viaveis.
   - Card resumo lilas da consulta informada.
   - Estado vazio estilizado caso nenhum prato atenda a despensa e tolerancia.
   - Cards clicaveis de pratos com ranking (`#1`, `#2`...), categoria, porcentagem de cobertura, itens disponiveis e lista de compras destacada.
   - Acordeao colapsavel com a contagem e lista de pratos bloqueados por seguranca alimentar.
3. **Tela 3 — Detalhes da Receita:**
   - Cabecalho com titulo do prato, categoria e cobertura.
   - Resumo de compras (verde se completo, coral se faltar comprar insumos).
   - Lista limpa com marcadores geometricos dos ingredientes originais com medidas.
   - Modo de preparo passo a passo em blocos numerados legiveis (`[1]`, `[2]`...).
   - Navegacao mantendo o estado da lista em memoria (sem recalcular o grafo ao voltar).

### Como Executar a Interface Grafica:
```bash
# Execucao nativa desktop:
python3 main.py --gui

# Ou diretamente pelo modulo da GUI:
python3 -m interface.gui

# Execucao em modo navegador web (ou quando sem servidor X11):
python3 main.py --gui --web
```

---

## 4. Interface de Linha de Comando Declarativa (`cli.py`)

A CLI oferece o fluxo interativo no terminal:

```bash
# Ponto de entrada padrao:
python3 main.py

# Ou diretamente pelo modulo da CLI:
python3 -m interface.cli
```

### Exemplo de Uso no Console:
```text
================================================================================
        COOK WHAT U HAVE — SUGESTOES DE REFEICAO DISPONIVEIS
================================================================================
Configuracoes da Sessao:
  • Despensa (3 itens): [leite, ovo, queijo]
  • Alergenos Banidos (1): [farinha]
  • Tolerancia Maxima de Faltantes: Ate 1 item(ns)
--------------------------------------------------------------------------------

[1] OMELETE CREMOSA (Categoria: Aves)
    Correspondencia: 100.0% [2/2 ingredientes]
    Disponiveis em casa: [ovo, queijo]
    Todos os ingredientes disponiveis em casa! Pronto para cozinhar.

--------------------------------------------------------------------------------
Pratos Bloqueados por Seguranca Alimentar:
   [BLOQUEADO] Bolo de Cenoura (Contem: [farinha de trigo])
================================================================================
```
