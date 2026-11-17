"""
testes_dsa.py - Testes automatizados (assert) do Citizen Assist AI (DSA).

Execução:
    python testes_dsa.py              -> tabela de evidências no terminal
    python testes_dsa.py --markdown   -> mesma tabela em formato Markdown

Cobertura: CRUD completo, buscas, Merge Sort (id/título/categoria, crescente
e decrescente), registros inexistentes, IDs duplicados, entradas inválidas,
operações com lista vazia e o menu interativo (entradas simuladas, sem
traceback).

Autor: Alan Júnior Araújo de Souza - RM 574112 (Individual)
"""

import builtins
import io
import random
import sys
from contextlib import redirect_stdout

from models import ServicoCidadao
from lista_encadeada import (
    ListaEncadeada, No, IdDuplicadoError, RegistroNaoEncontradoError, ListaVaziaError,
)
from algoritmos import (
    busca_linear_por_id, pesquisar_por_texto, merge_sort_lista, ordenar_via_colecao,
    normalizar_texto, chave_ordenacao,
)
from dados_iniciais import carregar_dados_iniciais, criar_servicos_iniciais
import main as menu

RESULTADOS = []  # (n, caso, entrada, esperado, observado, status)


# ---------------------------------------------------------------------- #
# Infraestrutura mínima de testes
# ---------------------------------------------------------------------- #
def caso(nome, entrada, esperado):
    """Decorador: registra e executa a função de teste imediatamente.

    A função deve usar `assert` e retornar uma string com o resultado
    observado. AssertionError -> FALHOU; outra exceção -> ERRO.
    """
    def decorador(funcao):
        try:
            observado = funcao()
            status = "PASSOU"
        except AssertionError as erro:
            observado = "AssertionError: %s" % erro
            status = "FALHOU"
        except Exception as erro:  # registro para análise, não interrompe a suíte
            observado = "%s: %s" % (type(erro).__name__, erro)
            status = "ERRO"
        RESULTADOS.append((len(RESULTADOS) + 1, nome, entrada, esperado, observado, status))
        return funcao
    return decorador


def espera_excecao(tipo, funcao, *args, **kwargs):
    """Executa a função e garante que a exceção `tipo` foi lançada."""
    try:
        funcao(*args, **kwargs)
    except tipo as erro:
        return "%s: %s" % (type(erro).__name__, erro)
    raise AssertionError("esperava %s, mas nenhuma exceção foi lançada" % tipo.__name__)


def srv(id, titulo="Serviço", categoria="Geral"):
    return ServicoCidadao(id, titulo, categoria, "Descrição", "Requisitos", "Local")


def lista_com(*ids):
    lista = ListaEncadeada()
    for i in ids:
        lista.inserir(srv(i, "Serviço %d" % i))
    return lista


def lista_inicial():
    lista = ListaEncadeada()
    carregar_dados_iniciais(lista)
    return lista


def rodar_menu(entradas, lista=None):
    """Executa o menu com entradas simuladas; devolve (saida, lista)."""
    fila = list(entradas)

    def falso_input(prompt=""):
        if not fila:
            raise EOFError()
        return fila.pop(0)

    original = builtins.input
    builtins.input = falso_input
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            lista = menu.executar_menu(lista)
    finally:
        builtins.input = original
    return buffer.getvalue(), lista


# ====================================================================== #
# 1) MODELO E VALIDAÇÃO DE ENTRADAS
# ====================================================================== #
@caso("Criar ServicoCidadao válido", "id=1, campos preenchidos", "Objeto criado com campos sem espaços extras")
def _():
    s = ServicoCidadao(" 1 ", "  CPF  ", "Documentação", "d", "r", "l")
    assert s.id == 1 and s.titulo == "CPF"
    return "id=%d, titulo=%r" % (s.id, s.titulo)


@caso("ID não numérico", "id='abc'", "ValueError")
def _():
    return espera_excecao(ValueError, ServicoCidadao, "abc", "t", "c", "d", "r", "l")


