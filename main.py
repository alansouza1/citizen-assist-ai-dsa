"""
main.py - Menu interativo do Citizen Assist AI (DSA).

Execução:  python main.py

Todas as entradas inválidas (texto no lugar de número, campos vazios,
opções inexistentes, IDs duplicados, registros inexistentes e operações
com lista vazia) são tratadas com mensagens amigáveis, sem traceback.

Autor: Alan Júnior Araújo de Souza - RM 574112 (Individual)
"""

from models import ServicoCidadao, CAMPOS_TEXTO, ROTULOS, validar_id, validar_texto
from lista_encadeada import (
    ListaEncadeada, IdDuplicadoError, RegistroNaoEncontradoError, ListaVaziaError,
)
from algoritmos import (
    busca_linear_por_id, pesquisar_por_texto, merge_sort_lista, CRITERIOS_ORDENACAO,
)
from dados_iniciais import carregar_dados_iniciais

LINHA = "=" * 64
SUB = "-" * 64

MENU = """
{linha}
   CITIZEN ASSIST AI  |  Serviços e orientações ao cidadão (DSA)
{linha}
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
{sub}""".format(linha=LINHA, sub=SUB)


class EntradaCancelada(Exception):
    """Usuário encerrou a entrada (Ctrl+D / Ctrl+C) no meio de uma operação."""


# ---------------------------------------------------------------------- #
# Helpers de entrada (nunca deixam exceções escaparem para o usuário)
# ---------------------------------------------------------------------- #
def ler(prompt):
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        raise EntradaCancelada()


def ler_texto_obrigatorio(campo, tentativas=3):
    """Lê um campo de texto não vazio, com até `tentativas` tentativas."""
    for _ in range(tentativas):
        try:
            return validar_texto(campo, ler("  %s: " % ROTULOS[campo]))
        except ValueError as erro:
            print("  [!] %s" % erro)
    raise ValueError("Número máximo de tentativas excedido para '%s'." % ROTULOS[campo])


def ler_id(prompt="  Informe o ID: "):
    """Lê e valida um ID inteiro positivo (lança ValueError se inválido)."""
    return validar_id(ler(prompt))


def confirmar(prompt):
    resposta = ler(prompt + " (s/n): ").strip().lower()
    return resposta in ("s", "sim", "y", "yes")


def lista_vazia(lista, acao):
    if lista.esta_vazia():
        print("  [i] A lista está vazia: não há registros para %s." % acao)
        print("      Use a opção 1 para cadastrar ou a opção 9 para carregar os dados iniciais.")
        return True
    return False


# ---------------------------------------------------------------------- #
# Operações do menu
# ---------------------------------------------------------------------- #
def op_cadastrar(lista):
    print("\n[1] CADASTRAR SERVIÇO")
    id_novo = ler_id("  ID (inteiro positivo): ")
    if lista.contem_id(id_novo):
        raise IdDuplicadoError("Já existe um registro com o ID %d. Escolha outro ID." % id_novo)
    valores = {}
    for campo in CAMPOS_TEXTO:
        valores[campo] = ler_texto_obrigatorio(campo)
    servico = ServicoCidadao(id_novo, **valores)
    lista.inserir(servico)
    print("  [OK] Serviço cadastrado: %s" % servico.resumo())
    print("  Encadeamento: %s" % lista.representar_encadeamento())


def op_listar(lista):
    print("\n[2] LISTAR TODOS (percurso da cabeça até a cauda)")
    if lista_vazia(lista, "listar"):
        return
    for linha in lista.listar():
        print("  " + linha)
    print("  Total: %d registro(s)" % len(lista))


def op_consultar(lista):
    print("\n[3] CONSULTAR POR ID (busca linear)")
    if lista_vazia(lista, "consultar"):
        return
    id_proc = ler_id()
    servico, comparacoes = busca_linear_por_id(lista, id_proc)
    if servico is None:
        print("  [i] Nenhum registro encontrado com o ID %d (%d comparações)." % (id_proc, comparacoes))
        return
    print("  [OK] Registro encontrado após %d comparação(ões):" % comparacoes)
    print(servico.detalhado())


