"""
lista_encadeada.py - Lista simplesmente encadeada implementada manualmente.

Estrutura:

    cabeca                                          cauda
      |                                               |
      v                                               v
   +-------+------+    +-------+------+    +-------+------+
   | dado  |  o---+--->| dado  |  o---+--->| dado  | None |
   +-------+------+    +-------+------+    +-------+------+
      No 1                 No 2                 No 3

- Cada No guarda um ServicoCidadao em `dado` e uma referencia `proximo`.
- A lista guarda referencias para o primeiro (cabeca) e o ultimo (cauda) no,
  alem de um contador de tamanho (_tamanho) mantido a cada operacao.
- Nenhuma estrutura nativa (list/dict) e usada para ARMAZENAR os registros.
  Colecoes auxiliares aparecem apenas em conversoes controladas
  (para_colecao / reconstruir_de_colecao) e em resultados de consultas.

Autor: Alan Junior Araujo de Souza - RM 574112 (Individual)
"""

from models import ServicoCidadao, validar_id, CAMPOS_TEXTO


class IdDuplicadoError(ValueError):
    """Lancada ao tentar inserir um registro cujo id ja existe na lista."""


class RegistroNaoEncontradoError(LookupError):
    """Lancada ao tentar atualizar/remover um id que nao existe."""


class ListaVaziaError(LookupError):
    """Lancada quando a operacao exige pelo menos um registro."""


class No:
    """No da lista encadeada: um dado e a referencia para o proximo no."""

    __slots__ = ("dado", "proximo")

    def __init__(self, dado, proximo=None):
        self.dado = dado
        self.proximo = proximo

    def __repr__(self):
        return "No(%s)" % self.dado.resumo()