@caso("ID zero/negativo", "id=0 e id=-5", "ValueError nos dois casos")
def _():
    espera_excecao(ValueError, srv, 0)
    return espera_excecao(ValueError, srv, -5)


@caso("ID vazio / bool / float", "id='', True, 3.5", "ValueError nos três casos")
def _():
    espera_excecao(ValueError, srv, "")
    espera_excecao(ValueError, srv, True)
    return espera_excecao(ValueError, srv, 3.5)


@caso("Campo de texto vazio", "titulo='   '", "ValueError")
def _():
    return espera_excecao(ValueError, ServicoCidadao, 1, "   ", "c", "d", "r", "l")


# ====================================================================== #
# 2) OPERAÇÕES COM LISTA VAZIA
# ====================================================================== #
@caso("Lista vazia: estado inicial", "ListaEncadeada()", "len=0, cabeca=cauda=None, integra")
def _():
    l = ListaEncadeada()
    assert len(l) == 0 and l.cabeca is None and l.cauda is None and l.esta_vazia()
    assert l.verificar_integridade()
    return l.representar_encadeamento()


@caso("Lista vazia: listar/percorrer", "listar()", "[] (nenhuma linha)")
def _():
    l = ListaEncadeada()
    assert l.listar() == [] and list(l.percorrer()) == []
    return "listar() -> []"


@caso("Lista vazia: consultar por ID", "buscar_por_id(1) / busca_linear_por_id(1)", "None com 0 comparações")
def _():
    l = ListaEncadeada()
    assert l.buscar_por_id(1) is None
    s, c = busca_linear_por_id(l, 1)
    assert s is None and c == 0
    return "None, comparacoes=0"


@caso("Lista vazia: pesquisar texto", "pesquisar('cpf')", "Nenhum resultado (encontrou=False)")
def _():
    r = pesquisar_por_texto(ListaEncadeada(), "cpf")
    assert not r.encontrou and r.registros == [] and r.comparacoes == 0
    return "encontrou=False, registros=[]"


@caso("Lista vazia: atualizar", "atualizar(1, titulo='X')", "ListaVaziaError")
def _():
    return espera_excecao(ListaVaziaError, ListaEncadeada().atualizar, 1, titulo="X")


@caso("Lista vazia: remover", "remover(1)", "ListaVaziaError")
def _():
    return espera_excecao(ListaVaziaError, ListaEncadeada().remover, 1)


@caso("Lista vazia: ordenar (Merge Sort)", "merge_sort_lista(vazia, 'titulo')", "0 comparações, lista íntegra")
def _():
    l = ListaEncadeada()
    assert merge_sort_lista(l, "titulo") == 0 and l.verificar_integridade()
    assert ordenar_via_colecao(l, "id") == 0 and l.esta_vazia()
    return "comparacoes=0, cabeca=None"


@caso("Lista vazia: estatísticas", "estatisticas()", "total=0, categorias=[]")
def _():
    e = ListaEncadeada().estatisticas()
    assert e == {"total": 0, "categorias": []}
    return str(e)


@caso("Lista vazia: limpar / converter", "limpar(), para_colecao()", "0 removidos, colecao []")
def _():
    l = ListaEncadeada()
    assert l.limpar() == 0 and l.para_colecao() == []
    return "limpar()=0, para_colecao()=[]"


# ====================================================================== #
# 3) INSERÇÃO E IDS DUPLICADOS
# ====================================================================== #
@caso("Inserir primeiro registro", "inserir(id=10)", "cabeca=cauda=No(10), len=1")
def _():
    l = ListaEncadeada()
    no = l.inserir(srv(10))
    assert isinstance(no, No) and l.cabeca is no and l.cauda is no and no.proximo is None and len(l) == 1
    return l.representar_encadeamento()


@caso("Inserir vários (no fim)", "ids 3, 1, 2", "Ordem de inserção preservada: 3->1->2")
def _():
    l = lista_com(3, 1, 2)
    assert l.ids() == [3, 1, 2] and l.cauda.dado.id == 2 and l.verificar_integridade()
    return l.representar_encadeamento()