def op_pesquisar(lista):
    print("\n[4] PESQUISAR POR TÍTULO/CATEGORIA (sem diferenciar maiúsculas e acentos)")
    if lista_vazia(lista, "pesquisar"):
        return
    print("  Campo: 1-Título  2-Categoria  3-Ambos")
    opcoes = {"1": "titulo", "2": "categoria", "3": "ambos"}
    escolha = ler("  Escolha o campo [3]: ").strip() or "3"
    if escolha not in opcoes:
        print("  [!] Opção de campo inexistente: '%s'." % escolha)
        return
    termo = ler("  Termo de pesquisa: ")
    resultado = pesquisar_por_texto(lista, termo, opcoes[escolha])
    if not resultado.encontrou:
        print("  [i] Nenhum registro encontrado para '%s' (%d comparações)." % (termo.strip(), resultado.comparacoes))
        return
    print("  [OK] %d registro(s) encontrado(s) (%d comparações):" % (len(resultado), resultado.comparacoes))
    for servico in resultado.registros:
        print("    - " + servico.resumo())


def op_atualizar(lista):
    print("\n[5] ATUALIZAR REGISTRO")
    if lista_vazia(lista, "atualizar"):
        return
    id_proc = ler_id()
    servico = lista.buscar_por_id(id_proc)
    if servico is None:
        raise RegistroNaoEncontradoError("Nenhum registro com o ID %d." % id_proc)
    print("  Dados atuais:")
    print(servico.detalhado())
    print("  Digite o novo valor ou pressione Enter para manter o atual.")
    novos = {}
    for campo in CAMPOS_TEXTO:
        valor = ler("  %s: " % ROTULOS[campo])
        if valor.strip() != "":
            novos[campo] = valor
    if not novos:
        print("  [i] Nenhuma alteração informada. Registro mantido.")
        return
    alterados = lista.atualizar(id_proc, **novos)
    if alterados:
        nomes = ", ".join(ROTULOS[c] for c in alterados)
        print("  [OK] Registro %d atualizado (campos: %s)." % (id_proc, nomes))
    else:
        print("  [i] Os valores informados são iguais aos atuais. Nada mudou.")
    print("  Encadeamento preservado: %s" % lista.representar_encadeamento())


def op_excluir(lista):
    print("\n[6] EXCLUIR REGISTRO")
    if lista_vazia(lista, "excluir"):
        return
    id_proc = ler_id()
    servico = lista.buscar_por_id(id_proc)
    if servico is None:
        raise RegistroNaoEncontradoError("Nenhum registro com o ID %d." % id_proc)
    print("  Registro: %s" % servico.resumo())
    if not confirmar("  Confirma a exclusão?"):
        print("  [i] Exclusão cancelada.")
        return
    lista.remover(id_proc)
    print("  [OK] Registro %d removido." % id_proc)
    print("  Encadeamento: %s" % lista.representar_encadeamento())


def op_ordenar(lista):
    print("\n[7] ORDENAR REGISTROS (Merge Sort sobre os nós da lista)")
    if lista_vazia(lista, "ordenar"):
        return
    print("  Critério: 1-ID  2-Título  3-Categoria")
    escolha = ler("  Escolha o critério: ").strip()
    criterios = {"1": "id", "2": "titulo", "3": "categoria"}
    if escolha not in criterios:
        print("  [!] Critério inexistente: '%s'. Use 1, 2 ou 3." % escolha)
        return
    ordem = ler("  Ordem: 1-Crescente  2-Decrescente [1]: ").strip() or "1"
    if ordem not in ("1", "2"):
        print("  [!] Ordem inexistente: '%s'. Use 1 ou 2." % ordem)
        return
    criterio = criterios[escolha]
    print("  Antes : %s" % lista.representar_encadeamento())
    comparacoes = merge_sort_lista(lista, criterio, decrescente=(ordem == "2"))
    print("  Depois: %s" % lista.representar_encadeamento())
    print("  [OK] Lista reorganizada por %s (%s) com %d comparações." % (
        ROTULOS[criterio], "decrescente" if ordem == "2" else "crescente", comparacoes))
    for linha in lista.listar():
        print("  " + linha)


