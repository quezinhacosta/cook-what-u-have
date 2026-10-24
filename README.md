#  Cook What U Have (MealMatch)
### Motor Funcional de Indicação de Pratos e Redução do Desperdício Alimentar

> **Disciplina:** Programação Funcional em Python — Avaliação do 2º Grau de Qualificação (GQ)  
> **Etapa 1:** Especificação Detalhada da Situação-Problema e Proposta de Solução  
> **Prazo da Etapa 1:** 27/10/2026 às 23:55  
> **Prazo da Etapa 2 (Implementação):** 16/11/2026 às 23:55  

---

##  Sumário Executivo

O **Cook What U Have** (também referenciado como **MealMatch**) é um sistema computacional concebido estritamente sob as premissas do **Paradigma de Programação Funcional (PF)** em Python. O seu objetivo central é solucionar a dissonância diária enfrentada por milhares de famílias: a coexistência entre o **desperdício de alimentos domésticos** e a **dificuldade de planeamento de refeições seguras** perante alergias e intolerâncias alimentares severas.

Diferente de plataformas convencionais que operam em fluxo imperativo de busca ("escolha um prato e compre os ingredientes faltantes"), o *Cook What U Have* **inverte radicalmente o fluxo**: processa a coleção de ingredientes disponíveis na despensa, aplica restrições alérgicas absolutas e projeta as opções de pratos viáveis por meio de teoria dos conjuntos, ordenadas pela maior taxa de cobertura e menor necessidade de compras adicionais.

---

##  Navegação Rápida pelos Módulos do Projeto

O projeto foi decomposto em três grandes módulos arquiteturais independentes, cada um acompanhado de sua documentação dedicada:

| Módulo / Pasta | Documentação | Responsabilidade Central |
| :--- | :---: | :--- |
| ** Ingestão de Dados** | [`ingestion/README.md`](ingestion/README.md) | Raspagem semântica de receitas reais (`recipe-scrapers`), pipeline funcional de sanitização/normalização de strings e geração da base estática imutável (`pratos.json`). |
| ** Implementação Funcional** | [`implementation/README.md`](implementation/README.md) | Núcleo algorítmico do sistema: estruturas imutáveis (`@dataclass(frozen=True)`, `frozenset`), funções puras, álgebra de conjuntos e pipeline de alta ordem (`filter`, `map`, `sorted`). |
| **Interface e I/O** | [`interface/README.md`](interface/README.md) | Camada de borda (*I/O Boundaries*): CLI interativa/declarativa, leitura controlada de arquivos e formatação determinística dos relatórios de refeições e compras. |

---

## 1. Especificação Detalhada da Situação-Problema

### 1.1. O Paradoxo da Despensa Cheia e o Desperdício Alimentar
O desperdício de alimentos no ambiente doméstico é impulsionado principalmente pela incapacidade humana de correlacionar mentalmente ingredientes perecíveis dispersos em receitas viáveis. Frequentemente, os consumidores possuem diversos insumos (ex.: abobrinha, ovos, cebola, arroz cozido), mas acabam por recorrer a novos pedidos de entrega (*delivery*) ou a novas compras de supermercado por não vislumbrarem combinações imediatas. Os insumos prévios deterioram-se e são descartados, gerando prejuízos financeiros e impactos socioambientais significativos.

### 1.2. O Risco Crítico das Alergias e Restrições Alimentares
Segundo a Organização Mundial da Saúde (OMS), as alergias alimentares afetam uma parcela substancial da população global. Reações alérgicas a glúten (doença celíaca), lactose/proteína do leite, mariscos, nozes, amendoim e soja podem variar desde desconfortos gastrointestinais até choque anafilático potencialmente fatal.
* **A falha humana na inspeção manual:** A análise manual de listas extensas de receitas ou de cardápios é um processo demorado, cognitivamente exaustivo e altamente suscetível a erros humanos de desatenção.
* **A necessidade de rigor absoluto:** Um sistema confiável de recomendação culinária não pode tratar restrições alimentares como um mero critério ponderado de pontuação. A presença de um único alérgeno interdito deve desqualificar **terminantemente e determinísticamente** o prato do rol de sugestões.