@caso("Inserir no início", "lista 3->1; inserir_no_inicio(9)", "9->3->1")
def _():
    l = lista_com(3, 1)
    l.inserir_no_inicio(srv(9))
    assert l.ids() == [9, 3, 1] and l.verificar_integridade()
    return l.representar_encadeamento()


@caso("ID duplicado bloqueado", "lista 1->2; inserir(id=2)", "IdDuplicadoError e lista inalterada")
def _():
    l = lista_com(1, 2)
    msg = espera_excecao(IdDuplicadoError, l.inserir, srv(2, "Outro"))
    espera_excecao(IdDuplicadoError, l.inserir_no_inicio, srv(1))
    assert l.ids() == [1, 2] and len(l) == 2 and l.buscar_por_id(2).titulo == "Serviço 2"
    return msg + " | lista=" + str(l.ids())


@caso("Inserir tipo inválido", "inserir('texto')", "TypeError")
def _():
    return espera_excecao(TypeError, ListaEncadeada().inserir, "texto")


@caso("Carga inicial + recarga", "carregar 2x", "12 inseridos; depois 0 inseridos/12 ignorados")
def _():
    l = ListaEncadeada()
    a = carregar_dados_iniciais(l)
    b = carregar_dados_iniciais(l)
    assert a == (12, 0) and b == (0, 12) and len(l) == 12 and l.verificar_integridade()
    return "1a carga=%s, 2a carga=%s" % (a, b)


# ====================================================================== #
# 4) CONSULTA E PESQUISA
# ====================================================================== #
@caso("Consultar ID existente (meio)", "dados iniciais; busca_linear_por_id(9)", "Cartão SUS, 5 comparações")
def _():
    s, c = busca_linear_por_id(lista_inicial(), 9)
    assert s is not None and s.id == 9 and "SUS" in s.titulo and c == 5
    return "%s, comparacoes=%d" % (s.resumo(), c)


@caso("Consultar ID na cabeça (melhor caso)", "busca_linear_por_id(7)", "1 comparação")
def _():
    s, c = busca_linear_por_id(lista_inicial(), 7)
    assert s.id == 7 and c == 1
    return "%s, comparacoes=%d" % (s.resumo(), c)


@caso("Consultar ID inexistente (pior caso)", "busca_linear_por_id(999)", "None após n=12 comparações")
def _():
    s, c = busca_linear_por_id(lista_inicial(), 999)
    assert s is None and c == 12
    return "None, comparacoes=%d" % c


@caso("Consultar com ID inválido", "buscar_por_id('x')", "ValueError")
def _():
    return espera_excecao(ValueError, lista_inicial().buscar_por_id, "x")


@caso("Pesquisa por título sem acento/maiúsculas", "titulo contém 'CARTAO'", "Somente id 9 ('Cartão Nacional de Saúde')")
def _():
    r = pesquisar_por_texto(lista_inicial(), "CARTAO", "titulo")
    ids = [s.id for s in r.registros]
    assert ids == [9], ids
    return "ids=%s, comparacoes=%d" % (ids, r.comparacoes)


@caso("Pesquisa por categoria", "categoria contém 'documentacao'", "4 registros: [2, 1, 3, 4]")
def _():
    r = pesquisar_por_texto(lista_inicial(), "documentacao", "categoria")
    ids = [s.id for s in r.registros]
    assert ids == [2, 1, 3, 4], ids
    return "ids=%s" % ids


@caso("Pesquisa em ambos os campos", "'saude' em título ou categoria", "[9, 10]")
def _():
    r = pesquisar_por_texto(lista_inicial(), "  SAÚDE ", "ambos")
    ids = [s.id for s in r.registros]
    assert ids == [9, 10], ids
    return "ids=%s, comparacoes=%d" % (ids, r.comparacoes)


@caso("Pesquisa sem resultado", "'passaporte'", "encontrou=False, lista vazia de resultados")
def _():
    r = pesquisar_por_texto(lista_inicial(), "passaporte")
    assert not r.encontrou and len(r) == 0 and r.comparacoes == 24
    return "encontrou=False, comparacoes=%d" % r.comparacoes


