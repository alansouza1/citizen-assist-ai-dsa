# Documentação Técnica — Citizen Assist AI (DSA)

**Global Solution 2026.2 — Citizen Tech** · Disciplina: *Data Structures and Algorithms* · Linguagem: **Python 3 (somente biblioteca padrão)**

| Nome completo               | RM     | Modalidade |
| --------------------------- | ------ | ---------- |
| Alan Júnior Araújo de Souza | 574112 | Individual |

---

## Sumário

1. [Instruções de execução](#1-instruções-de-execução)
2. [Recorte escolhido](#2-recorte-escolhido)
3. [Modelo dos registros](#3-modelo-dos-registros)
4. [Estrutura da lista encadeada](#4-estrutura-da-lista-encadeada)
5. [Algoritmos de busca e ordenação](#5-algoritmos-de-busca-e-ordenação)
6. [Análise de complexidade (Big-O)](#6-análise-de-complexidade-big-o)
7. [Funcionamento do menu e validação](#7-funcionamento-do-menu-e-validação)
8. [Evidências de testes](#8-evidências-de-testes)
9. [Demonstração prática (log real)](#9-demonstração-prática-log-real)
10. [Atendimento aos requisitos do enunciado](#10-atendimento-aos-requisitos-do-enunciado)

---

## 1. Instruções de execução

Pré-requisito: **Python 3.8+**. Não há dependências externas nem etapa de compilação.

```bash
cd citizen-assist-ai-dsa
python main.py                    # menu interativo
python testes_dsa.py              # testes automatizados (código de saída 0 = todos passaram)
python testes_dsa.py --markdown   # tabela de evidências em Markdown
python demonstracao_dsa.py        # demonstração passo a passo dos nós
```

## 2. Recorte escolhido

O recorte é o **catálogo de serviços e orientações ao cidadão do Citizen Assist AI**, com foco em
jovens no primeiro emprego e cidadãos em geral. Cada registro descreve um serviço público
(documentação, saúde, assistência social, trabalho e renda, educação e qualificação, serviços urbanos):
o que é, quais documentos são exigidos e onde o atendimento é feito.

A carga inicial ([dados_iniciais.py](dados_iniciais.py)) contém **12 serviços** adaptados da base de
conhecimento do projeto Citizen Assist AI (fontes gov.br): CPF, CIN (novo RG), título de eleitor,
alistamento militar, Carteira de Trabalho Digital, seguro-desemprego, Jovem Aprendiz, Cartão SUS,
vacinação, CadÚnico, Tarifa Social de Energia e reclamação ao consumidor.
Os IDs são inseridos **propositalmente fora de ordem** (7, 2, 11, 1, 9, 5, 13, 3, 10, 6, 12, 4) para que
o efeito do Merge Sort fique visível.

Perguntas que o sistema responde:

- "Qual é o serviço de ID 9?" → consulta por ID (busca linear);
- "Quais serviços falam de *saúde*?" → pesquisa textual sem acento/maiúsculas;
- "Quais serviços existem, em ordem alfabética ou por categoria?" → Merge Sort;
- "Quantos serviços há por categoria e qual a porcentagem?" → análise.

## 3. Modelo dos registros

Classe `ServicoCidadao` ([models.py](models.py)) — usa `__slots__` para fixar os atributos:

| Atributo | Tipo | Regra de validação | Exemplo |
| --- | --- | --- | --- |
| `id` | `int` | inteiro > 0, **único na lista**, não editável | `9` |
| `titulo` | `str` | obrigatório, não vazio (espaços extras removidos) | `Cartão Nacional de Saúde (Cartão SUS)` |
| `categoria` | `str` | obrigatório | `Saúde` |
| `descricao` | `str` | obrigatório | `Identifica o cidadão no SUS...` |
| `requisitos` | `str` | obrigatório | `Documento de identificação com foto e CPF` |
| `local_atendimento` | `str` | obrigatório | `Qualquer UBS ou aplicativo Meu SUS Digital` |

Entradas como `"abc"`, `""`, `0`, `-5`, `True` ou `3.5` para o ID e textos vazios geram `ValueError`
com mensagem amigável, tratada pelo menu.

## 4. Estrutura da lista encadeada

Arquivo [lista_encadeada.py](lista_encadeada.py). Os registros **não** são armazenados em `list` nem
`dict`: cada um fica dentro de um objeto `No`, ligado ao próximo por referência.

```text
 class No:                         class ListaEncadeada:
   dado    -> ServicoCidadao         cabeca   -> primeiro No (ou None)
   proximo -> No | None              cauda    -> último No   (ou None)
                                     _tamanho -> int (contador mantido a cada operação)

          cabeca                                                   cauda
            │                                                        │
            ▼                                                        ▼
   ┌────────────────┬───┐    ┌────────────────┬───┐    ┌────────────────┬──────┐
   │ [7] Seguro-    │ ●─┼───►│ [2] CIN        │ ●─┼───►│ [11] CadÚnico  │ None │
   │ desemprego     │   │    │ (Documentação) │   │    │ (Assist. Soc.) │      │
   └────────────────┴───┘    └────────────────┴───┘    └────────────────┴──────┘
          dado     proximo         dado     proximo          dado      proximo
```

### 4.1 Operações

| Operação | Método | Como funciona (ponteiros) |
| --- | --- | --- |
| Inserção no fim | `inserir(servico)` | Percorre a lista procurando o ID (bloqueia duplicado com `IdDuplicadoError`); depois `cauda.proximo = novo` e `cauda = novo`. Lista vazia: `cabeca = cauda = novo`. |
| Inserção no início | `inserir_no_inicio(servico)` | Mesma checagem; `novo.proximo = cabeca`, `cabeca = novo`. |
| Percurso | `percorrer()` / `listar()` | `atual = cabeca`; enquanto `atual` não é `None`, visita e avança `atual = atual.proximo`. |
| Consulta por ID | `buscar_por_id(id)` | Percurso até achar o ID; devolve o registro ou `None`. |
| Atualização | `atualizar(id, **campos)` | Localiza o nó e altera **apenas `no.dado`**. Valida todos os campos antes de alterar qualquer um (atômico). Nenhum ponteiro muda. |
| Remoção | `remover(id)` | Localiza `(anterior, atual)`. Ver diagrama abaixo. |
| Limpeza | `limpar()` | `cabeca = cauda = None`, `_tamanho = 0` (nós liberados pelo coletor de lixo). |
| Estatísticas | `estatisticas()` | Um percurso contando por categoria; devolve total, quantidade e percentual. |
| Conversão controlada | `para_colecao()` / `reconstruir_de_colecao()` / `de_colecao()` | Copia referências para uma `list` só quando um algoritmo precisa de índice; a reconstrução valida tudo numa lista temporária antes de substituir os nós (nunca deixa estado inconsistente). |
| Integridade | `verificar_integridade()` | Confere ausência de ciclos, contador = nº de nós, `cauda` = último nó, `cauda.proximo is None`, IDs únicos. Usado nos testes e na demonstração. |

### 4.2 Remoção nos três pontos da lista

```text
INÍCIO  (remover 7)     antes:  cabeca─►[7]─►[2]─►[11]─►None
                        ação:   cabeca = cabeca.proximo
                        depois: cabeca─►[2]─►[11]─►None

MEIO    (remover 2)     antes:  [7]─►[2]─►[11]─►None
                        ação:   anterior.proximo = atual.proximo     ([7] "pula" [2])
                        depois: [7]─►[11]─►None

FIM     (remover 11)    antes:  [7]─►[2]─►[11]─►None   (cauda = [11])
                        ação:   anterior.proximo = None ; cauda = anterior
                        depois: [7]─►[2]─►None          (cauda = [2])
```

Em todos os casos o nó removido tem `proximo = None` (desligado) e `_tamanho` é decrementado.
Remover o único elemento deixa `cabeca = cauda = None`.

## 5. Algoritmos de busca e ordenação

Arquivo [algoritmos.py](algoritmos.py). Nenhum `.sort()`, `sorted()`, `index()`, `in` sobre lista de
registros ou `min/max` é usado para buscar ou ordenar.

### 5.1 Busca linear por ID — `busca_linear_por_id(lista, id)`

```text
atual ← cabeca ; comparacoes ← 0
enquanto atual ≠ None:
    comparacoes ← comparacoes + 1
    se atual.dado.id = id: devolve (atual.dado, comparacoes)     ← para imediatamente
    atual ← atual.proximo
devolve (None, comparacoes)                                       ← NÃO ENCONTRADO
```

Por que busca linear? A lista encadeada **não tem acesso por índice**, então a busca binária
não se aplica (chegar ao meio já custa O(n)). A busca sequencial é a escolha natural.

**Nenhum registro encontrado:** a função devolve `None` depois de visitar todos os *n* nós; o menu
mostra *"Nenhum registro encontrado com o ID X (n comparações)"*. Lista vazia → `(None, 0)`.

### 5.2 Pesquisa textual — `pesquisar_por_texto(lista, termo, campo)`

- `campo` ∈ {`titulo`, `categoria`, `ambos`};
- termo e campos são normalizados por `normalizar_texto()` (Unicode NFD, remoção de acentos, `casefold`
  e espaços colapsados), então `"SAUDE"`, `"saúde"` e `"  Saúde "` são equivalentes;
- é feita busca por **substring** em todos os nós (pode haver vários resultados);
- devolve `ResultadoBusca` (registros + nº de comparações). Sem resultado → `encontrou == False`
  e o menu exibe *"Nenhum registro encontrado para 'termo'"*;
- termo vazio ou campo inválido → `ValueError`.

### 5.3 Merge Sort sobre os nós — `merge_sort_lista(lista, criterio, decrescente)`

Divisão e conquista aplicada **diretamente à cadeia de nós**, apenas religando `proximo`:

1. **Dividir** (`_dividir`): ponteiros *lento/rápido* (tartaruga e lebre). Quando o rápido chega
   ao fim, o lento está no meio; faz-se `lento.proximo = None`, criando duas sublistas.
2. **Conquistar** (`_merge_sort_nos`): ordena recursivamente cada metade (caso base: 0 ou 1 nó).
3. **Combinar** (`_intercalar`): com um **nó sentinela**, compara as cabeças das duas cadeias e
   encadeia a menor em `ultimo.proximo`; quando uma acaba, a outra é anexada inteira.
4. No fim, `lista.cabeca` recebe a nova cabeça e `lista.cauda` é recalculada.

```text
[7]→[2]→[11]→[1]                              dividir
     ┌─────────┴─────────┐
 [7]→[2]            [11]→[1]                   dividir
  ┌──┴──┐            ┌──┴──┐
 [7]   [2]         [11]   [1]                  caso base
  └──┬──┘            └──┬──┘
 [2]→[7]            [1]→[11]                   intercalar
     └─────────┬─────────┘
   [1]→[2]→[7]→[11]                            intercalar (mesmos nós, novos ponteiros)
```

Critérios (`chave_ordenacao`):

| Critério | Chave comparada |
| --- | --- |
| `id` | o inteiro `id` |
| `titulo` | (título normalizado, id) |
| `categoria` | (categoria normalizada, título normalizado, id) |

O algoritmo é **estável** (em empate, o nó da metade esquerda vem primeiro, `<=`) e a ordem
decrescente usa `>=`. Os testes provam que o conjunto de objetos `No` é o mesmo antes e depois:
**nenhum registro é copiado**.

**Versão com coleção auxiliar** (`ordenar_via_colecao`): converte a lista em `list`
(`para_colecao`), aplica `merge_sort_vetor` (Merge Sort manual em vetor) e reconstrói a lista
(`reconstruir_de_colecao`). Existe para demonstrar a conversão controlada e servir de oráculo nos
testes — o menu usa a versão sobre nós, que não precisa de memória O(n).

## 6. Análise de complexidade (Big-O)

Notação: **n** = número de registros; **m** = tamanho médio dos textos comparados;
**k** = número de resultados/categorias.

### 6.1 Tabela-resumo

| Operação | Melhor caso | Caso médio | Pior caso | Espaço extra |
| --- | --- | --- | --- | --- |
| `inserir` (fim, com checagem de duplicado) | Θ(n) (sucesso) / O(1) (duplicado na cabeça) | Θ(n) | Θ(n) | O(1) |
| `inserir_no_inicio` | idem | Θ(n) | Θ(n) | O(1) |
| `buscar_por_id` / `busca_linear_por_id` | O(1) | O(n) | O(n) | O(1) |
| `pesquisar_por_texto` | Θ(n·m) | Θ(n·m) | Θ(n·m) | O(k + m) |
| `atualizar` | O(1) | O(n) | O(n) | O(1)¹ |
| `remover` (início/meio/fim) | O(1) | O(n) | O(n) | O(1) |
| `listar` / `percorrer` | Θ(n) | Θ(n) | Θ(n) | O(1) gerador / O(n) linhas |
| `estatisticas` | Θ(n) | O(n·k) | O(n²) se todas as categorias forem distintas | O(k) |
| `merge_sort_lista` (nós) | Θ(n log n) | Θ(n log n) | Θ(n log n) | **O(log n)** (pilha de recursão) |
| `ordenar_via_colecao` (vetor) | Θ(n log n) + O(n²)² | Θ(n log n) + O(n²)² | idem | O(n) |
| `para_colecao` | Θ(n) | Θ(n) | Θ(n) | O(n) |
| `limpar` | O(1) | O(1) | O(1) | O(1) |

¹ Uma cópia de 6 campos (tamanho constante) é criada para validar a atualização de forma atômica.
² A reconstrução reutiliza `inserir`, que checa duplicidade em O(i) para o i-ésimo elemento: Σi = n(n−1)/2.
É o preço da garantia de integridade; por isso o menu usa a ordenação sobre os nós.

### 6.2 Justificativas

**Inserção.** Encadear o nó no fim custa **O(1)** porque a lista mantém o ponteiro `cauda`
(sem ele seria preciso percorrer até o último nó). Porém, para garantir a unicidade do `id`,
`contem_id` percorre a lista: uma inserção bem-sucedida faz exatamente *n* comparações,
logo **Θ(n)** em todos os casos de sucesso. O único "melhor caso" O(1) é a rejeição de um duplicado
que está na cabeça. Inserir *n* registros a partir da lista vazia custa
0 + 1 + … + (n−1) = n(n−1)/2 = **Θ(n²)** no total. Espaço: um nó novo, O(1).

**Consulta por ID (busca linear).** Se o alvo está na posição *i* (1 ≤ i ≤ n), são feitas *i*
comparações.
- Melhor caso: alvo na cabeça → 1 comparação → **O(1)** (teste 22: 1 comparação).
- Caso médio (alvo presente, posição uniforme): (1 + 2 + … + n)/n = (n+1)/2 → **O(n)**.
- Pior caso: alvo na cauda ou ausente → *n* comparações → **O(n)** (teste 23: 12 comparações para n = 12).
- Espaço: apenas o ponteiro `atual` → **O(1)**.

**Pesquisa por título/categoria.** Como pode haver vários resultados, a busca **nunca para cedo**:
visita sempre os *n* nós, e em cada um normaliza e procura a substring em O(m). Portanto
**Θ(n·m)** em todos os casos (com `ambos`, até 2n verificações — o teste 28 mostra 24 = 2·12).
Espaço: lista de *k* resultados + string normalizada O(m).

**Atualização.** Localizar o nó é uma busca linear (O(1) / O(n) / O(n)); validar e atribuir os
campos é O(c·m) com c = 6 constante. Como apenas `no.dado` muda, os ponteiros ficam intactos
(teste 31 verifica que o nó e o seu `proximo` são os mesmos objetos).

**Remoção.** O custo está em encontrar `(anterior, atual)`: O(1) se o nó é a cabeça; O(n) no meio
ou no fim. A religação (`cabeca = atual.proximo` ou `anterior.proximo = atual.proximo`, e
`cauda = anterior` se necessário) é **O(1)**. Em lista simplesmente encadeada, remover a cauda é O(n)
mesmo com o ponteiro `cauda`, porque é preciso conhecer o **anterior**.

**Merge Sort sobre os nós.**
A recorrência é

```text
T(n) = 2·T(n/2) + Θ(n)        (Θ(n/2) para achar o meio + Θ(n) para intercalar)
T(1) = Θ(1)
```

Pelo **Teorema Mestre** (a = 2, b = 2, f(n) = Θ(n) = Θ(n^(log_b a))) → **T(n) = Θ(n log n)**.
Intuitivamente: a árvore de recursão tem ⌈log₂ n⌉ níveis e, em cada nível, todos os *n* nós são
percorridos uma vez na divisão e uma vez na intercalação.

Diferentemente do Quick Sort, a divisão **não depende dos dados** (sempre ao meio), por isso o
Merge Sort é Θ(n log n) também no melhor e no pior caso. Só o número de comparações varia:
- melhor caso (uma metade inteira menor que a outra): ≈ (n/2)·log₂ n comparações —
  teste 47: lista já ordenada com n = 8 → **12** comparações = (8/2)·3;
- pior caso (intercalações alternadas): n·⌈log₂ n⌉ − 2^⌈log₂ n⌉ + 1 comparações —
  para n = 12: 12·4 − 16 + 1 = 33 (observado nos dados iniciais: 31 por ID, 31 por título, 30 por categoria);
- n = 200 aleatório: **1276** comparações (n·log₂ n ≈ 1529).

Espaço: a intercalação é **iterativa e reaproveita os próprios nós** (só ponteiros mudam e há
um nó sentinela), então o espaço extra é apenas a pilha de recursão, de profundidade
⌈log₂ n⌉ → **O(log n)**. A versão em vetor (`merge_sort_vetor`) precisa de **O(n)** de memória
auxiliar para as sublistas — essa é a principal vantagem de ordenar a lista encadeada
diretamente. Observação: a chave textual é normalizada a cada comparação (custo O(m)), então o
custo real por título/categoria é Θ(n log n · m); o recálculo da cauda ao final soma Θ(n),
que não altera a ordem de grandeza.

### 6.3 Comparação empírica (comparações contadas pelos próprios algoritmos)

| Cenário | n | Comparações observadas | Referência teórica |
| --- | --- | --- | --- |
| Busca por ID na cabeça (id 7) | 12 | 1 | melhor caso = 1 |
| Busca por ID no meio (id 9) | 12 | 5 | posição 5 |
| Busca por ID inexistente (999) | 12 | 12 | pior caso = n |
| Pesquisa sem resultado (`ambos`) | 12 | 24 | 2n |
| Merge Sort por ID, dados iniciais | 12 | 31 | ≤ 33 (pior caso) |
| Merge Sort lista já ordenada | 8 | 12 | (n/2)·log₂ n = 12 |
| Merge Sort aleatório (nós) | 200 | 1276 | n·log₂ n ≈ 1529 |
| Merge Sort aleatório (vetor) | 200 | 1284 | idem (divisão ⌊n/2⌋ em vez de ⌈n/2⌉) |

## 7. Funcionamento do menu e validação

Arquivo [main.py](main.py). O laço principal mostra o menu, lê a opção e chama a função
correspondente. Cada operação roda dentro de um `try/except` que transforma as exceções do
domínio em mensagens — **nunca é exibido traceback**.

| Opção | Ação | Observações |
| --- | --- | --- |
| 1 | Cadastrar serviço | Valida o ID **antes** de pedir os demais campos (avisa duplicado na hora); cada campo de texto tem até 3 tentativas. |
| 2 | Listar todos | Percurso cabeça → cauda e total. |
| 3 | Consultar por ID | Busca linear, mostra o registro completo e o nº de comparações. |
| 4 | Pesquisar por título/categoria | Escolha do campo (1/2/3, padrão 3) e termo. |
| 5 | Atualizar registro | Mostra os dados atuais; Enter mantém o valor; ID não é editável. |
| 6 | Excluir registro | Mostra o registro e pede confirmação (s/n). Exibe o encadeamento resultante. |
| 7 | Ordenar | Critério (1-ID, 2-Título, 3-Categoria) e ordem (crescente/decrescente); mostra o encadeamento antes/depois e as comparações. |
| 8 | Análise por categoria | Total, quantidade, percentual, barra e categoria mais frequente. |
| 9 | Dados iniciais / limpar | 1 carrega os 12 serviços (ignora IDs já existentes); 2 limpa com confirmação. |
| 0 | Encerrar | — |

| Situação inválida | Tratamento |
| --- | --- |
| Opção inexistente (`abc`, `42`) ou vazia | `[!] Opção inexistente: 'abc'. Digite um número de 0 a 9.` |
| ID não numérico / ≤ 0 / vazio (`ValueError`) | `[!] Entrada inválida: O ID deve ser um número inteiro...` |
| ID duplicado | `[!] ID duplicado: Já existe um registro com o ID 1. Escolha outro ID.` |
| Campo de texto vazio | `[!] O campo 'Título' não pode ficar vazio.` (nova tentativa) |
| Registro inexistente | `[i] Nenhum registro encontrado com o ID 999 (12 comparações).` |
| Pesquisa sem resultado | `[i] Nenhum registro encontrado para 'xyz' (24 comparações).` |
| Lista vazia (opções 2–8) | `[i] A lista está vazia: não há registros para listar.` + dica da opção 9 |
| Critério/campo inexistente | `[!] Critério inexistente: '5'. Use 1, 2 ou 3.` |
| Ctrl+C / Ctrl+D | Cancela a operação atual ou encerra o programa com mensagem amigável. |

## 8. Evidências de testes

Comando: `python testes_dsa.py --markdown` — execução real em <!-- DATA:INICIO -->16/11/2026 23:12 (Python 3.15.2)<!-- DATA:FIM -->.
Os testes usam `assert` e cobrem: validação do modelo, **todas as operações com lista vazia**,
inserção e IDs duplicados, consultas (existente/inexistente/inválida), pesquisas (com e sem
resultado), atualização (válida, inexistente, inválida e atômica), remoção no início/meio/fim/único,
Merge Sort por ID/título/categoria (crescente e decrescente, estabilidade, reutilização dos nós,
200 registros aleatórios comparados com o oráculo em vetor), estatísticas, conversão controlada e o
**menu interativo** com entradas simuladas (verificando a ausência de traceback).

<!-- TESTES:INICIO -->
| # | Caso de teste | Entrada | Resultado esperado | Resultado observado | Status |
|---|---|---|---|---|---|
| 1 | Criar ServicoCidadao válido | id=1, campos preenchidos | Objeto criado com campos sem espaços extras | id=1, titulo='CPF' | ✅ PASSOU |
| 2 | ID não numérico | id='abc' | ValueError | ValueError: O ID deve ser um número inteiro (recebido: 'abc'). | ✅ PASSOU |
| 3 | ID zero/negativo | id=0 e id=-5 | ValueError nos dois casos | ValueError: O ID deve ser maior que zero (recebido: -5). | ✅ PASSOU |
| 4 | ID vazio / bool / float | id='', True, 3.5 | ValueError nos três casos | ValueError: O ID deve ser um número inteiro positivo. | ✅ PASSOU |
| 5 | Campo de texto vazio | titulo='   ' | ValueError | ValueError: O campo 'Título' não pode ficar vazio. | ✅ PASSOU |
| 6 | Lista vazia: estado inicial | ListaEncadeada() | len=0, cabeca=cauda=None, integra | HEAD -> None   (tamanho=0, cabeca=None, cauda=None) | ✅ PASSOU |
| 7 | Lista vazia: listar/percorrer | listar() | [] (nenhuma linha) | listar() -> [] | ✅ PASSOU |
| 8 | Lista vazia: consultar por ID | buscar_por_id(1) / busca_linear_por_id(1) | None com 0 comparações | None, comparacoes=0 | ✅ PASSOU |
| 9 | Lista vazia: pesquisar texto | pesquisar('cpf') | Nenhum resultado (encontrou=False) | encontrou=False, registros=[] | ✅ PASSOU |
| 10 | Lista vazia: atualizar | atualizar(1, titulo='X') | ListaVaziaError | ListaVaziaError: A lista está vazia: não há registros para atualizar. | ✅ PASSOU |
| 11 | Lista vazia: remover | remover(1) | ListaVaziaError | ListaVaziaError: A lista está vazia: não há registros para remover. | ✅ PASSOU |
| 12 | Lista vazia: ordenar (Merge Sort) | merge_sort_lista(vazia, 'titulo') | 0 comparações, lista íntegra | comparacoes=0, cabeca=None | ✅ PASSOU |
| 13 | Lista vazia: estatísticas | estatisticas() | total=0, categorias=[] | {'total': 0, 'categorias': []} | ✅ PASSOU |
| 14 | Lista vazia: limpar / converter | limpar(), para_colecao() | 0 removidos, colecao [] | limpar()=0, para_colecao()=[] | ✅ PASSOU |
| 15 | Inserir primeiro registro | inserir(id=10) | cabeca=cauda=No(10), len=1 | HEAD -> [10] -> None   (tamanho=1, cabeca=10, cauda=10) | ✅ PASSOU |
| 16 | Inserir vários (no fim) | ids 3, 1, 2 | Ordem de inserção preservada: 3->1->2 | HEAD -> [3] -> [1] -> [2] -> None   (tamanho=3, cabeca=3, cauda=2) | ✅ PASSOU |
| 17 | Inserir no início | lista 3->1; inserir_no_inicio(9) | 9->3->1 | HEAD -> [9] -> [3] -> [1] -> None   (tamanho=3, cabeca=9, cauda=1) | ✅ PASSOU |
| 18 | ID duplicado bloqueado | lista 1->2; inserir(id=2) | IdDuplicadoError e lista inalterada | IdDuplicadoError: Já existe um registro com o ID 2. \| lista=[1, 2] | ✅ PASSOU |
| 19 | Inserir tipo inválido | inserir('texto') | TypeError | TypeError: Somente objetos ServicoCidadao podem ser inseridos. | ✅ PASSOU |
| 20 | Carga inicial + recarga | carregar 2x | 12 inseridos; depois 0 inseridos/12 ignorados | 1a carga=(12, 0), 2a carga=(0, 12) | ✅ PASSOU |
| 21 | Consultar ID existente (meio) | dados iniciais; busca_linear_por_id(9) | Cartão SUS, 5 comparações | [9] Cartão Nacional de Saúde (Cartão SUS) (Saúde), comparacoes=5 | ✅ PASSOU |
| 22 | Consultar ID na cabeça (melhor caso) | busca_linear_por_id(7) | 1 comparação | [7] Pedir o seguro-desemprego (Trabalho e Renda), comparacoes=1 | ✅ PASSOU |
| 23 | Consultar ID inexistente (pior caso) | busca_linear_por_id(999) | None após n=12 comparações | None, comparacoes=12 | ✅ PASSOU |
| 24 | Consultar com ID inválido | buscar_por_id('x') | ValueError | ValueError: O ID deve ser um número inteiro (recebido: 'x'). | ✅ PASSOU |
| 25 | Pesquisa por título sem acento/maiúsculas | titulo contém 'CARTAO' | Somente id 9 ('Cartão Nacional de Saúde') | ids=[9], comparacoes=12 | ✅ PASSOU |
| 26 | Pesquisa por categoria | categoria contém 'documentacao' | 4 registros: [2, 1, 3, 4] | ids=[2, 1, 3, 4] | ✅ PASSOU |
| 27 | Pesquisa em ambos os campos | 'saude' em título ou categoria | [9, 10] | ids=[9, 10], comparacoes=23 | ✅ PASSOU |
| 28 | Pesquisa sem resultado | 'passaporte' | encontrou=False, lista vazia de resultados | encontrou=False, comparacoes=24 | ✅ PASSOU |
| 29 | Pesquisa com termo vazio / campo inválido | termo='  ' ; campo='local' | ValueError nos dois casos | ValueError: Campo de pesquisa inválido: 'local'. Use titulo, categoria ou ambos. | ✅ PASSOU |
| 30 | Normalização de texto | normalizar('  SAÚDE   e Educação ') | 'saude e educacao' | 'saude e educacao' | ✅ PASSOU |
| 31 | Atualizar campos existentes | atualizar(5, titulo, local) | Campos alterados, mesmo nó e encadeamento | alterados=['titulo', 'local_atendimento'], ids=[1, 5, 8] | ✅ PASSOU |
| 32 | Atualizar ID inexistente | atualizar(99, titulo='X') | RegistroNaoEncontradoError | RegistroNaoEncontradoError: Nenhum registro com o ID 99. | ✅ PASSOU |
| 33 | Atualizar com valor vazio (atômico) | atualizar(1, titulo='Novo', categoria='') | ValueError e nada alterado | ValueError: O campo 'Categoria' não pode ficar vazio. \| titulo mantido | ✅ PASSOU |
| 34 | Atualizar campo proibido/inexistente | atualizar(1, id=7) ; atualizar(1, cor='x') | ValueError nos dois casos | ValueError: Campo inexistente: 'cor'. | ✅ PASSOU |
| 35 | Remover do início | lista 1->2->3; remover(1) | 2->3, cabeca=2 | HEAD -> [2] -> [3] -> None   (tamanho=2, cabeca=2, cauda=3) | ✅ PASSOU |
| 36 | Remover do meio | lista 1->2->3; remover(2) | 1->3 (1.proximo aponta p/ 3) | HEAD -> [1] -> [3] -> None   (tamanho=2, cabeca=1, cauda=3) | ✅ PASSOU |
| 37 | Remover do fim | lista 1->2->3; remover(3) | 1->2, cauda=2, cauda.proximo=None | após remover(3) e inserir(4): HEAD -> [1] -> [2] -> [4] -> None   (tamanho=3, cabeca=1, cauda=4) | ✅ PASSOU |
| 38 | Remover único elemento | lista 7; remover(7) | Lista vazia, cabeca=cauda=None | HEAD -> None   (tamanho=0, cabeca=None, cauda=None) | ✅ PASSOU |
| 39 | Remover ID inexistente | lista 1->2; remover(50) | RegistroNaoEncontradoError, lista intacta | RegistroNaoEncontradoError: Nenhum registro com o ID 50. | ✅ PASSOU |
| 40 | Remover com ID inválido | remover('dois') | ValueError | ValueError: O ID deve ser um número inteiro (recebido: 'dois'). | ✅ PASSOU |
| 41 | Merge Sort por ID (crescente) | dados iniciais (ordem 7,2,11,...) | [1,2,3,4,5,6,7,9,10,11,12,13] | ids=[1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13], comparacoes=31 | ✅ PASSOU |
| 42 | Merge Sort por ID (decrescente) | decrescente=True | [13,12,...,1] | ids=[13, 12, 11, 10, 9, 7, 6, 5, 4, 3, 2, 1] | ✅ PASSOU |
| 43 | Merge Sort por título | critério 'titulo' | Títulos em ordem alfabética (sem acento) | 1o='Alistamento militar obrigatório' ... ultimo='Vacinação gratuita e caderneta' | ✅ PASSOU |
| 44 | Merge Sort por categoria | critério 'categoria' | Assistência Social primeiro, Trabalho e Renda por último | categorias=['Assistência Social', 'Assistência Social', 'Documentação', 'Documentação', 'Documentação', 'Documentação', 'Educação e Qualificação', 'Saúde', 'Saúde', 'Serviços Urbanos', 'Trabalho e Renda', 'Trabalho e Renda'] | ✅ PASSOU |
| 45 | Merge Sort reutiliza os mesmos nós | ordenar por id | Mesmo conjunto de objetos No (só ponteiros mudam) | 12 nós antes = 12 nós depois (mesmas referências) | ✅ PASSOU |
| 46 | Merge Sort: empate de categoria | 3 registros mesma categoria (ids 3,1,2) | Empate desfeito por título e depois id | ids=[1, 2, 3] | ✅ PASSOU |
| 47 | Merge Sort 1 elemento / já ordenada | lista 5 ; lista 1..8 | 0 comparações ; ordem mantida | 1 elem: 0 comp; já ordenada (n=8): 12 comp (melhor caso n/2*log2 n = 12) | ✅ PASSOU |
| 48 | Merge Sort aleatório (200 registros) | ids embaralhados, seed=2026 | Ordenado de 1 a 200; igual ao Merge Sort via coleção | ordenado; comparacoes nós=1276, colecao=1284 (n log2 n ~ 1529) | ✅ PASSOU |
| 49 | Critério de ordenação inválido | merge_sort_lista(l, 'local') | ValueError, lista intacta | ValueError: Critério de ordenação inválido: 'local'. Use id, titulo ou categoria. | ✅ PASSOU |
| 50 | Estatísticas por categoria | dados iniciais | total=12; Documentação=4 (33.33%) | total=12, categorias=6, Documentação=(4, 33.33) | ✅ PASSOU |
| 51 | Conversão lista -> coleção -> lista | para_colecao() e de_colecao() | Mesma ordem; original intacta | colecao com 12 itens; reconstruída íntegra | ✅ PASSOU |
| 52 | Reconstrução rejeita duplicados | reconstruir_de_colecao([1, 2, 1]) | IdDuplicadoError, lista original preservada | IdDuplicadoError: Já existe um registro com o ID 1. | ✅ PASSOU |
| 53 | CRUD completo em sequência | inserir 3, atualizar, remover, consultar | Estado final consistente | HEAD -> [2] -> [11] -> None   (tamanho=2, cabeca=2, cauda=11) | ✅ PASSOU |
| 54 | Menu: opções inexistentes e vazias | 'abc', '', '42', '0' | Mensagens de erro, sem traceback | 3 avisos exibidos; encerrou normalmente | ✅ PASSOU |
| 55 | Menu: operações 2-8 com lista vazia | 2,3,4,5,6,7,8 e 9->2 | Aviso 'lista está vazia' em todas | 7 avisos de lista vazia + 'lista já está vazia' | ✅ PASSOU |
| 56 | Menu: cadastro com ID inválido e duplicado | 1->'x' ; 9->1 ; 1->'7' | Entrada inválida ; ID duplicado | ValueError e duplicidade tratados; len=12 | ✅ PASSOU |
| 57 | Menu: cadastro válido com campo vazio repetido | 1->20, título '' e depois 'Emitir passaporte'... | Registro 20 cadastrado | aviso de campo vazio + cadastro OK; ids=[20] | ✅ PASSOU |
| 58 | Menu: consulta, pesquisa, atualização e exclusão | fluxo 9,3,4,5,6,7,8 | Todas as operações concluídas | 11 registros ao final; nenhum traceback | ✅ PASSOU |
| 59 | Menu: Ctrl+D (EOF) no meio de uma operação | 1 -> EOF | Encerra sem traceback | operação cancelada e menu encerrado | ✅ PASSOU |

**RESUMO: 59/59 testes passaram, 0 falharam.** (código de saída `0`). Log em texto: [evidencias/saida_testes.txt](evidencias/saida_testes.txt).
<!-- TESTES:FIM -->

## 9. Demonstração prática (log real)

Comando: `python demonstracao_dsa.py`. Cada passo imprime o encadeamento `HEAD -> ... -> None`,
o tamanho, a cabeça, a cauda e uma tabela com o `proximo` de cada nó (rótulo `N<id>`), além da
verificação de integridade.

<!-- DEMO:INICIO -->
```text
$ python demonstracao_dsa.py
CITIZEN ASSIST AI - DEMONSTRAÇÃO PRÁTICA DA LISTA ENCADEADA (DSA)
Aluno: Alan Júnior Araújo de Souza - RM 574112 (Individual)

========================================================================
PASSO 01 - Lista vazia recém-criada
========================================================================
Estado: HEAD -> None   (tamanho=0, cabeca=None, cauda=None)
   (nenhum nó: cabeca = None, cauda = None)

========================================================================
PASSO 02 - Inserção do primeiro registro (id 7) - cabeça e cauda apontam para o mesmo nó
========================================================================
Depois: HEAD -> [7] -> None   (tamanho=1, cabeca=7, cauda=7)
   pos  nó     dado                                       proximo -> 
   1    N7     [7] Pedir o seguro-desemprego (Trabalho... None        CABEÇA/CAUDA
   Integridade verificada: OK

========================================================================
PASSO 03 - Inserções no fim (ids 2, 11, 1, 9) - a antiga cauda passa a apontar para o novo nó
========================================================================
   inserir(2): N7.proximo = N2 ; cauda = N2
   inserir(11): N2.proximo = N11 ; cauda = N11
   inserir(1): N11.proximo = N1 ; cauda = N1
   inserir(9): N1.proximo = N9 ; cauda = N9
Depois: HEAD -> [7] -> [2] -> [11] -> [1] -> [9] -> None   (tamanho=5, cabeca=7, cauda=9)
   pos  nó     dado                                       proximo -> 
   1    N7     [7] Pedir o seguro-desemprego (Trabalho... N2          CABEÇA
   2    N2     [2] Carteira de Identidade Nacional (CI... N11         
   3    N11    [11] Inscrição no Cadastro Único (CadÚn... N1          
   4    N1     [1] Tirar o CPF pela primeira vez (Docu... N9          
   5    N9     [9] Cartão Nacional de Saúde (Cartão SU... None        CAUDA
   Integridade verificada: OK

========================================================================
PASSO 04 - Tentativa de inserir ID duplicado (id 11)
========================================================================
   Bloqueado -> IdDuplicadoError: Já existe um registro com o ID 11.
Lista inalterada: HEAD -> [7] -> [2] -> [11] -> [1] -> [9] -> None   (tamanho=5, cabeca=7, cauda=9)
   pos  nó     dado                                       proximo -> 
   1    N7     [7] Pedir o seguro-desemprego (Trabalho... N2          CABEÇA
   2    N2     [2] Carteira de Identidade Nacional (CI... N11         
   3    N11    [11] Inscrição no Cadastro Único (CadÚn... N1          
   4    N1     [1] Tirar o CPF pela primeira vez (Docu... N9          
   5    N9     [9] Cartão Nacional de Saúde (Cartão SU... None        CAUDA
   Integridade verificada: OK

========================================================================
PASSO 05 - Consulta por ID com busca linear (existente, cabeça e inexistente)
========================================================================
   busca_linear_por_id(1): [1] Tirar o CPF pela primeira vez (Documentação) após 4 comparação(ões)
   busca_linear_por_id(7): [7] Pedir o seguro-desemprego (Trabalho e Renda) após 1 comparação(ões)
   busca_linear_por_id(99): NÃO ENCONTRADO após 5 comparações (percorreu tudo)

========================================================================
PASSO 06 - Pesquisa textual (sem acento / sem maiúsculas)
========================================================================
   pesquisar('DOCUMENTACAO', categoria): 2 resultado(s) -> [2] Carteira de Identidade Nacional (CIN) (Documentação), [1] Tirar o CPF pela primeira vez (Documentação)
   pesquisar('cartão', titulo): 1 resultado(s) -> [9] Cartão Nacional de Saúde (Cartão SUS) (Saúde)
   pesquisar('passaporte', ambos): nenhum registro encontrado (10 comparações)

========================================================================
PASSO 07 - Atualização do registro 11 - só o dado muda, os ponteiros são preservados
========================================================================
Antes : HEAD -> [7] -> [2] -> [11] -> [1] -> [9] -> None   (tamanho=5, cabeca=7, cauda=9)
   pos  nó     dado                                       proximo -> 
   1    N7     [7] Pedir o seguro-desemprego (Trabalho... N2          CABEÇA
   2    N2     [2] Carteira de Identidade Nacional (CI... N11         
   3    N11    [11] Inscrição no Cadastro Único (CadÚn... N1          
   4    N1     [1] Tirar o CPF pela primeira vez (Docu... N9          
   5    N9     [9] Cartão Nacional de Saúde (Cartão SU... None        CAUDA
   Integridade verificada: OK
   Local antes : CRAS ou posto de cadastramento do município
   Campos alterados: ['local_atendimento']
   Local depois: CRAS do município ou app Cadastro Único
   Mesmo nó? True | mesmo proximo? True
Depois: HEAD -> [7] -> [2] -> [11] -> [1] -> [9] -> None   (tamanho=5, cabeca=7, cauda=9)
   pos  nó     dado                                       proximo -> 
   1    N7     [7] Pedir o seguro-desemprego (Trabalho... N2          CABEÇA
   2    N2     [2] Carteira de Identidade Nacional (CI... N11         
   3    N11    [11] Inscrição no Cadastro Único (CadÚn... N1          
   4    N1     [1] Tirar o CPF pela primeira vez (Docu... N9          
   5    N9     [9] Cartão Nacional de Saúde (Cartão SU... None        CAUDA
   Integridade verificada: OK

========================================================================
PASSO 08 - Remoção no INÍCIO (id 7) - cabeça avança para o segundo nó
========================================================================
Antes : HEAD -> [7] -> [2] -> [11] -> [1] -> [9] -> None   (tamanho=5, cabeca=7, cauda=9)
   pos  nó     dado                                       proximo -> 
   1    N7     [7] Pedir o seguro-desemprego (Trabalho... N2          CABEÇA
   2    N2     [2] Carteira de Identidade Nacional (CI... N11         
   3    N11    [11] Inscrição no Cadastro Único (CadÚn... N1          
   4    N1     [1] Tirar o CPF pela primeira vez (Docu... N9          
   5    N9     [9] Cartão Nacional de Saúde (Cartão SU... None        CAUDA
   Integridade verificada: OK
   removido: [7] Pedir o seguro-desemprego (Trabalho e Renda)
Depois: HEAD -> [2] -> [11] -> [1] -> [9] -> None   (tamanho=4, cabeca=2, cauda=9)
   pos  nó     dado                                       proximo -> 
   1    N2     [2] Carteira de Identidade Nacional (CI... N11         CABEÇA
   2    N11    [11] Inscrição no Cadastro Único (CadÚn... N1          
   3    N1     [1] Tirar o CPF pela primeira vez (Docu... N9          
   4    N9     [9] Cartão Nacional de Saúde (Cartão SU... None        CAUDA
   Integridade verificada: OK

========================================================================
PASSO 09 - Remoção no MEIO (id 11) - o anterior passa a apontar para o sucessor
========================================================================
Antes : HEAD -> [2] -> [11] -> [1] -> [9] -> None   (tamanho=4, cabeca=2, cauda=9)
   pos  nó     dado                                       proximo -> 
   1    N2     [2] Carteira de Identidade Nacional (CI... N11         CABEÇA
   2    N11    [11] Inscrição no Cadastro Único (CadÚn... N1          
   3    N1     [1] Tirar o CPF pela primeira vez (Docu... N9          
   4    N9     [9] Cartão Nacional de Saúde (Cartão SU... None        CAUDA
   Integridade verificada: OK
   removido: [11] Inscrição no Cadastro Único (CadÚnico) (Assistência Social)
Depois: HEAD -> [2] -> [1] -> [9] -> None   (tamanho=3, cabeca=2, cauda=9)
   pos  nó     dado                                       proximo -> 
   1    N2     [2] Carteira de Identidade Nacional (CI... N1          CABEÇA
   2    N1     [1] Tirar o CPF pela primeira vez (Docu... N9          
   3    N9     [9] Cartão Nacional de Saúde (Cartão SU... None        CAUDA
   Integridade verificada: OK

========================================================================
PASSO 10 - Remoção no FIM (id 9) - a cauda recua para o anterior
========================================================================
Antes : HEAD -> [2] -> [1] -> [9] -> None   (tamanho=3, cabeca=2, cauda=9)
   pos  nó     dado                                       proximo -> 
   1    N2     [2] Carteira de Identidade Nacional (CI... N1          CABEÇA
   2    N1     [1] Tirar o CPF pela primeira vez (Docu... N9          
   3    N9     [9] Cartão Nacional de Saúde (Cartão SU... None        CAUDA
   Integridade verificada: OK
   removido: [9] Cartão Nacional de Saúde (Cartão SUS) (Saúde)
Depois: HEAD -> [2] -> [1] -> None   (tamanho=2, cabeca=2, cauda=1)
   pos  nó     dado                                       proximo -> 
   1    N2     [2] Carteira de Identidade Nacional (CI... N1          CABEÇA
   2    N1     [1] Tirar o CPF pela primeira vez (Docu... None        CAUDA
   Integridade verificada: OK

========================================================================
PASSO 11 - Remoção de ID inexistente (id 50)
========================================================================
   RegistroNaoEncontradoError: Nenhum registro com o ID 50.
Lista inalterada: HEAD -> [2] -> [1] -> None   (tamanho=2, cabeca=2, cauda=1)
   pos  nó     dado                                       proximo -> 
   1    N2     [2] Carteira de Identidade Nacional (CI... N1          CABEÇA
   2    N1     [1] Tirar o CPF pela primeira vez (Docu... None        CAUDA
   Integridade verificada: OK

========================================================================
PASSO 12 - Carga dos dados iniciais do Citizen Assist AI (ids já existentes são ignorados)
========================================================================
   inseridos=10, ignorados=2
Depois: HEAD -> [2] -> [1] -> [7] -> [11] -> [9] -> [5] -> [13] -> [3] -> [10] -> [6] -> [12] -> [4] -> None   (tamanho=12, cabeca=2, cauda=4)
   pos  nó     dado                                       proximo -> 
   1    N2     [2] Carteira de Identidade Nacional (CI... N1          CABEÇA
   2    N1     [1] Tirar o CPF pela primeira vez (Docu... N7          
   3    N7     [7] Pedir o seguro-desemprego (Trabalho... N11         
   4    N11    [11] Inscrição no Cadastro Único (CadÚn... N9          
   5    N9     [9] Cartão Nacional de Saúde (Cartão SU... N5          
   6    N5     [5] Carteira de Trabalho Digital (Traba... N13         
   7    N13    [13] Tarifa Social de Energia Elétrica ... N3          
   8    N3     [3] Primeiro título de eleitor (Documen... N10         
   9    N10    [10] Vacinação gratuita e caderneta (Sa... N6          
   10   N6     [6] Programa Jovem Aprendiz (Educação e... N12         
   11   N12    [12] Reclamação de direitos do consumid... N4          
   12   N4     [4] Alistamento militar obrigatório (Do... None        CAUDA
   Integridade verificada: OK

========================================================================
PASSO 13 - Merge Sort por id (crescente) - religação dos nós existentes
========================================================================
Antes : HEAD -> [2] -> [1] -> [7] -> [11] -> [9] -> [5] -> [13] -> [3] -> [10] -> [6] -> [12] -> [4] -> None   (tamanho=12, cabeca=2, cauda=4)
Depois: HEAD -> [1] -> [2] -> [3] -> [4] -> [5] -> [6] -> [7] -> [9] -> [10] -> [11] -> [12] -> [13] -> None   (tamanho=12, cabeca=1, cauda=13)
   pos  nó     dado                                       proximo -> 
   1    N1     [1] Tirar o CPF pela primeira vez (Docu... N2          CABEÇA
   2    N2     [2] Carteira de Identidade Nacional (CI... N3          
   3    N3     [3] Primeiro título de eleitor (Documen... N4          
   4    N4     [4] Alistamento militar obrigatório (Do... N5          
   5    N5     [5] Carteira de Trabalho Digital (Traba... N6          
   6    N6     [6] Programa Jovem Aprendiz (Educação e... N7          
   7    N7     [7] Pedir o seguro-desemprego (Trabalho... N9          
   8    N9     [9] Cartão Nacional de Saúde (Cartão SU... N10         
   9    N10    [10] Vacinação gratuita e caderneta (Sa... N11         
   10   N11    [11] Inscrição no Cadastro Único (CadÚn... N12         
   11   N12    [12] Reclamação de direitos do consumid... N13         
   12   N13    [13] Tarifa Social de Energia Elétrica ... None        CAUDA
   Integridade verificada: OK
   Comparações: 29 | mesmos 12 nós reutilizados (nenhuma cópia): True

========================================================================
PASSO 14 - Merge Sort por titulo (crescente) - religação dos nós existentes
========================================================================
Antes : HEAD -> [1] -> [2] -> [3] -> [4] -> [5] -> [6] -> [7] -> [9] -> [10] -> [11] -> [12] -> [13] -> None   (tamanho=12, cabeca=1, cauda=13)
Depois: HEAD -> [4] -> [9] -> [2] -> [5] -> [11] -> [7] -> [3] -> [6] -> [12] -> [13] -> [1] -> [10] -> None   (tamanho=12, cabeca=4, cauda=10)
   pos  nó     dado                                       proximo -> 
   1    N4     [4] Alistamento militar obrigatório (Do... N9          CABEÇA
   2    N9     [9] Cartão Nacional de Saúde (Cartão SU... N2          
   3    N2     [2] Carteira de Identidade Nacional (CI... N5          
   4    N5     [5] Carteira de Trabalho Digital (Traba... N11         
   5    N11    [11] Inscrição no Cadastro Único (CadÚn... N7          
   6    N7     [7] Pedir o seguro-desemprego (Trabalho... N3          
   7    N3     [3] Primeiro título de eleitor (Documen... N6          
   8    N6     [6] Programa Jovem Aprendiz (Educação e... N12         
   9    N12    [12] Reclamação de direitos do consumid... N13         
   10   N13    [13] Tarifa Social de Energia Elétrica ... N1          
   11   N1     [1] Tirar o CPF pela primeira vez (Docu... N10         
   12   N10    [10] Vacinação gratuita e caderneta (Sa... None        CAUDA
   Integridade verificada: OK
   Comparações: 33 | mesmos 12 nós reutilizados (nenhuma cópia): True

========================================================================
PASSO 15 - Merge Sort por categoria (crescente) - religação dos nós existentes
========================================================================
Antes : HEAD -> [4] -> [9] -> [2] -> [5] -> [11] -> [7] -> [3] -> [6] -> [12] -> [13] -> [1] -> [10] -> None   (tamanho=12, cabeca=4, cauda=10)
Depois: HEAD -> [11] -> [13] -> [4] -> [2] -> [3] -> [1] -> [6] -> [9] -> [10] -> [12] -> [5] -> [7] -> None   (tamanho=12, cabeca=11, cauda=7)
   pos  nó     dado                                       proximo -> 
   1    N11    [11] Inscrição no Cadastro Único (CadÚn... N13         CABEÇA
   2    N13    [13] Tarifa Social de Energia Elétrica ... N4          
   3    N4     [4] Alistamento militar obrigatório (Do... N2          
   4    N2     [2] Carteira de Identidade Nacional (CI... N3          
   5    N3     [3] Primeiro título de eleitor (Documen... N1          
   6    N1     [1] Tirar o CPF pela primeira vez (Docu... N6          
   7    N6     [6] Programa Jovem Aprendiz (Educação e... N9          
   8    N9     [9] Cartão Nacional de Saúde (Cartão SU... N10         
   9    N10    [10] Vacinação gratuita e caderneta (Sa... N12         
   10   N12    [12] Reclamação de direitos do consumid... N5          
   11   N5     [5] Carteira de Trabalho Digital (Traba... N7          
   12   N7     [7] Pedir o seguro-desemprego (Trabalho... None        CAUDA
   Integridade verificada: OK
   Comparações: 31 | mesmos 12 nós reutilizados (nenhuma cópia): True

========================================================================
PASSO 16 - Merge Sort por id (decrescente) - religação dos nós existentes
========================================================================
Antes : HEAD -> [11] -> [13] -> [4] -> [2] -> [3] -> [1] -> [6] -> [9] -> [10] -> [12] -> [5] -> [7] -> None   (tamanho=12, cabeca=11, cauda=7)
Depois: HEAD -> [13] -> [12] -> [11] -> [10] -> [9] -> [7] -> [6] -> [5] -> [4] -> [3] -> [2] -> [1] -> None   (tamanho=12, cabeca=13, cauda=1)
   pos  nó     dado                                       proximo -> 
   1    N13    [13] Tarifa Social de Energia Elétrica ... N12         CABEÇA
   2    N12    [12] Reclamação de direitos do consumid... N11         
   3    N11    [11] Inscrição no Cadastro Único (CadÚn... N10         
   4    N10    [10] Vacinação gratuita e caderneta (Sa... N9          
   5    N9     [9] Cartão Nacional de Saúde (Cartão SU... N7          
   6    N7     [7] Pedir o seguro-desemprego (Trabalho... N6          
   7    N6     [6] Programa Jovem Aprendiz (Educação e... N5          
   8    N5     [5] Carteira de Trabalho Digital (Traba... N4          
   9    N4     [4] Alistamento militar obrigatório (Do... N3          
   10   N3     [3] Primeiro título de eleitor (Documen... N2          
   11   N2     [2] Carteira de Identidade Nacional (CI... N1          
   12   N1     [1] Tirar o CPF pela primeira vez (Docu... None        CAUDA
   Integridade verificada: OK
   Comparações: 27 | mesmos 12 nós reutilizados (nenhuma cópia): True

========================================================================
PASSO 17 - Análise por categoria
========================================================================
   Total de registros: 12
   Assistência Social          2   16.67%  ##
   Serviços Urbanos            1    8.33%  #
   Saúde                       2   16.67%  ##
   Trabalho e Renda            2   16.67%  ##
   Educação e Qualificação     1    8.33%  #
   Documentação                4   33.33%  ####

========================================================================
PASSO 18 - Limpar lista
========================================================================
   removidos: 12
Depois: HEAD -> None   (tamanho=0, cabeca=None, cauda=None)
   (nenhum nó: cabeca = None, cauda = None)

Demonstração concluída com sucesso.
```

Log salvo em [evidencias/saida_demonstracao.txt](evidencias/saida_demonstracao.txt).
<!-- DEMO:FIM -->

## 10. Atendimento aos requisitos do enunciado

| Requisito (enunciado) | Onde é atendido |
| --- | --- |
| 3.1 Cadastro com ID único em lista encadeada própria | `ListaEncadeada.inserir` + `IdDuplicadoError`; menu opção 1 |
| 3.2 Consulta por ID e pesquisa por atributo; comportamento sem resultado | `busca_linear_por_id`, `pesquisar_por_texto`; seções 5.1–5.2; testes 21–30 |
| 3.3 Ordenação com algoritmo estudado (sem função pronta) | `merge_sort_lista` (Merge Sort); seção 5.3; testes 41–49 |
| 3.4 Lista encadeada com inserção, percurso e remoção; classes e referências | `No`, `ListaEncadeada`; seção 4 |
| 3.5 Atualizar/excluir preservando integridade; informação útil | `atualizar`, `remover`, `verificar_integridade`, `estatisticas`; opção 8 |
| 3.6 Menu com validação de entradas, opções inexistentes, duplicados e consultas vazias | [main.py](main.py); seção 7; testes 54–59 |
| 4 Análise Big-O de inserção, busca, remoção e ordenação | Seção 6 |
| 4 Testes: normais, inexistentes, inválidos e lista vazia | [testes_dsa.py](testes_dsa.py); seção 8 |
| 6 Demonstração do funcionamento real das estruturas | [demonstracao_dsa.py](demonstracao_dsa.py); seção 9 |
