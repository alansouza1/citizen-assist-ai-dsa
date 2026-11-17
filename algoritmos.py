"""
algoritmos.py - Algoritmos de busca e ordenacao implementados manualmente.

Busca:
  - busca_linear_por_id: busca sequencial no a no, conta comparacoes.
  - pesquisar_por_texto: busca sequencial por substring em titulo e/ou
    categoria, ignorando maiusculas/minusculas e acentos.

Ordenacao:
  - merge_sort_lista: Merge Sort (divisao e conquista) aplicado DIRETAMENTE
    sobre os nos da ListaEncadeada, apenas religando as referencias
    `proximo` (nenhum registro e copiado, nenhum .sort()/sorted() e usado).
  - ordenar_via_colecao: Merge Sort sobre uma colecao auxiliar (conversao
    controlada lista -> list -> lista), usado para comparacao/validacao.

Autor: Alan Junior Araujo de Souza - RM 574112 (Individual)
"""

import unicodedata

from models import validar_id
from lista_encadeada import No

CRITERIOS_ORDENACAO = ("id", "titulo", "categoria")
CAMPOS_PESQUISA = ("titulo", "categoria", "ambos")


# ---------------------------------------------------------------------- #
# Utilitario de texto
# ---------------------------------------------------------------------- #
def normalizar_texto(texto):
    """Minusculas + remocao de acentos + espacos internos colapsados.

    'Saude e Cidadania' == normalizar('SAÚDE   e cidadania')
    """
    decomposto = unicodedata.normalize("NFD", str(texto))
    sem_acento = "".join(c for c in decomposto if unicodedata.category(c) != "Mn")
    return " ".join(sem_acento.casefold().split())


# ---------------------------------------------------------------------- #
# BUSCA
# ---------------------------------------------------------------------- #
class ResultadoBusca:
    """Resultado de uma busca: registros encontrados + comparacoes feitas."""

    def __init__(self, registros, comparacoes, termo=None):
        self.registros = registros
        self.comparacoes = comparacoes
        self.termo = termo

    @property
    def encontrou(self):
        return len(self.registros) > 0

    def __len__(self):
        return len(self.registros)


def busca_linear_por_id(lista, id_procurado):
    """Busca sequencial pelo id, partindo da cabeca.

    Retorna (servico, comparacoes). Se nao houver registro com o id,
    retorna (None, comparacoes) - com comparacoes == len(lista), pois todos
    os nos foram visitados (pior caso). Lista vazia: (None, 0).
    """
    id_procurado = validar_id(id_procurado)
    comparacoes = 0
    atual = lista.cabeca
    while atual is not None:
        comparacoes += 1
        if atual.dado.id == id_procurado:
            return atual.dado, comparacoes        # encontrou: para imediatamente
        atual = atual.proximo
    return None, comparacoes                      # percorreu tudo: nao encontrado


def pesquisar_por_texto(lista, termo, campo="ambos"):
    """Busca sequencial por substring (case-insensitive e sem acentos).

    campo: 'titulo', 'categoria' ou 'ambos'.
    Retorna um ResultadoBusca; quando nada e encontrado, `registros` e uma
    lista vazia e `encontrou` e False (o chamador exibe a mensagem).
    Lanca ValueError para termo vazio ou campo invalido.
    """
    if not isinstance(termo, str) or termo.strip() == "":
        raise ValueError("O termo de pesquisa não pode ser vazio.")
    if campo not in CAMPOS_PESQUISA:
        raise ValueError("Campo de pesquisa inválido: '%s'. Use titulo, categoria ou ambos." % campo)

    alvo = normalizar_texto(termo)
    encontrados = []
    comparacoes = 0
    atual = lista.cabeca
    while atual is not None:
        servico = atual.dado
        bateu = False
        if campo in ("titulo", "ambos"):
            comparacoes += 1
            if alvo in normalizar_texto(servico.titulo):
                bateu = True
        if not bateu and campo in ("categoria", "ambos"):
            comparacoes += 1
            if alvo in normalizar_texto(servico.categoria):
                bateu = True
        if bateu:
            encontrados.append(servico)
        atual = atual.proximo
    return ResultadoBusca(encontrados, comparacoes, termo)


# ---------------------------------------------------------------------- #
# ORDENACAO - MERGE SORT
# ---------------------------------------------------------------------- #
def chave_ordenacao(criterio):
    """Devolve a funcao que extrai a chave de comparacao de um registro.

    - id:        o proprio inteiro;
    - titulo:    titulo normalizado (desempate pelo id);
    - categoria: categoria normalizada, depois titulo, depois id.
    """
    if criterio == "id":
        return lambda s: s.id
    if criterio == "titulo":
        return lambda s: (normalizar_texto(s.titulo), s.id)
    if criterio == "categoria":
        return lambda s: (normalizar_texto(s.categoria), normalizar_texto(s.titulo), s.id)
    raise ValueError("Critério de ordenação inválido: '%s'. Use id, titulo ou categoria." % criterio)