@caso("Pesquisa com termo vazio / campo inválido", "termo='  ' ; campo='local'", "ValueError nos dois casos")
def _():
    espera_excecao(ValueError, pesquisar_por_texto, lista_inicial(), "  ")
    return espera_excecao(ValueError, pesquisar_por_texto, lista_inicial(), "cpf", "local")


@caso("Normalização de texto", "normalizar('  SAÚDE   e Educação ')", "'saude e educacao'")
def _():
    n = normalizar_texto("  SAÚDE   e Educação ")
    assert n == "saude e educacao"
    return repr(n)


# ====================================================================== #
# 5) ATUALIZAÇÃO
# ====================================================================== #
@caso("Atualizar campos existentes", "atualizar(5, titulo, local)", "Campos alterados, mesmo nó e encadeamento")
def _():
    l = lista_com(1, 5, 8)
    no_antes = l.cabeca.proximo
    proximo_antes = no_antes.proximo
    alterados = l.atualizar(5, titulo="CTPS Digital", local_atendimento="App gov.br")
    assert alterados == ["titulo", "local_atendimento"]
    assert l.cabeca.proximo is no_antes and no_antes.proximo is proximo_antes
    assert l.buscar_por_id(5).titulo == "CTPS Digital" and l.ids() == [1, 5, 8]
    return "alterados=%s, ids=%s" % (alterados, l.ids())


@caso("Atualizar ID inexistente", "atualizar(99, titulo='X')", "RegistroNaoEncontradoError")
def _():
    return espera_excecao(RegistroNaoEncontradoError, lista_com(1, 2).atualizar, 99, titulo="X")


@caso("Atualizar com valor vazio (atômico)", "atualizar(1, titulo='Novo', categoria='')", "ValueError e nada alterado")
def _():
    l = lista_com(1)
    msg = espera_excecao(ValueError, l.atualizar, 1, titulo="Novo", categoria="")
    assert l.buscar_por_id(1).titulo == "Serviço 1"
    return msg + " | titulo mantido"


@caso("Atualizar campo proibido/inexistente", "atualizar(1, id=7) ; atualizar(1, cor='x')", "ValueError nos dois casos")
def _():
    l = lista_com(1)
    espera_excecao(ValueError, l.atualizar, 1, id=7)
    espera_excecao(ValueError, l.atualizar, 1)
    return espera_excecao(ValueError, l.atualizar, 1, cor="x")


# ====================================================================== #
# 6) REMOÇÃO (INÍCIO, MEIO, FIM, ÚNICO)
# ====================================================================== #
@caso("Remover do início", "lista 1->2->3; remover(1)", "2->3, cabeca=2")
def _():
    l = lista_com(1, 2, 3)
    r = l.remover(1)
    assert r.id == 1 and l.ids() == [2, 3] and l.cabeca.dado.id == 2 and l.verificar_integridade()
    return l.representar_encadeamento()


@caso("Remover do meio", "lista 1->2->3; remover(2)", "1->3 (1.proximo aponta p/ 3)")
def _():
    l = lista_com(1, 2, 3)
    l.remover(2)
    assert l.ids() == [1, 3] and l.cabeca.proximo is l.cauda and l.verificar_integridade()
    return l.representar_encadeamento()


@caso("Remover do fim", "lista 1->2->3; remover(3)", "1->2, cauda=2, cauda.proximo=None")
def _():
    l = lista_com(1, 2, 3)
    l.remover(3)
    assert l.ids() == [1, 2] and l.cauda.dado.id == 2 and l.cauda.proximo is None
    l.inserir(srv(4))  # a cauda correta permite inserir no fim depois
    assert l.ids() == [1, 2, 4] and l.verificar_integridade()
    return "após remover(3) e inserir(4): " + l.representar_encadeamento()


@caso("Remover único elemento", "lista 7; remover(7)", "Lista vazia, cabeca=cauda=None")
def _():
    l = lista_com(7)
    l.remover(7)
    assert l.esta_vazia() and l.cauda is None and len(l) == 0 and l.verificar_integridade()
    return l.representar_encadeamento()


