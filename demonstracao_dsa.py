"""
demonstracao_dsa.py - Demonstração prática passo a passo da lista encadeada.

Execução:  python demonstracao_dsa.py

Mostra o ESTADO REAL dos nós (cabeça, cauda, tamanho e para onde cada
`proximo` aponta) antes e depois de cada operação: inserções, atualização,
remoções (início/meio/fim), buscas e ordenação com Merge Sort.

Autor: Alan Júnior Araújo de Souza - RM 574112 (Individual)
"""

from lista_encadeada import ListaEncadeada, IdDuplicadoError, RegistroNaoEncontradoError
from algoritmos import busca_linear_por_id, pesquisar_por_texto, merge_sort_lista
from dados_iniciais import criar_servicos_iniciais, carregar_dados_iniciais

PASSO = [0]


def titulo(texto):
    PASSO[0] += 1
    print()
    print("=" * 72)
    print("PASSO %02d - %s" % (PASSO[0], texto))
    print("=" * 72)


def rotulo_no(no):
    """Rótulo estável do nó: N<id do registro> (ids são únicos na lista)."""
    return "N%d" % no.dado.id


def mostrar_nos(lista, legenda="Estado"):
    """Imprime o encadeamento e uma tabela com cada nó e seu `proximo`."""
    print("%s: %s" % (legenda, lista.representar_encadeamento()))
    if lista.esta_vazia():
        print("   (nenhum nó: cabeca = None, cauda = None)")
        return
    print("   %-4s %-6s %-42s %-11s" % ("pos", "nó", "dado", "proximo ->"))
    atual = lista.cabeca
    pos = 1
    while atual is not None:
        prox = rotulo_no(atual.proximo) if atual.proximo is not None else "None"
        marca = []
        if atual is lista.cabeca:
            marca.append("CABEÇA")
        if atual is lista.cauda:
            marca.append("CAUDA")
        dado = atual.dado.resumo()
        if len(dado) > 42:
            dado = dado[:39] + "..."
        print("   %-4d %-6s %-42s %-11s %s" % (pos, rotulo_no(atual), dado, prox, "/".join(marca)))
        atual = atual.proximo
        pos += 1
    print("   Integridade verificada: %s" % ("OK" if lista.verificar_integridade() else "FALHA"))