### 1.3. Limitações das Plataformas Atuais
As plataformas de receitas existentes (como TudoGostoso, Tastemade e Allrecipes) sofrem de três gargalos conceituais:
1. **Busca Nominal Unidirecional:** O usuário é obrigado a saber antecipadamente o nome do prato que deseja confeccionar.
2. **Excesso de Instruções Não Essenciais:** Focam em gerar descrições textuais longas de passos de preparo, tempos de forno e vídeos, negligenciando a etapa primordial da tomada de decisão ("o que é matematicamente possível cozinhar agora?").
3. **Ausência de Transparência na Cobertura:** Raramente informam a porcentagem exata de insumos já presentes versus a lista minimalista do que realmente falta comprar.

### 1.4. Inversão do Fluxo Operacional
O *Cook What U Have* inverte este paradigma através de uma abordagem orientada a dados e álgebra de conjuntos:

```
[Fluxo Convencional - Problemático]
Ideia do Prato ──► Leitura de 20 Ingredientes ──► Ida ao Supermercado ──► Descarte do que sobrou na despensa

[Fluxo do Cook What U Have - Proposto]
Despensa Atual (O que tenho) ──► Filtro de Segurança (Alérgenos = 0) ──► Otimização de Cobertura ──► Prato Viável + Lista Residual Mínima
```

---

## 2. Proposta de Programa e Escopo da Solução

### 2.1. O que é o *Cook What U Have*
O programa atuará como um **motor determinístico de decisão, filtragem e recomendação culinária**. Não se propõe a ser um livro de receitas prolixo com tutoriais culinários, mas uma ferramenta computacional precisa que responde com exatidão matemática:
> *"Com os $N$ ingredientes presentes na sua despensa e banindo absolutamente os alérgenos $A$, quais são os pratos possíveis de serem feitos, qual a taxa de cobertura de cada um e o que exatamente resta comprar?"*

### 2.2. Delimitação de Fronteiras (Escopo)

| Dimensão | Em Escopo (In-Scope) | Fora de Escopo (Out-of-Scope) |
| :--- | :--- | :--- |
| **Lógica de Decisão** | Álgebra de conjuntos puros (interseção, diferença, pertinência) e ranking de cobertura. | Algoritmos de redes neurais opacos ou modelos estocásticos não determinísticos. |
| **Segurança Alimentar** | Exclusão determinística rígida com base em lista de termos interditos. | Diagnóstico médico de alergias ou análise química de traços microscópicos. |
| **Base de Dados** | Extração de fontes confiáveis via `recipe-scrapers` e persistência estática em `pratos.json`. | Banco de dados relacional (SQL) com transações mutáveis ou escrita concorrente em disco. |
| **Instruções Culinárias** | Metadados essenciais (identificador, nome, categoria e conjunto de ingredientes padronizados). | Textos descritivos de modo de preparo, tempo de forno, temperatura ou vídeos tutoriais. |
| **Interface** | CLI interativa e declarativa com suporte a relatórios visuais estruturados. | Frontend web complexo ou aplicativo mobile baseado em frameworks de estado reativo mutável. |

---

## 3. Aplicação Rigorosa do Paradigma de Programação Funcional

A totalidade da lógica de negócio do sistema será estruturada em conformidade estrita com os fundamentos de Programação Funcional (PF), garantindo corretude formal, testabilidade e ausência de bugs relacionados a estado compartilhado.

```mermaid
flowchart TD
    A["Despensa do Usuário (frozenset)"] --> PIPELINE
    B["Restrições / Alérgenos (frozenset)"] --> PIPELINE
    C["Base de Pratos (pratos.json)"] --> PIPELINE
    T["Limiar de Tolerância (k faltantes)"] --> PIPELINE

    subgraph PIPELINE ["Pipeline Funcional Puro (implementation/)"]
        P1["1. Carregamento Imutável dos Pratos\n(NamedTuple / dataclass frozen)"]
        P2["2. filter(is_safe_dish, dishes)\nEliminação absoluta de alérgenos (isdisjoint)"]
        P3["3. map(calculate_match, safe_dishes)\nCálculo de interseção, faltantes e % cobertura"]
        P4["4. filter(is_within_tolerance, matches)\nDescarte de pratos acima do limiar de compras"]
        P5["5. sorted(matches, key=pure_lambda)\nOrdenação decrescente de match e crescente de faltantes"]
        
        P1 --> P2 --> P3 --> P4 --> P5
    end

    PIPELINE --> OUT["Resultado: Coleção Imutável de Sugestões\n(Percentual, Presentes, Faltantes)"]
```