@caso("Remover ID inexistente", "lista 1->2; remover(50)", "RegistroNaoEncontradoError, lista intacta")
def _():
    l = lista_com(1, 2)
    msg = espera_excecao(RegistroNaoEncontradoError, l.remover, 50)
    assert l.ids() == [1, 2]
    return msg


@caso("Remover com ID inválido", "remover('dois')", "ValueError")
def _():
    return espera_excecao(ValueError, lista_com(1).remover, "dois")


# ====================================================================== #
# 7) MERGE SORT
# ====================================================================== #
@caso("Merge Sort por ID (crescente)", "dados iniciais (ordem 7,2,11,...)", "[1,2,3,4,5,6,7,9,10,11,12,13]")
def _():
    l = lista_inicial()
    c = merge_sort_lista(l, "id")
    assert l.ids() == [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13] and l.verificar_integridade()
    assert l.cabeca.dado.id == 1 and l.cauda.dado.id == 13
    return "ids=%s, comparacoes=%d" % (l.ids(), c)


@caso("Merge Sort por ID (decrescente)", "decrescente=True", "[13,12,...,1]")
def _():
    l = lista_inicial()
    merge_sort_lista(l, "id", decrescente=True)
    assert l.ids() == [13, 12, 11, 10, 9, 7, 6, 5, 4, 3, 2, 1] and l.verificar_integridade()
    return "ids=%s" % l.ids()


@caso("Merge Sort por título", "critério 'titulo'", "Títulos em ordem alfabética (sem acento)")
def _():
    l = lista_inicial()
    merge_sort_lista(l, "titulo")
    titulos = [normalizar_texto(s.titulo) for s in l.percorrer()]
    for i in range(len(titulos) - 1):
        assert titulos[i] <= titulos[i + 1], (titulos[i], titulos[i + 1])
    assert l.verificar_integridade()
    return "1o=%r ... ultimo=%r" % (l.cabeca.dado.titulo, l.cauda.dado.titulo)


@caso("Merge Sort por categoria", "critério 'categoria'", "Assistência Social primeiro, Trabalho e Renda por último")
def _():
    l = lista_inicial()
    merge_sort_lista(l, "categoria")
    cats = [s.categoria for s in l.percorrer()]
    assert cats[0] == "Assistência Social" and cats[-1] == "Trabalho e Renda"
    for i in range(len(cats) - 1):
        assert normalizar_texto(cats[i]) <= normalizar_texto(cats[i + 1])
    return "categorias=%s" % cats


@caso("Merge Sort reutiliza os mesmos nós", "ordenar por id", "Mesmo conjunto de objetos No (só ponteiros mudam)")
def _():
    l = lista_inicial()
    antes = set()
    atual = l.cabeca
    while atual:
        antes.add(id(atual))
        atual = atual.proximo
    merge_sort_lista(l, "id")
    depois = set()
    atual = l.cabeca
    while atual:
        depois.add(id(atual))
        atual = atual.proximo
    assert antes == depois and len(depois) == 12
    return "%d nós antes = %d nós depois (mesmas referências)" % (len(antes), len(depois))


@caso("Merge Sort: empate de categoria", "3 registros mesma categoria (ids 3,1,2)", "Empate desfeito por título e depois id")
def _():
    l = ListaEncadeada()
    l.inserir(srv(3, "B", "X"))
    l.inserir(srv(1, "A", "X"))
    l.inserir(srv(2, "A", "X"))
    merge_sort_lista(l, "categoria")
    assert l.ids() == [1, 2, 3]
    return "ids=%s" % l.ids()


@caso("Merge Sort 1 elemento / já ordenada", "lista 5 ; lista 1..8", "0 comparações ; ordem mantida")
def _():
    l1 = lista_com(5)
    assert merge_sort_lista(l1, "id") == 0 and l1.ids() == [5]
    l2 = lista_com(*range(1, 9))
    c = merge_sort_lista(l2, "id")
    assert l2.ids() == list(range(1, 9))
    return "1 elem: 0 comp; já ordenada (n=8): %d comp (melhor caso n/2*log2 n = 12)" % c