def main():
    print("CITIZEN ASSIST AI - DEMONSTRAÇÃO PRÁTICA DA LISTA ENCADEADA (DSA)")
    print("Aluno: Alan Júnior Araújo de Souza - RM 574112 (Individual)")

    servicos = dict((s.id, s) for s in criar_servicos_iniciais())
    lista = ListaEncadeada()

    titulo("Lista vazia recém-criada")
    mostrar_nos(lista)

    titulo("Inserção do primeiro registro (id 7) - cabeça e cauda apontam para o mesmo nó")
    lista.inserir(servicos[7])
    mostrar_nos(lista, "Depois")

    titulo("Inserções no fim (ids 2, 11, 1, 9) - a antiga cauda passa a apontar para o novo nó")
    for i in (2, 11, 1, 9):
        cauda_antes = lista.cauda
        lista.inserir(servicos[i])
        print("   inserir(%d): %s.proximo = %s ; cauda = %s" % (
            i, rotulo_no(cauda_antes), rotulo_no(lista.cauda), rotulo_no(lista.cauda)))
    mostrar_nos(lista, "Depois")

    titulo("Tentativa de inserir ID duplicado (id 11)")
    try:
        lista.inserir(servicos[11])
    except IdDuplicadoError as erro:
        print("   Bloqueado -> IdDuplicadoError: %s" % erro)
    mostrar_nos(lista, "Lista inalterada")

    titulo("Consulta por ID com busca linear (existente, cabeça e inexistente)")
    for alvo in (1, 7, 99):
        servico, comp = busca_linear_por_id(lista, alvo)
        if servico is None:
            print("   busca_linear_por_id(%d): NÃO ENCONTRADO após %d comparações (percorreu tudo)" % (alvo, comp))
        else:
            print("   busca_linear_por_id(%d): %s após %d comparação(ões)" % (alvo, servico.resumo(), comp))

    titulo("Pesquisa textual (sem acento / sem maiúsculas)")
    for termo, campo in (("DOCUMENTACAO", "categoria"), ("cartão", "titulo"), ("passaporte", "ambos")):
        r = pesquisar_por_texto(lista, termo, campo)
        if r.encontrou:
            print("   pesquisar(%r, %s): %d resultado(s) -> %s" % (
                termo, campo, len(r), ", ".join(s.resumo() for s in r.registros)))
        else:
            print("   pesquisar(%r, %s): nenhum registro encontrado (%d comparações)" % (termo, campo, r.comparacoes))

    titulo("Atualização do registro 11 - só o dado muda, os ponteiros são preservados")
    no_11 = lista.cabeca.proximo.proximo
    prox_antes = no_11.proximo
    mostrar_nos(lista, "Antes ")
    print("   Local antes : %s" % no_11.dado.local_atendimento)
    alterados = lista.atualizar(11, local_atendimento="CRAS do município ou app Cadastro Único")
    print("   Campos alterados: %s" % alterados)
    print("   Local depois: %s" % no_11.dado.local_atendimento)
    print("   Mesmo nó? %s | mesmo proximo? %s" % (
        lista.cabeca.proximo.proximo is no_11, no_11.proximo is prox_antes))
    mostrar_nos(lista, "Depois")

    titulo("Remoção no INÍCIO (id 7) - cabeça avança para o segundo nó")
    mostrar_nos(lista, "Antes ")
    print("   removido: %s" % lista.remover(7).resumo())
    mostrar_nos(lista, "Depois")

    titulo("Remoção no MEIO (id 11) - o anterior passa a apontar para o sucessor")
    mostrar_nos(lista, "Antes ")
    print("   removido: %s" % lista.remover(11).resumo())
    mostrar_nos(lista, "Depois")

    titulo("Remoção no FIM (id 9) - a cauda recua para o anterior")
    mostrar_nos(lista, "Antes ")
    print("   removido: %s" % lista.remover(9).resumo())
    mostrar_nos(lista, "Depois")

    titulo("Remoção de ID inexistente (id 50)")
    try:
        lista.remover(50)
    except RegistroNaoEncontradoError as erro:
        print("   RegistroNaoEncontradoError: %s" % erro)
    mostrar_nos(lista, "Lista inalterada")

    titulo("Carga dos dados iniciais do Citizen Assist AI (ids já existentes são ignorados)")
    inseridos, ignorados = carregar_dados_iniciais(lista)
    print("   inseridos=%d, ignorados=%d" % (inseridos, ignorados))
    mostrar_nos(lista, "Depois")

    for criterio, desc in (("id", False), ("titulo", False), ("categoria", False), ("id", True)):
        titulo("Merge Sort por %s (%s) - religação dos nós existentes" % (
            criterio, "decrescente" if desc else "crescente"))
        enderecos_antes = set()
        atual = lista.cabeca
        while atual:
            enderecos_antes.add(id(atual))
            atual = atual.proximo
        print("Antes : %s" % lista.representar_encadeamento())
        comp = merge_sort_lista(lista, criterio, decrescente=desc)
        enderecos_depois = set()
        atual = lista.cabeca
        while atual:
            enderecos_depois.add(id(atual))
            atual = atual.proximo
        mostrar_nos(lista, "Depois")
        print("   Comparações: %d | mesmos %d nós reutilizados (nenhuma cópia): %s" % (
            comp, len(enderecos_depois), enderecos_antes == enderecos_depois))

    titulo("Análise por categoria")
    est = lista.estatisticas()
    print("   Total de registros: %d" % est["total"])
    for categoria, qtd, pct in est["categorias"]:
        print("   %-26s %2d  %6.2f%%  %s" % (categoria, qtd, pct, "#" * qtd))

    titulo("Limpar lista")
    print("   removidos: %d" % lista.limpar())
    mostrar_nos(lista, "Depois")
    print("\nDemonstração concluída com sucesso.")


if __name__ == "__main__":
    main()
