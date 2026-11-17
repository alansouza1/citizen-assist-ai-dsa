"""
dados_iniciais.py - Carga inicial de servicos do Citizen Assist AI.

Os registros foram adaptados da base de conhecimento do projeto Citizen
Assist AI (fontes oficiais gov.br verificadas em 16/11/2026). Os IDs estao
propositalmente fora de ordem para evidenciar o efeito da ordenacao.

Autor: Alan Junior Araujo de Souza - RM 574112 (Individual)
"""

from models import ServicoCidadao
from lista_encadeada import IdDuplicadoError

DADOS_INICIAIS = (
    (7, "Pedir o seguro-desemprego", "Trabalho e Renda",
     "Benefício temporário para quem foi demitido sem justa causa; o pedido é gratuito e pode ser feito pela internet.",
     "Requerimento entregue pelo empregador, CPF e Carteira de Trabalho Digital",
     "App Carteira de Trabalho Digital, portal gov.br, telefone 158 ou unidade de atendimento do trabalhador"),
    (2, "Carteira de Identidade Nacional (CIN)", "Documentação",
     "Novo RG que usa o CPF como número único; a primeira via é gratuita e tem versão digital no app gov.br.",
     "Certidão de nascimento ou casamento e CPF regularizado",
     "Órgão de identificação do estado (em SP, Poupatempo)"),
    (11, "Inscrição no Cadastro Único (CadÚnico)", "Assistência Social",
     "Porta de entrada para programas sociais como Bolsa Família e Tarifa Social de Energia.",
     "CPF de todos os moradores e documento com foto do responsável familiar",
     "CRAS ou posto de cadastramento do município"),
    (1, "Tirar o CPF pela primeira vez", "Documentação",
     "Inscrição gratuita pela internet ou na Receita Federal; em conveniados há taxa de R$ 7,00.",
     "Documento oficial com foto e certidão de nascimento ou casamento",
     "Site da Receita Federal (gov.br), Correios, Banco do Brasil, Caixa ou cartórios"),
    (9, "Cartão Nacional de Saúde (Cartão SUS)", "Saúde",
     "Identifica o cidadão no SUS e dá acesso ao histórico de atendimentos e vacinas.",
     "Documento de identificação com foto e CPF",
     "Qualquer UBS ou aplicativo Meu SUS Digital"),
    (5, "Carteira de Trabalho Digital", "Trabalho e Renda",
     "Versão digital da carteira de trabalho, emitida automaticamente a partir do CPF.",
     "CPF e conta gov.br",
     "Aplicativo Carteira de Trabalho Digital ou portal gov.br"),
    (13, "Tarifa Social de Energia Elétrica", "Assistência Social",
     "Desconto na conta de luz para famílias de baixa renda inscritas no CadÚnico.",
     "Cadastro Único atualizado (NIS) e CPF do titular da conta",
     "Distribuidora de energia da região e CRAS"),
    (3, "Primeiro título de eleitor", "Documentação",
     "Alistamento eleitoral pelo Autoatendimento do TSE; voto opcional aos 16 e 17 anos.",
     "Documento oficial com foto e comprovante de residência recente",
     "Autoatendimento Eleitoral (site do TSE) ou cartório eleitoral"),
    (10, "Vacinação gratuita e caderneta", "Saúde",
     "Vacinas do Calendário Nacional são gratuitas; a caderneta pode ser atualizada na UBS.",
     "Caderneta de vacinação (se tiver) e documento com foto ou Cartão SUS",
     "Unidade Básica de Saúde (UBS) mais próxima"),
    (6, "Programa Jovem Aprendiz", "Educação e Qualificação",
     "Contrato de aprendizagem para jovens de 14 a 24 anos com curso de qualificação.",
     "CPF, Carteira de Trabalho Digital e matrícula escolar (se não concluiu o ensino médio)",
     "Entidades formadoras habilitadas e portal Emprega Brasil"),
    (12, "Reclamação de direitos do consumidor", "Serviços Urbanos",
     "Registro de reclamação contra empresas após tentativa de solução direta.",
     "Nota fiscal ou comprovante e protocolos de atendimento da empresa",
     "Site consumidor.gov.br ou Procon da cidade"),
    (4, "Alistamento militar obrigatório", "Documentação",
     "Obrigatório para homens no ano em que completam 18 anos; feito on-line ou na Junta.",
     "Conta gov.br e documento oficial com foto",
     "Site alistamento.eb.mil.br ou Junta de Serviço Militar"),
)


def criar_servicos_iniciais():
    """Cria os objetos ServicoCidadao da carga inicial (nova instancia a cada chamada)."""
    servicos = []
    for registro in DADOS_INICIAIS:
        servicos.append(ServicoCidadao(*registro))
    return servicos


def carregar_dados_iniciais(lista):
    """Insere os servicos iniciais na lista, ignorando ids ja existentes.

    Retorna (inseridos, ignorados).
    """
    inseridos = 0
    ignorados = 0
    for servico in criar_servicos_iniciais():
        try:
            lista.inserir(servico)
            inseridos += 1
        except IdDuplicadoError:
            ignorados += 1
    return inseridos, ignorados