@caso("Merge Sort aleatório (200 registros)", "ids embaralhados, seed=2026", "Ordenado de 1 a 200; igual ao Merge Sort via coleção")
def _():
    ids = list(range(1, 201))
    random.Random(2026).shuffle(ids)
    l1 = lista_com(*ids)
    l2 = lista_com(*ids)
    c1 = merge_sort_lista(l1, "id")
    c2 = ordenar_via_colecao(l2, "id")
    assert l1.ids() == l2.ids() == list(range(1, 201))
    assert l1.verificar_integridade() and l2.verificar_integridade()
    return "ordenado; comparacoes nós=%d, colecao=%d (n log2 n ~ 1529)" % (c1, c2)


@caso("Critério de ordenação inválido", "merge_sort_lista(l, 'local')", "ValueError, lista intacta")
def _():
    l = lista_com(2, 1)
    msg = espera_excecao(ValueError, merge_sort_lista, l, "local")
    espera_excecao(ValueError, chave_ordenacao, "")
    assert l.ids() == [2, 1]
    return msg


# ====================================================================== #
# 8) ANÁLISE E CONVERSÃO CONTROLADA
# ====================================================================== #
@caso("Estatísticas por categoria", "dados iniciais", "total=12; Documentação=4 (33.33%)")
def _():
    e = lista_inicial().estatisticas()
    mapa = dict((c, (q, p)) for c, q, p in e["categorias"])
    assert e["total"] == 12 and mapa["Documentação"] == (4, 33.33)
    assert sum(q for _, q, _ in e["categorias"]) == 12
    assert abs(sum(p for _, _, p in e["categorias"]) - 100) < 0.05
    return "total=12, categorias=%d, Documentação=%s" % (len(mapa), mapa["Documentação"])


@caso("Conversão lista -> coleção -> lista", "para_colecao() e de_colecao()", "Mesma ordem; original intacta")
def _():
    l = lista_inicial()
    col = l.para_colecao()
    assert [s.id for s in col] == l.ids() and len(l) == 12
    nova = ListaEncadeada.de_colecao(col)
    assert nova.ids() == l.ids() and nova.verificar_integridade()
    return "colecao com %d itens; reconstruída íntegra" % len(col)


@caso("Reconstrução rejeita duplicados", "reconstruir_de_colecao([1, 2, 1])", "IdDuplicadoError, lista original preservada")
def _():
    l = lista_com(5, 6)
    msg = espera_excecao(IdDuplicadoError, l.reconstruir_de_colecao, [srv(1), srv(2), srv(1)])
    assert l.ids() == [5, 6] and l.verificar_integridade()
    return msg


@caso("CRUD completo em sequência", "inserir 3, atualizar, remover, consultar", "Estado final consistente")
def _():
    l = ListaEncadeada()
    for s in criar_servicos_iniciais()[:3]:
        l.inserir(s)
    l.atualizar(2, requisitos="CPF")
    l.remover(7)
    assert l.ids() == [2, 11] and l.buscar_por_id(2).requisitos == "CPF"
    assert l.buscar_por_id(7) is None and l.verificar_integridade()
    return l.representar_encadeamento()


# ====================================================================== #
# 9) MENU INTERATIVO (entradas simuladas)
# ====================================================================== #
@caso("Menu: opções inexistentes e vazias", "'abc', '', '42', '0'", "Mensagens de erro, sem traceback")
def _():
    saida, _ = rodar_menu(["abc", "", "42", "0"])
    assert "Opção inexistente: 'abc'" in saida and "Nenhuma opção informada" in saida
    assert "Opção inexistente: '42'" in saida and "Traceback" not in saida
    return "3 avisos exibidos; encerrou normalmente"