### 3.1. Imutabilidade Absoluta de Dados
* Nenhuma entidade de domínio permitirá alteração de estado após sua instanciação.
* Serão empregados exclusivamente `@dataclass(frozen=True)` e coleções do tipo `frozenset`.
* Proibição categórica de métodos mutadores como `.append()`, `.extend()`, `.pop()`, bem como de reatribuição de variáveis locais.

### 3.2. Funções Puras e Ausência de Efeitos Secundários (*Side Effects*)
* Todas as funções que realizam processamento, cálculo ou filtragem serão **funções puras** no sentido matemático: para os mesmos parâmetros de entrada, retornarão invariavelmente a mesma saída, sem consultar nem modificar variáveis globais.
* As operações de I/O (leitura do arquivo `pratos.json` e impressão no terminal) são estritamente isoladas na pasta `interface/` (*I/O Boundaries*), mantendo a pasta `implementation/` 100% pura.

### 3.3. Funções de Alta Ordem (*Higher-Order Functions*) e Composição
A manipulação e transformação de fluxos de dados prescindirá de laços imperativos, recorrendo ao encadeamento de funções de ordem superior:
* **`filter()`**: Utilizado para remover com garantia matemática qualquer prato cuja interseção com o conjunto de alérgenos seja não vazia (`ingredients.isdisjoint(allergens)`).
* **`map()`**: Utilizado para projetar os pratos seguros em estruturas enriquecidas de resultado (`MatchResult`), calculando a taxa percentual de cobertura e segregando insumos disponíveis e faltantes.
* **`sorted()`**: Recorrendo a funções `lambda` puras como critério de ordenação e relevância multicritério (ex.: maior taxa de match, menor quantidade de ingredientes faltantes).
* **`functools.partial`**: Utilizado para aplicação parcial e currying, parametrizando predicados de filtragem conforme as configurações do usuário.

### 3.4. Eliminação de Estruturas Imperativas
* Banimento completo do uso de laços `for` ou `while` que operem com acumuladores ou contadores mutáveis (`count += 1`, `lista.append(item)`).
* O processamento agregador ou redutor será implementado via funções de ordem superior (`functools.reduce`), compreensão declarativa de coleções imutáveis ou recursão de cauda onde apropriado.

### 3.5. Fundamentação na Teoria dos Conjuntos
As operações centrais do motor traduzem-se diretamente em operações primitivas sobre `frozenset`:
* **Pertinência de Alérgenos:** $\text{Seguro}(P, A) \iff (I_P \cap A) = \emptyset$ (ou `I_P.isdisjoint(A)`)
* **Ingredientes Presentes:** $I_{\text{presentes}} = I_P \cap D$
* **Ingredientes em Falta (Lista de Compras):** $I_{\text{faltantes}} = I_P \setminus D$
* **Taxa de Cobertura:** $\text{Score}(P, D) = \frac{|I_P \cap D|}{|I_P|} \times 100\%$

---

## 4. Modelagem de Dados Imutável

As estruturas de dados primárias serão expressas no módulo `implementation/models.py` da seguinte forma:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Dish:
    """Representa a entidade de um prato cadastrado na base imutável."""
    id: str
    name: str
    category: str
    ingredients: frozenset[str]

@dataclass(frozen=True)
class UserPreferences:
    """Encapsula a despensa, os alérgenos e parâmetros de tolerância do usuário."""
    pantry: frozenset[str]
    allergens: frozenset[str]
    max_missing_threshold: int = 0

@dataclass(frozen=True)
class MatchResult:
    """Resultado imutável da análise de viabilidade de um prato."""
    dish: Dish
    match_percentage: float
    available_ingredients: frozenset[str]
    missing_ingredients: frozenset[str]