def op_analise(lista):
    print("\n[8] ANÁLISE POR CATEGORIA")
    if lista_vazia(lista, "analisar"):
        return
    est = lista.estatisticas()
    print("  Total de registros: %d" % est["total"])
    print("  %-28s %10s %10s" % ("Categoria", "Qtd.", "%"))
    print("  " + "-" * 50)
    for categoria, qtd, pct in est["categorias"]:
        barra = "#" * int(round(pct / 5))
        print("  %-28s %10d %9.2f%%  %s" % (categoria, qtd, pct, barra))
    maior = est["categorias"][0]
    for item in est["categorias"]:
        if item[1] > maior[1]:
            maior = item
    print("  Categoria com mais serviços: %s (%d)" % (maior[0], maior[1]))


def op_dados(lista):
    print("\n[9] DADOS INICIAIS / LIMPAR LISTA")
    print("  1-Carregar dados iniciais do Citizen Assist AI")
    print("  2-Limpar lista (remover todos os registros)")
    print("  0-Voltar")
    escolha = ler("  Escolha: ").strip()
    if escolha == "1":
        inseridos, ignorados = carregar_dados_iniciais(lista)
        print("  [OK] %d registro(s) inserido(s); %d ignorado(s) por ID já existente." % (inseridos, ignorados))
        print("  Encadeamento: %s" % lista.representar_encadeamento())
    elif escolha == "2":
        if lista.esta_vazia():
            print("  [i] A lista já está vazia.")
            return
        if confirmar("  Remover TODOS os %d registros?" % len(lista)):
            print("  [OK] %d registro(s) removido(s)." % lista.limpar())
        else:
            print("  [i] Operação cancelada.")
    elif escolha == "0":
        return
    else:
        print("  [!] Opção inexistente: '%s'." % escolha)


OPERACOES = {
    "1": op_cadastrar, "2": op_listar, "3": op_consultar, "4": op_pesquisar,
    "5": op_atualizar, "6": op_excluir, "7": op_ordenar, "8": op_analise,
    "9": op_dados,
}


def executar_menu(lista=None):
    """Laço principal do menu. Retorna a lista ao encerrar (útil nos testes)."""
    if lista is None:
        lista = ListaEncadeada()
    while True:
        print(MENU)
        try:
            opcao = ler("Escolha uma opção: ").strip()
        except EntradaCancelada:
            print("\nEntrada encerrada. Até logo!")
            return lista
        if opcao == "0":
            print("Encerrando o Citizen Assist AI. Até logo!")
            return lista
        operacao = OPERACOES.get(opcao)
        if operacao is None:
            if opcao == "":
                print("[!] Nenhuma opção informada. Digite um número de 0 a 9.")
            else:
                print("[!] Opção inexistente: '%s'. Digite um número de 0 a 9." % opcao)
            continue
        try:
            operacao(lista)
        except EntradaCancelada:
            print("\n  [i] Operação cancelada pelo usuário.")
        except IdDuplicadoError as erro:
            print("  [!] ID duplicado: %s" % erro)
        except (RegistroNaoEncontradoError, ListaVaziaError) as erro:
            print("  [i] %s" % (erro.args[0] if erro.args else erro))
        except ValueError as erro:
            print("  [!] Entrada inválida: %s" % erro)
        except Exception as erro:  # rede de segurança: nunca exibir traceback
            print("  [!] Erro inesperado: %s" % erro)


if __name__ == "__main__":
    executar_menu()
