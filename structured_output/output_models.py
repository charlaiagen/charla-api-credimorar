from pydantic import BaseModel, Field
from typing import Optional

class FinancialInstitutionOutput(BaseModel):
    banco: str = Field(default="")

class DadosComprador(BaseModel):
    nome_completo: str = Field(default="")
    cpf_mf: str = Field(default="")
    profissao: str = Field(default="")
    e_mail: str = Field(default="")
    estado_civil: str = Field(default="")
    campo_obrigatorio_para_quem_nao_e_casado_vive_em_uniao_estavel: str = Field(default="")
    e_funcionario_da_organizacao_bradesco_ou_parente_de_primeiro_grau_pai_ou_filho: str = Field(default="")
    se_sim_informe_codigo_funcional: str = Field(default="")

class DadosBancarios(BaseModel):
    autorizo_o_debito_pagamento_do_valor_das_prestacoes_por_meio_de: str = Field(default="")
    para_opcao_de_pagamento_das_prestacoes_por_meio_debito_em_conta_corrente_informar: str = Field(default="")
    conta_de_titularidade_do_comprador_que_autorizou_o_debito: str = Field(default="")
    nome: str = Field(default="")
    agencia_debito_parcela: str = Field(default="")
    conta_debito_parcela: str = Field(default="")
    digito_conta: str = Field(default="")
    autorizo_utilizar_o_limite_de_credito_incluindo_o_cheque_especial_se_contratados_quando_nao_houver_saldo_em_conta: str = Field(default="")
    autorizo_o_debito_do_valor_da_s_prestacao_s_vencida_s_inclusive_de_valor_es_parcial_is_os_encargos_serao_incorporados_nas_prestacoes_seguintes_conforme_detalhado_em_contrato: str = Field(default="")

class DadosVendedor(BaseModel):
    nome_completo_razao_social: str = Field(default="")
    cpf_cnpj_mf: str = Field(default="")
    profissao: str = Field(default="")
    e_mail: str = Field(default="")
    estado_civil: str = Field(default="")
    campo_obrigatorio_para_quem_nao_e_casado_vive_em_uniao_estavel: str = Field(default="")
    forma_de_recebimento: str = Field(default="")
    banco: str = Field(default="")
    agencia: str = Field(default="")
    digito: str = Field(default="")
    conta: str = Field(default="")

class DadosImovel(BaseModel):
    endereco: str = Field(default="")
    numero: str = Field(default="")
    complemento: str = Field(default="")
    quantidade_de_vagas: str = Field(default="")
    n_de_vagas: str = Field(default="")
    quantidade_deposito_box: str = Field(default="")
    n_deposito_box: str = Field(default="")

class CondicoesOperacao(BaseModel):
    valor_da_compra_venda: str = Field(default="")
    valor_de_financiamento: str = Field(default="")
    ira_utilizar_o_fgts: str = Field(default="")
    prazo_de_amortizacao: str = Field(default="")
    dia_base_para_pagamento_das_prestacoes_de_01_a_28: str = Field(default="")
    sistema_de_amortizacao: str = Field(default="")
    deseja_incluir_despesas_cartorarias_no_financiamento: str = Field(default="")

class DeclaracoesComprador(BaseModel):
    o_s_comprador_es_concordam_com_a_dispensa: str = Field(default="")
    declaracao_de_inexistencia_de_debitos_condominiais: str = Field(default="")
    certidao_negativa_de_impostos_e_taxas_municipais: str = Field(default="")
    declaracao_de_regularidade_de_foro_para_imoveis_foreiros: str = Field(default="")

class BradescoOutput(BaseModel):
    dados_do_1o_comprador: DadosComprador = Field(default_factory=DadosComprador)
    dados_do_2o_comprador: DadosComprador = Field(default_factory=DadosComprador)
    dados_do_3o_comprador: DadosComprador = Field(default_factory=DadosComprador)
    dados_do_4o_comprador: DadosComprador = Field(default_factory=DadosComprador)
    dados_bancarios_pagamento_das_prestacoes: DadosBancarios = Field(default_factory=DadosBancarios)
    dados_do_s_1o_vendedor_es_pessoa_fisica_pessoa_juridica: DadosVendedor = Field(default_factory=DadosVendedor)
    dados_do_s_2o_vendedor_es_pessoa_fisica_pessoa_juridica: DadosVendedor = Field(default_factory=DadosVendedor)
    dados_do_imovel_a_ser_financiado: DadosImovel = Field(default_factory=DadosImovel)
    condicoes_da_operacao_todos_os_itens_deste_bloco_sao_de_preenchimento_obrigatorio: CondicoesOperacao = Field(default_factory=CondicoesOperacao)
    aceite_registro_eletronico_assinatura_digital: str = Field(default="")
    declaracoes_do_s_comprador_es: DeclaracoesComprador = Field(default_factory=DeclaracoesComprador)