```

Para mais detalhes sobre as funções puras do motor, consulte o [`implementation/README.md`](implementation/README.md).

---

## 5. Ingestão de Dados e Extração (`recipe-scrapers`)

Para garantir que a base de dados não seja trivial ou fictícia, o módulo `ingestion/` executa uma rotina desacoplada de extração e higienização de receitas baseada na biblioteca [`recipe-scrapers`](https://github.com/hhursev/recipe-scrapers).

```mermaid
flowchart LR
    URL["URLs Culinárias\n(Web / Portais)"] --> SCRAPE["Módulo Extrator\n(ingestion/extractor.py)"]
    SCRAPE --> RAW["Ingredientes Brutos\n('200g de farinha de trigo')"]
    RAW --> NORM["Pipeline de Normalização Pura\n(ingestion/normalizer.py)"]
    NORM --> JSON[("data/pratos.json\n(Base Local Imutável)")]
```

Para detalhes técnicos sobre os filtros de sanitização textual e remoção de unidades, consulte o [`ingestion/README.md`](ingestion/README.md).

---

## 6. Interface do Usuário e Visualização

A interação do usuário com o sistema é centralizada no módulo `interface/`, isolando as chamadas de I/O e garantindo uma apresentação clara dos resultados:

```text
================================================================================
        🍳 COOK WHAT U HAVE — SUGESTÕES DE REFEIÇÃO DISPONÍVEIS
================================================================================
Filtros Ativos:
- Despensa: [arroz arboreo, abobrinha, espinafre, ovo, sal]
- Alérgenos Banidos: [camarao, frutos do mar, leite de coco]
- Limiar de Tolerância: Até 2 itens faltantes
--------------------------------------------------------------------------------

[1] OMELETE DE ESPINAFRE E QUEIJO (Categoria: Prato Principal)
    Correspondência: 60.0% [3/5 ingredientes]
     Disponíveis em casa: [espinafre, ovo, sal]
    Lista de compras (faltam 2): [manteiga, queijo]

[2] RISOTO DE ABOBRINHA COM TOMATE SECO (Categoria: Massas e Risotos)
    Correspondência: 33.3% [2/6 ingredientes]
    Disponíveis em casa: [abobrinha, arroz arboreo]
    Lista de compras (faltam 4): [azeite, caldo de legumes, cebola, tomate seco]
    (Oculto por exceder a tolerância de faltantes <= 2)

--------------------------------------------------------------------------------
Pratos desclassificados por segurança alimentar (Alérgenos detectados):
   - Moqueca de Camarão (Contém: 'camarao', 'leite de coco')
================================================================================
```

Para ver a especificação completa da CLI e dos adaptadores de entrada/saída, consulte o [`interface/README.md`](interface/README.md).

---

## 7. Estrutura Arquitetural do Repositório

O repositório está organizado de forma modular, com responsabilidades estritamente delimitadas:

```
cook-what-u-have/
│
├── data/
│   └── pratos.json                 # Catálogo estático e imutável de pratos
│
├── docs/
│   └── trabalhoProgramacaoFuncional.pdf  # Diretrizes acadêmicas oficiais
│
├── ingestion/                      # MÓDULO 1: Extração e Sanitização de Dados
│   ├── extractor.py                # Extração via recipe-scrapers
│   ├── normalizer.py               # Pipeline funcional de sanitização textual
│   ├── pipeline.py                 # Orquestrador funcional de geração de pratos.json
│   ├── sources.json                # Relação de URLs gastronômicas
│   └── README.md                   # Documentação detalhada da Ingestão
│
├── implementation/                 # MÓDULO 2: Núcleo Algorítmico Funcional
│   ├── models.py                   # Entidades imutáveis (Dish, UserPreferences, MatchResult)
│   ├── engine.py                   # Funções puras de teoria dos conjuntos e cobertura
│   ├── pipeline.py                 # Funções de alta ordem (filter, map, sorted)
│   └── README.md                   # Documentação detalhada da Implementação Funcional
│
├── interface/                      # MÓDULO 3: Bordas de I/O e Apresentação
│   ├── cli.py                      # Ponto de entrada da CLI e parsing de argumentos
│   ├── formatter.py                # Funções puras de formatação visual de relatórios
│   ├── io_adapter.py               # Leitura pura de dados do disco
│   └── README.md                   # Documentação detalhada da Interface
│
├── tests/                          # MÓDULO DE TESTES
│   ├── test_engine.py              # Testes unitários de determinismo e teoria dos conjuntos
│   ├── test_pipeline.py            # Testes de exclusão de alérgenos e ranking
│   └── test_immutability.py        # Testes de garantia de imutabilidade de dados
│
├── requirements.txt                # Dependências mínimas
└── README.md                       # Documento principal da proposta
```

---

## 8. Planejamento de Desenvolvimento e Cronograma de Entregas

Conforme as diretrizes estipuladas no documento acadêmico da disciplina, o projeto é subdividido em quatro etapas formais:

```mermaid
timeline
    title Cronograma de Desenvolvimento (2º GQ)
    2026-10-24 : Concepção e Elaboração da Proposta
    2026-10-27 : ETAPA 1 - Entrega do Documento de Proposta e Especificação (23:55)
    2026-10-28 a 2026-11-15 : Desenvolvimento do Código Funcional e Testes Unitários
    2026-11-16 : ETAPA 2 - Entrega do Código Fonte Funcional em Python (23:55)
    2026-11-17 a 2026-12-01 : ETAPA 3 e 4 - Apresentações ao Vivo e Avaliação pelos Pares
