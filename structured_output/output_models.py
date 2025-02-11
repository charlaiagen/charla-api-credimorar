from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class FinancialInstitutionOutput(BaseModel):
    banco: str

class BradescoOutput(BaseModel):
    dados_primeiro_comprador: Dict[str, Dict[str, str]]
    dados_segundo_comprador: Dict[str, Dict[str, str]]
    dados_terceiro_comprador: Dict[str, Dict[str, str]]
    dados_quarto_comprador: Dict[str, Dict[str, str]]
    dados_bancarios: Dict[str, Dict[str, str]]
    dados_primeiro_vendedor: Dict[str, Dict[str, str]]
    dados_segundo_vendedor: Dict[str, Dict[str, str]]
    dados_imovel_financiado: Dict[str, Dict[str, str]]
    condicoes_operacao: Dict[str, Dict[str, str]]
    aceite_registro: str
    declaracoes_comprador: Dict[str, Dict[str, str]]