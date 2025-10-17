import streamlit as st
import pandas as pd
import plotly.express as px

from calc import (
    Inputs, custos_mensais, ias, classificar_ias,
    custo_por_km, recomendacao_texto
)
from pdf_report import gerar_pdf_bytes

st.set_page_config(page_title="Ideia Consultoria - AutoSmart", page_icon="🚗", layout="wide")
st.title("🚗💰 AutoSmart — Consultoria Automotiva Inteligente (MVP)")

st.markdown("""
Preencha os dados para estimar **custo mensal**, **custo por km** e o **IAS** (Índice AutoSmart).
Use estimativas — você pode ajustar depois.
""")

# Estado para persistir o resultado após o submit
if "resultado" not in st.session_state:
    st.session_state["resultado"] = None

with st.form("form"):
    colA, colB, colC = st.columns(3)
    with colA:
        renda = st.number_input("Renda líquida mensal (R$)", min_value=0.0, value=4000.0, step=100.0)
        valor_carro = st.number_input("Valor do carro (R$)", min_value=0.0, value=90000.0, step=1000.0)
        km_mes = st.number_input("Km rodados por mês", min_value=0.0, value=1000.0, step=50.0)
    with colB:
        consumo = st.number_input("Consumo médio (km/l)", min_value=0.0, value=11.0, step=0.5)
        preco_comb = st.number_input("Preço do combustível (R$/l)", min_value=0.0, value=5.90, step=0.1, format="%.2f")
        manut = st.number_input("Manutenção mensal (R$)", min_value=0.0, value=200.0, step=50.0)
    with colC:
        seguro_anual = st.number_input("Seguro anual (R$)", min_value=0.0, value=3500.0, step=100.0)
        ipva_pct = st.number_input("IPVA (% ao ano)", min_value=0.0, value=4.0, step=0.5)
        dep_pct = st.number_input("Depreciação (% ao ano)", min_value=0.0, value=10.0, step=0.5)

    submitted = st.form_submit_button("Calcular", type="primary", use_container_width=True)

if submitted:
    i = Inputs(
        renda_liquida=renda,
        valor_carro=valor_carro,
        km_mes=km_mes,
        consumo_km_l=consumo,
        preco_combustivel=preco_comb,
        manutencao_mensal=manut,
        seguro_anual=seguro_anual,
        ipva_percent_anual=ipva_pct,
        depreciacao_percent_anual=dep_pct
    )
    custos = custos_mensais(i)
    total = custos["total"]
    ias_val = ias(total, renda)
    ias_classe = classificar_ias(ias_val)
    cpk = custo_por_km(total, km_mes)
    saldo = renda - total
    rec = recomendacao_texto(ias_val, cpk)

    st.session_state["resultado"] = {
        "custos": custos,
        "total": total,
        "ias_val": ias_val,
        "ias_classe": ias_classe,
        "cpk": cpk,
        "saldo": saldo,
        "renda": renda,
        "km_mes": km_mes,
        "rec": rec,
    }

# Renderização após cálculo
res = st.session_state["resultado"]
if res is not None:
    custos = res["custos"]
    total = res["total"]
    ias_val = res["ias_val"]
    ias_classe = res["ias_classe"]
    cpk = res["cpk"]
    saldo = res["saldo"]
    renda = res["renda"]
    km_mes = res["km_mes"]
    rec = res["rec"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Custo mensal total", f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    c2.metric("IAS (custo/renda × 100)", f"{ias_val:.1f}%")
    c3.metric("Custo por km", f"R$ {cpk:.2f}")
    st.info(f"Classificação do IAS: **{ias_classe}**")

    comp_df = pd.DataFrame({
        "Componente": ["Combustível", "Manutenção", "Seguro", "IPVA", "Depreciação"],
        "Valor": [
            custos["combustivel"], custos["manutencao"],
            custos["seguro"], custos["ipva"], custos["depreciacao"]
        ]
    })
    fig = px.pie(comp_df, names="Componente", values="Valor", title="Distribuição de custos mensais")
    st.plotly_chart(fig, use_container_width=True)

    st.write(
        f"**Saldo mensal após o carro:** R$ {saldo:,.2f}"
        .replace(",", "X").replace(".", ",").replace("X", ".")
    )

    st.subheader("Recomendações")
    st.write(rec)

    # Download do PDF (sem st.button para evitar rerun)
    kpis_fmt = {
        "Custo mensal total": f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        "IAS": f"{ias_val:.1f}% ({ias_classe})",
        "Custo por km": f"R$ {cpk:.2f}",
        "Renda líquida": f"R$ {renda:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        "Km/mês": f"{km_mes:,.0f}".replace(",", ".")
    }
    barras = {
        "Combustível": custos["combustivel"],
        "Manutenção": custos["manutencao"],
        "Seguro": custos["seguro"],
        "IPVA": custos["ipva"],
        "Depreciação": custos["depreciacao"]
    }
    pdf_bytes = gerar_pdf_bytes(kpis_fmt, barras, rec)
    st.download_button(
        "📄 Download do PDF",
        data=pdf_bytes,
        file_name="AutoSmart_Relatorio.pdf",
        mime="application/pdf",
        use_container_width=True
    )
