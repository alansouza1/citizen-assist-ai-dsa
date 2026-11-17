# Citizen Assist AI — Data Structures and Algorithms (DSA) 🇧🇷

> **Global Solution 2026.2 — Citizen Tech** · Disciplina: *Data Structures and Algorithms*
> Sistema de gerenciamento e consulta de **serviços e orientações ao cidadão** com
> **lista encadeada**, **busca linear** e **Merge Sort** implementados manualmente em **Python puro**.

## 👤 Identificação

| Nome completo               | RM     | Modalidade |
| --------------------------- | ------ | ---------- |
| Alan Júnior Araújo de Souza | 574112 | Individual |

## ▶️ Como executar

**Pré-requisito:** Python 3.8 ou superior. **Nenhuma biblioteca externa** — somente a biblioteca padrão.

```bash
cd citizen-assist-ai-dsa

python main.py               # menu interativo
python testes_dsa.py         # 59 testes automatizados (assert) + tabela de evidências
python testes_dsa.py --markdown   # mesma tabela em formato Markdown
python demonstracao_dsa.py   # demonstração passo a passo do estado real dos nós
```

> Em alguns sistemas o interpretador se chama `python3` (ex.: `python3 main.py`).

## 📁 Estrutura

| Arquivo | Responsabilidade |
| --- | --- |
| [`models.py`](models.py) | Classe `ServicoCidadao` (id, título, categoria, descrição, requisitos, local de atendimento) e validação de entradas. |
| [`lista_encadeada.py`](lista_encadeada.py) | Classes `No` e `ListaEncadeada` (cabeça, cauda, tamanho): inserção com bloqueio de ID duplicado, percurso, consulta, atualização, remoção (início/meio/fim), estatísticas, conversão controlada e verificação de integridade. |
| [`algoritmos.py`](algoritmos.py) | Busca linear por ID, pesquisa textual sem acento/maiúsculas e **Merge Sort** sobre os nós (critérios `id`, `titulo`, `categoria`; crescente/decrescente). |
| [`dados_iniciais.py`](dados_iniciais.py) | 12 serviços reais do Citizen Assist AI (CPF, CIN, CadÚnico, Cartão SUS, seguro-desemprego...). |
| [`main.py`](main.py) | Menu interativo com as opções 0–9 e tratamento de todas as entradas inválidas (sem traceback). |
| [`testes_dsa.py`](testes_dsa.py) | Testes automatizados com `assert`. |
| [`demonstracao_dsa.py`](demonstracao_dsa.py) | Demonstração prática das estruturas e algoritmos. |
| [`evidencias/`](evidencias/) | Saídas reais de `testes_dsa.py` e `demonstracao_dsa.py`. |
| [`DOCUMENTACAO_DSA.md`](DOCUMENTACAO_DSA.md) | Documentação técnica completa: recorte, modelagem, diagramas, menu, análise Big-O, evidências de testes e log da demonstração. |

## 🧭 Menu

```
  1. Cadastrar serviço
  2. Listar todos
  3. Consultar por ID
  4. Pesquisar por título/categoria
  5. Atualizar registro
  6. Excluir registro
  7. Ordenar registros por critério (Merge Sort)
  8. Exibir análise por categoria
  9. Carregar dados iniciais / Limpar lista
  0. Encerrar
```

Dica: comece pela opção **9 → 1** para carregar os 12 serviços de exemplo.

## 📊 Resumo da complexidade

| Operação | Melhor | Médio | Pior | Espaço extra |
| --- | --- | --- | --- | --- |
| Inserção (com checagem de duplicado) | Θ(n)* | Θ(n) | Θ(n) | O(1) |
| Consulta por ID (busca linear) | O(1) | O(n) | O(n) | O(1) |
| Pesquisa por título/categoria | Θ(n·m) | Θ(n·m) | Θ(n·m) | O(k + m) |
| Atualização | O(1) | O(n) | O(n) | O(1) |
| Remoção | O(1) | O(n) | O(n) | O(1) |
| Merge Sort (nós) | Θ(n log n) | Θ(n log n) | Θ(n log n) | O(log n) |

\* inserção bem-sucedida sempre percorre a lista inteira para garantir que o ID é único. Detalhes e justificativas em [DOCUMENTACAO_DSA.md](DOCUMENTACAO_DSA.md#6-análise-de-complexidade-big-o).