class _Contador:
    """Conta comparacoes realizadas pelo Merge Sort (para analise empirica)."""

    def __init__(self):
        self.comparacoes = 0


def _dividir(cabeca):
    """Divide a cadeia ao meio com ponteiros lento/rapido (tartaruga e lebre).

    Retorna a cabeca da segunda metade e corta o encadeamento entre as
    metades. O(n) por chamada.
    """
    lento = cabeca
    rapido = cabeca.proximo
    while rapido is not None and rapido.proximo is not None:
        lento = lento.proximo
        rapido = rapido.proximo.proximo
    meio = lento.proximo
    lento.proximo = None       # corta a ligacao: duas sublistas independentes
    return meio


def _intercalar(a, b, chave, decrescente, contador):
    """Intercala (merge) duas cadeias ja ordenadas religando os nos.

    Usa um no sentinela para simplificar o codigo. Estavel: em empate,
    o no da cadeia da esquerda (a) vem primeiro. Iterativo -> O(1) espaco.
    """
    sentinela = No(None)       # no ficticio: sentinela.proximo sera a nova cabeca
    ultimo = sentinela
    while a is not None and b is not None:
        contador.comparacoes += 1
        ka, kb = chave(a.dado), chave(b.dado)
        if (ka <= kb) if not decrescente else (ka >= kb):
            ultimo.proximo = a
            a = a.proximo
        else:
            ultimo.proximo = b
            b = b.proximo
        ultimo = ultimo.proximo
    ultimo.proximo = a if a is not None else b   # anexa o restante (ja ordenado)
    return sentinela.proximo


def _merge_sort_nos(cabeca, chave, decrescente, contador):
    """Merge Sort recursivo sobre uma cadeia de nos. Retorna a nova cabeca."""
    if cabeca is None or cabeca.proximo is None:   # caso base: 0 ou 1 no
        return cabeca
    meio = _dividir(cabeca)                        # DIVIDIR
    esquerda = _merge_sort_nos(cabeca, chave, decrescente, contador)   # CONQUISTAR
    direita = _merge_sort_nos(meio, chave, decrescente, contador)
    return _intercalar(esquerda, direita, chave, decrescente, contador)  # COMBINAR


def merge_sort_lista(lista, criterio="id", decrescente=False):
    """Ordena a ListaEncadeada IN-PLACE religando os nos.

    Retorna o numero de comparacoes realizadas. Ao final, cabeca e cauda
    sao atualizadas e o contador de tamanho permanece o mesmo.
    Lista vazia ou com 1 elemento: nada a fazer (0 comparacoes).
    """
    chave = chave_ordenacao(criterio)     # valida o criterio mesmo com lista vazia
    contador = _Contador()
    if lista.cabeca is None or lista.cabeca.proximo is None:
        return 0
    lista.cabeca = _merge_sort_nos(lista.cabeca, chave, decrescente, contador)
    # Recalcula a cauda (O(n)): o ultimo no mudou apos a religacao.
    atual = lista.cabeca
    while atual.proximo is not None:
        atual = atual.proximo
    lista.cauda = atual
    return contador.comparacoes


# ---------------------------------------------------------------------- #
# Merge Sort sobre colecao auxiliar (conversao controlada)
# ---------------------------------------------------------------------- #
def merge_sort_vetor(vetor, chave, decrescente=False, contador=None):
    """Merge Sort classico sobre uma list Python. Retorna NOVA list ordenada."""
    if contador is None:
        contador = _Contador()
    if len(vetor) <= 1:
        return vetor[:]
    meio = len(vetor) // 2
    esquerda = merge_sort_vetor(vetor[:meio], chave, decrescente, contador)
    direita = merge_sort_vetor(vetor[meio:], chave, decrescente, contador)
    resultado = []
    i = j = 0
    while i < len(esquerda) and j < len(direita):
        contador.comparacoes += 1
        ke, kd = chave(esquerda[i]), chave(direita[j])
        if (ke <= kd) if not decrescente else (ke >= kd):
            resultado.append(esquerda[i])
            i += 1
        else:
            resultado.append(direita[j])
            j += 1
    while i < len(esquerda):
        resultado.append(esquerda[i])
        i += 1
    while j < len(direita):
        resultado.append(direita[j])
        j += 1
    return resultado


def ordenar_via_colecao(lista, criterio="id", decrescente=False):
    """Converte a lista encadeada em colecao, ordena e RECONSTROI a lista.

    Demonstra a conversao controlada exigida: a colecao auxiliar existe
    apenas durante o algoritmo; ao final, a lista encadeada e reconstruida
    com novos nos na ordem correta. Retorna o numero de comparacoes.
    """
    chave = chave_ordenacao(criterio)
    contador = _Contador()
    colecao = lista.para_colecao()
    ordenada = merge_sort_vetor(colecao, chave, decrescente, contador)
    lista.reconstruir_de_colecao(ordenada)
    return contador.comparacoes
