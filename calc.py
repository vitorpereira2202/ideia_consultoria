from dataclasses import dataclass
from typing import Dict

@dataclass
class Inputs:
    renda_liquida: float
    valor_carro: float
    km_mes: float
    consumo_km_l: float
    preco_combustivel: float
    manutencao_mensal: float
    seguro_anual: float
    ipva_percent_anual: float
    depreciacao_percent_anual: float

def custos_mensais(i: Inputs) -> Dict[str, float]:
    combustivel = 0.0 if i.consumo_km_l <= 0 else (i.km_mes / i.consumo_km_l) * i.preco_combustivel
    seguro_mensal = i.seguro_anual / 12.0
    ipva_mensal = (i.valor_carro * (i.ipva_percent_anual / 100.0)) / 12.0
    depreciacao_mensal = (i.valor_carro * (i.depreciacao_percent_anual / 100.0)) / 12.0
    total = combustivel + i.manutencao_mensal + seguro_mensal + ipva_mensal + depreciacao_mensal
    return {
        "combustivel": combustivel,
        "manutencao": i.manutencao_mensal,
        "seguro": seguro_mensal,
        "ipva": ipva_mensal,
        "depreciacao": depreciacao_mensal,
        "total": total
    }

def ias(custo_mensal_total: float, renda_liquida: float) -> float:
    return 999.0 if renda_liquida <= 0 else (custo_mensal_total / renda_liquida) * 100.0

def classificar_ias(ias_val: float) -> str:
    if ias_val < 10:
        return "Excelente (≤ 10%)"
    if ias_val <= 20:
        return "Adequado (10–20%)"
    if ias_val <= 30:
        return "Atenção (20–30%)"
    return "Crítico (> 30%)"

def custo_por_km(custo_mensal_total: float, km_mes: float) -> float:
    return 0.0 if km_mes <= 0 else custo_mensal_total / km_mes

def recomendacao_texto(ias_val: float, cpk: float) -> str:
    if ias_val <= 10:
        return "Relação carro × renda saudável. Mantenha preventiva e acompanhe consumo."
    if ias_val <= 20:
        return "Equilíbrio ok. Tente reduzir combustível/manutenção e defina meta de economia."
    if ias_val <= 30:
        return "Alerta: reveja quilometragem, consumo e seguro. Simule troca por modelo mais eficiente."
    return "Crítico: alto peso no orçamento. Considere vender/trocar ou renegociar seguro/financiamento."