@caso("Menu: operações 2-8 com lista vazia", "2,3,4,5,6,7,8 e 9->2", "Aviso 'lista está vazia' em todas")
def _():
    saida, _ = rodar_menu(["2", "3", "4", "5", "6", "7", "8", "9", "2", "0"])
    assert saida.count("A lista está vazia") == 7 and "A lista já está vazia" in saida
    assert "Traceback" not in saida
    return "7 avisos de lista vazia + 'lista já está vazia'"


@caso("Menu: cadastro com ID inválido e duplicado", "1->'x' ; 9->1 ; 1->'7'", "Entrada inválida ; ID duplicado")
def _():
    saida, l = rodar_menu(["1", "x", "9", "1", "1", "7", "0"])
    assert "Entrada inválida" in saida and "ID duplicado" in saida and len(l) == 12
    return "ValueError e duplicidade tratados; len=%d" % len(l)


@caso("Menu: cadastro válido com campo vazio repetido", "1->20, título '' e depois 'Emitir passaporte'...", "Registro 20 cadastrado")
def _():
    entradas = ["1", "20", "", "Emitir passaporte", "Documentação", "Pedido na PF",
                "Documento com foto", "Polícia Federal", "0"]
    saida, l = rodar_menu(entradas)
    assert "não pode ficar vazio" in saida and l.buscar_por_id(20).titulo == "Emitir passaporte"
    return "aviso de campo vazio + cadastro OK; ids=%s" % l.ids()


@caso("Menu: consulta, pesquisa, atualização e exclusão", "fluxo 9,3,4,5,6,7,8", "Todas as operações concluídas")
def _():
    entradas = ["9", "1",
                "3", "999",                 # consulta inexistente
                "4", "1", "xyz",            # pesquisa sem resultado
                "4", "9", "cpf",            # campo de pesquisa inexistente
                "5", "2", "", "", "", "CPF e certidão", "", # atualização
                "6", "4", "n",              # exclusão cancelada
                "6", "4", "s",              # exclusão confirmada
                "7", "5",                   # critério inexistente
                "7", "2", "1",              # ordena por título
                "8", "0"]
    saida, l = rodar_menu(entradas)
    assert "Nenhum registro encontrado com o ID 999" in saida
    assert "Nenhum registro encontrado para 'xyz'" in saida
    assert "Opção de campo inexistente" in saida and "Critério inexistente" in saida
    assert "Exclusão cancelada" in saida and "Registro 4 removido" in saida
    assert l.buscar_por_id(2).requisitos == "CPF e certidão" and len(l) == 11
    assert "Total de registros: 11" in saida and "Traceback" not in saida
    return "11 registros ao final; nenhum traceback"


@caso("Menu: Ctrl+D (EOF) no meio de uma operação", "1 -> EOF", "Encerra sem traceback")
def _():
    saida, _ = rodar_menu(["1"])
    assert "Operação cancelada" in saida and "Traceback" not in saida
    return "operação cancelada e menu encerrado"


# ---------------------------------------------------------------------- #
# Relatório
# ---------------------------------------------------------------------- #
def imprimir_relatorio(markdown=False):
    if markdown:
        print("| # | Caso de teste | Entrada | Resultado esperado | Resultado observado | Status |")
        print("|---|---|---|---|---|---|")
        for n, nome, ent, esp, obs, st in RESULTADOS:
            celulas = [str(n), nome, ent, esp, obs, ("✅ " if st == "PASSOU" else "❌ ") + st]
            print("| " + " | ".join(c.replace("|", "\\|") for c in celulas) + " |")
    else:
        for n, nome, ent, esp, obs, st in RESULTADOS:
            print("[%s] %02d. %s" % (st, n, nome))
            print("       Entrada   : %s" % ent)
            print("       Esperado  : %s" % esp)
            print("       Observado : %s" % obs)
    total = len(RESULTADOS)
    ok = sum(1 for r in RESULTADOS if r[5] == "PASSOU")
    print()
    print("RESUMO: %d/%d testes passaram, %d falharam." % (ok, total, total - ok))
    return ok == total


if __name__ == "__main__":
    tudo_ok = imprimir_relatorio("--markdown" in sys.argv)
    sys.exit(0 if tudo_ok else 1)