class ListaEncadeada:
    """Lista simplesmente encadeada de ServicoCidadao com chave unica `id`."""

    def __init__(self):
        self.cabeca = None   # primeiro no (ou None se vazia)
        self.cauda = None    # ultimo no (ou None se vazia) -> insercao no fim em O(1)
        self._tamanho = 0    # contador mantido manualmente

    # ------------------------------------------------------------------ #
    # Utilitarios basicos
    # ------------------------------------------------------------------ #
    def __len__(self):
        return self._tamanho

    def esta_vazia(self):
        return self.cabeca is None

    def _exigir_nao_vazia(self, operacao):
        if self.esta_vazia():
            raise ListaVaziaError("A lista está vazia: não há registros para %s." % operacao)

    def _localizar(self, id_procurado):
        """Percorre a lista e retorna (anterior, atual) do no com o id.

        Se nao encontrar, retorna (ultimo_no, None). Complexidade O(n).
        Usado internamente por consulta, atualizacao e remocao.
        """
        anterior = None
        atual = self.cabeca
        while atual is not None:
            if atual.dado.id == id_procurado:
                return anterior, atual
            anterior = atual
            atual = atual.proximo
        return anterior, None

    def contem_id(self, id_procurado):
        return self._localizar(id_procurado)[1] is not None

    # ------------------------------------------------------------------ #
    # 1) Insercao
    # ------------------------------------------------------------------ #
    def inserir(self, servico):
        """Insere um ServicoCidadao no FIM da lista.

        Antes de encadear, percorre a lista verificando id duplicado
        (O(n)). O encadeamento em si e O(1) gracas ao ponteiro `cauda`.
        Lanca IdDuplicadoError se o id ja existir.
        """
        if not isinstance(servico, ServicoCidadao):
            raise TypeError("Somente objetos ServicoCidadao podem ser inseridos.")
        if self.contem_id(servico.id):
            raise IdDuplicadoError("Já existe um registro com o ID %d." % servico.id)

        novo = No(servico)
        if self.esta_vazia():
            self.cabeca = novo
            self.cauda = novo
        else:
            self.cauda.proximo = novo   # o antigo ultimo passa a apontar para o novo
            self.cauda = novo           # o novo vira a cauda
        self._tamanho += 1
        return novo

    def inserir_no_inicio(self, servico):
        """Insere na CABECA da lista (encadeamento O(1); checagem de duplicado O(n))."""
        if not isinstance(servico, ServicoCidadao):
            raise TypeError("Somente objetos ServicoCidadao podem ser inseridos.")
        if self.contem_id(servico.id):
            raise IdDuplicadoError("Já existe um registro com o ID %d." % servico.id)
        novo = No(servico, self.cabeca)
        self.cabeca = novo
        if self.cauda is None:
            self.cauda = novo
        self._tamanho += 1
        return novo

    # ------------------------------------------------------------------ #
    # 2) Percurso / listagem
    # ------------------------------------------------------------------ #
    def percorrer(self):
        """Gerador que visita cada no da cabeca ate a cauda, entregando o dado."""
        atual = self.cabeca
        while atual is not None:
            yield atual.dado
            atual = atual.proximo

    def listar(self):
        """Retorna as linhas de exibicao de todos os registros (percurso O(n))."""
        linhas = []
        posicao = 1
        for servico in self.percorrer():
            linhas.append("%2d. %s" % (posicao, servico.resumo()))
            posicao += 1
        return linhas

    def representar_encadeamento(self):
        """Mostra os nos e as referencias: HEAD -> [1] -> [5] -> None."""
        partes = ["HEAD"]
        atual = self.cabeca
        while atual is not None:
            partes.append("[%d]" % atual.dado.id)
            atual = atual.proximo
        partes.append("None")
        texto = " -> ".join(partes)
        cab = self.cabeca.dado.id if self.cabeca else None
        cau = self.cauda.dado.id if self.cauda else None
        return "%s   (tamanho=%d, cabeca=%s, cauda=%s)" % (texto, self._tamanho, cab, cau)

    # ------------------------------------------------------------------ #
    # 3) Consulta exata por id
    # ------------------------------------------------------------------ #
    def buscar_por_id(self, id_procurado):
        """Retorna o ServicoCidadao com o id ou None se nao existir. O(n)."""
        id_procurado = validar_id(id_procurado)
        no = self._localizar(id_procurado)[1]
        return no.dado if no is not None else None

    # ------------------------------------------------------------------ #
    # 4) Atualizacao
    # ------------------------------------------------------------------ #
    def atualizar(self, id_procurado, **novos_valores):
        """Atualiza campos de um registro existente.

        O no permanece no mesmo lugar: somente o `dado` e alterado, por isso
        os encadeamentos (proximo, cabeca, cauda) sao preservados.
        Valida TODOS os campos antes de alterar qualquer um (atomicidade).
        Retorna a lista de campos efetivamente alterados.
        """
        id_procurado = validar_id(id_procurado)
        self._exigir_nao_vazia("atualizar")
        if not novos_valores:
            raise ValueError("Nenhum campo informado para atualização.")
        no = self._localizar(id_procurado)[1]
        if no is None:
            raise RegistroNaoEncontradoError("Nenhum registro com o ID %d." % id_procurado)

        # Validacao previa em uma copia, para nao deixar o registro pela metade.
        dados = no.dado.para_dict()
        for campo, valor in novos_valores.items():
            if campo == "id":
                raise ValueError("O ID é a chave única do registro e não pode ser alterado.")
            if campo not in CAMPOS_TEXTO:
                raise ValueError("Campo inexistente: '%s'." % campo)
            dados[campo] = valor
        ServicoCidadao(**dados)  # valida tudo; lanca ValueError se algo for invalido

        alterados = []
        for campo, valor in novos_valores.items():
            antigo = getattr(no.dado, campo)
            no.dado.atualizar_campo(campo, valor)
            if getattr(no.dado, campo) != antigo:
                alterados.append(campo)
        return alterados

    # ------------------------------------------------------------------ #
    # 5) Remocao (inicio, meio e fim)
    # ------------------------------------------------------------------ #
    def remover(self, id_procurado):
        """Remove o no com o id e devolve o ServicoCidadao removido.

        Casos tratados:
          - inicio: cabeca passa a ser cabeca.proximo;
          - meio:   anterior.proximo "pula" o no removido;
          - fim:    alem do salto, a cauda passa a ser o anterior;
          - unico:  cabeca e cauda viram None.
        """
        id_procurado = validar_id(id_procurado)
        self._exigir_nao_vazia("remover")
        anterior, atual = self._localizar(id_procurado)
        if atual is None:
            raise RegistroNaoEncontradoError("Nenhum registro com o ID %d." % id_procurado)

        if anterior is None:                 # remocao no inicio
            self.cabeca = atual.proximo
        else:                                # remocao no meio ou no fim
            anterior.proximo = atual.proximo
        if atual is self.cauda:              # removeu o ultimo -> atualiza cauda
            self.cauda = anterior
        atual.proximo = None                 # desliga o no removido da lista
        self._tamanho -= 1
        return atual.dado

    def limpar(self):
        """Remove todos os registros (as referencias sao liberadas p/ o GC)."""
        quantidade = self._tamanho
        self.cabeca = None
        self.cauda = None
        self._tamanho = 0
        return quantidade

    # ------------------------------------------------------------------ #
    # 6) Analise / estatisticas
    # ------------------------------------------------------------------ #
    def estatisticas(self):
        """Total de registros e contagem/percentual por categoria.

        Retorna dict:
          {"total": n, "categorias": [(categoria, quantidade, percentual), ...]}
        As categorias aparecem na ordem da primeira ocorrencia na lista e a
        contagem e feita em um unico percurso (O(n * k), k = n. de categorias).
        """
        nomes = []     # colecao auxiliar de resultado (nao armazena registros)
        contagens = []
        for servico in self.percorrer():
            achou = False
            i = 0
            while i < len(nomes):
                if nomes[i] == servico.categoria:
                    contagens[i] += 1
                    achou = True
                    break
                i += 1
            if not achou:
                nomes.append(servico.categoria)
                contagens.append(1)
        total = self._tamanho
        categorias = []
        i = 0
        while i < len(nomes):
            percentual = (contagens[i] * 100.0 / total) if total else 0.0
            categorias.append((nomes[i], contagens[i], round(percentual, 2)))
            i += 1
        return {"total": total, "categorias": categorias}

    # ------------------------------------------------------------------ #
    # 7) Conversao controlada lista <-> colecao auxiliar
    # ------------------------------------------------------------------ #
    def para_colecao(self):
        """Copia as REFERENCIAS dos registros para uma list Python (O(n)).

        A lista encadeada NAO e alterada. Usada apenas quando um algoritmo
        precisa de acesso por indice (ex.: ordenar_via_colecao).
        """
        colecao = []
        for servico in self.percorrer():
            colecao.append(servico)
        return colecao

    def reconstruir_de_colecao(self, colecao):
        """Reconstroi o encadeamento a partir de uma colecao de registros.

        Valida antes (tipos e ids unicos) para nunca deixar a lista em estado
        inconsistente; so entao substitui os nos. O(n^2) no pior caso por
        causa da checagem de duplicados feita pela propria insercao.
        """
        temporaria = ListaEncadeada()
        for servico in colecao:
            temporaria.inserir(servico)  # valida tipo e duplicidade
        self.cabeca = temporaria.cabeca
        self.cauda = temporaria.cauda
        self._tamanho = temporaria._tamanho
        return self

    @classmethod
    def de_colecao(cls, colecao):
        return cls().reconstruir_de_colecao(colecao)

    def ids(self):
        """Ids na ordem atual da lista (util para testes e demonstracao)."""
        return [s.id for s in self.percorrer()]

    # ------------------------------------------------------------------ #
    # Verificacao de integridade (usada nos testes e na demonstracao)
    # ------------------------------------------------------------------ #
    def verificar_integridade(self):
        """Confere: sem ciclos, contador correto, cauda correta, ids unicos."""
        if self.cabeca is None:
            return self.cauda is None and self._tamanho == 0
        visitados = 0
        ultimo = None
        atual = self.cabeca
        ids_vistos = set()
        while atual is not None:
            visitados += 1
            if visitados > self._tamanho:     # mais nos que o contador -> ciclo/erro
                return False
            if atual.dado.id in ids_vistos:
                return False
            ids_vistos.add(atual.dado.id)
            ultimo = atual
            atual = atual.proximo
        return visitados == self._tamanho and ultimo is self.cauda and self.cauda.proximo is None