```

| Etapa | Data Limite | Descrição e Entregáveis | Penalidade / Observações |
| :---: | :---: | :--- | :--- |
| **Etapa 1** | **27/10/2026 (ter)**<br>até às 23:55 | **Entrega do Documento de Especificação Detalhada:** Especificação aprofundada da situação-problema, formalização matemática da solução funcional, escopo e modelagem. | Atrasos implicam na penalização de **1,0 ponto** na nota final. |
| **Etapa 2** | **16/11/2026 (ter)**<br>até às 23:55 | **Entrega do Código Fonte Completo:** Implementação em Python sob preceitos rigorosos do paradigma funcional, testes unitários automatizados cobrindo imutabilidade e pureza. | Atrasos implicam na penalização de **2,0 pontos** na nota final. |
| **Etapa 3** | **17/11, 24/11, 27/11 e 01/12/2026** | **Apresentação da Solução:** Demonstração ao vivo do programa em execução para a professora e para a turma, com explicação técnica do código desenvolvido e justificativa dos conceitos funcionais. | Cronograma das apresentações a ser disponibilizado no Teams. |
| **Etapa 4** | Durante as sessões de apresentação | **Avaliação pelos Pares:** Preenchimento de formulário impresso avaliando os trabalhos dos colegas com notas de 0 a 10 segundo critérios pré-estabelecidos. | Notas muito discrepantes das notas da professora serão penalizadas. |

### Composição da Nota Final do 2º GQ:
$$\text{Nota Final} = (0.7 \times \text{Trabalho}) + (0.1 \times \text{Lista de Exercícios}) + (0.1 \times \overline{\text{Notas dos Colegas}}) + (0.1 \times \text{Nota por Avaliar})$$

---

## 9. Critérios de Qualidade e Conformidade com o Paradigma Funcional

Para garantir nota máxima e atender a todos os requisitos de avaliação docente e pelos pares, o projeto passará por um rigoroso checklist de conformidade:

- [x] **Zero Mutações de Estado:** Sem variáveis reatribuídas; todas as estruturas são congeladas (`frozen=True`, `frozenset`).
- [x] **Zero Loops Imperativos com Acumuladores:** Sem `for` ou `while` modificando listas ou contadores em memória.
- [x] **Isolamento de Efeitos Colaterais:** Código central em `implementation/` 100% livre de operações de escrita ou leitura externa não determinística.
- [x] **Testes Automatizados de Pureza:** Suíte de testes com `pytest` verificando que invocar funções múltiplas vezes com os mesmos argumentos produz idênticos resultados sem alterar parâmetros recebidos.
- [x] **Segurança Alimentar com Tolerância Zero:** Garantia matemática de que nenhum alérgeno declarado figurará nas sugestões finais.

---

## 10. Como Executar o Projeto (Guia Inicial)

### Pré-requisitos
* Python 3.10 ou superior
* Gerenciador de pacotes `pip`

### Instalação de Dependências
```bash
pip install -r requirements.txt
```

### Execução dos Testes Automatizados
```bash
pytest tests/ -v
```

### Execução da Interface
```bash
python3 -m interface.cli
```
