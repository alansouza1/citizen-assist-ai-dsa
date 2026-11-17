"""
models.py - Modelo de dados do Citizen Assist AI (DSA).

Define a classe ServicoCidadao, que representa UM registro de servico ou
orientacao ao cidadao. Cada objeto desta classe sera o "dado" guardado em
um no da ListaEncadeada (ver lista_encadeada.py).

Autor: Alan Junior Araujo de Souza - RM 574112 (Individual)
"""

# Campos textuais obrigatorios do registro (o id e tratado a parte).
CAMPOS_TEXTO = ("titulo", "categoria", "descricao", "requisitos", "local_atendimento")

# Nomes amigaveis usados no menu e nas mensagens.
ROTULOS = {
    "id": "ID",
    "titulo": "Título",
    "categoria": "Categoria",
    "descricao": "Descrição",
    "requisitos": "Requisitos",
    "local_atendimento": "Local de atendimento",
}


def validar_id(valor):
    """Converte e valida um identificador.

    Aceita int ou str numerica. Retorna o int validado (> 0).
    Lanca ValueError com mensagem amigavel em caso de entrada invalida.
    """
    if isinstance(valor, bool):  # bool e subclasse de int; nao faz sentido como id
        raise ValueError("O ID deve ser um número inteiro positivo.")
    if isinstance(valor, str):
        texto = valor.strip()
        if texto == "":
            raise ValueError("O ID não pode ser vazio.")
        try:
            valor = int(texto)
        except ValueError:
            raise ValueError("O ID deve ser um número inteiro (recebido: '%s')." % texto)
    if not isinstance(valor, int):
        raise ValueError("O ID deve ser um número inteiro positivo.")
    if valor <= 0:
        raise ValueError("O ID deve ser maior que zero (recebido: %d)." % valor)
    return valor


def validar_texto(nome_campo, valor):
    """Valida um campo textual obrigatorio: deve ser str e nao vazio."""
    if not isinstance(valor, str):
        raise ValueError("O campo '%s' deve ser um texto." % ROTULOS.get(nome_campo, nome_campo))
    texto = valor.strip()
    if texto == "":
        raise ValueError("O campo '%s' não pode ficar vazio." % ROTULOS.get(nome_campo, nome_campo))
    return texto


class ServicoCidadao:
    """Registro de um servico/orientacao do Citizen Assist AI.

    Atributos:
        id (int): identificador unico (chave da lista encadeada).
        titulo (str): nome curto do servico.
        categoria (str): area (Documentacao, Saude, Trabalho e Renda...).
        descricao (str): orientacao resumida ao cidadao.
        requisitos (str): documentos/condicoes exigidos.
        local_atendimento (str): onde o cidadao e atendido.
    """

    __slots__ = ("id",) + CAMPOS_TEXTO

    def __init__(self, id, titulo, categoria, descricao, requisitos, local_atendimento):
        self.id = validar_id(id)
        self.titulo = validar_texto("titulo", titulo)
        self.categoria = validar_texto("categoria", categoria)
        self.descricao = validar_texto("descricao", descricao)
        self.requisitos = validar_texto("requisitos", requisitos)
        self.local_atendimento = validar_texto("local_atendimento", local_atendimento)

    def atualizar_campo(self, campo, valor):
        """Atualiza um campo textual com validacao. O id NAO e editavel."""
        if campo == "id":
            raise ValueError("O ID é a chave única do registro e não pode ser alterado.")
        if campo not in CAMPOS_TEXTO:
            raise ValueError("Campo inexistente: '%s'." % campo)
        setattr(self, campo, validar_texto(campo, valor))

    def para_dict(self):
        """Retorna os dados como dicionario (util para exibicao e testes)."""
        dados = {"id": self.id}
        for campo in CAMPOS_TEXTO:
            dados[campo] = getattr(self, campo)
        return dados

    def resumo(self):
        """Representacao curta em uma linha."""
        return "[%d] %s (%s)" % (self.id, self.titulo, self.categoria)

    def detalhado(self):
        """Representacao completa em varias linhas, para o menu."""
        linhas = []
        for campo in ("id",) + CAMPOS_TEXTO:
            linhas.append("  %-21s: %s" % (ROTULOS[campo], getattr(self, campo)))
        return "\n".join(linhas)

    def __eq__(self, outro):
        return isinstance(outro, ServicoCidadao) and self.para_dict() == outro.para_dict()

    def __repr__(self):
        return "ServicoCidadao(id=%d, titulo=%r, categoria=%r)" % (self.id, self.titulo, self.categoria)

    __str__ = resumo
