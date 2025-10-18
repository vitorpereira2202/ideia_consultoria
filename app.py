import streamlit as st
import pandas as pd
import plotly.express as px

from calc import (
    Inputs, custos_mensais, ias, classificar_ias,
    custo_por_km, recomendacao_texto, resumo
)
from pdf_report import gerar_pdf_bytes

st.set_page_config(page_title="Ideia Consultoria - AutoSmart", page_icon="🚗", layout="wide")
st.title("🚗💰 AutoSmart — Consultoria Automotiva Inteligente (MVP)")

tabs = st.tabs(["Análise única", "Comparador"])

# -------------------- ABA 1: ANÁLISE ÚNICA --------------------
with tabs[0]:
    st.markdown("""
Preencha os dados para estimar **custo mensal**, **custo por km** e o **IAS** (Índice AutoSmart).
Use estimativas — você pode ajustar depois.
""")

    if "resultado" not in st.session_state:
        st.session_state["resultado"] = None

    with st.form("form_unico"):
        colA, colB, colC = st.columns(3)
        with colA:
            renda = st.number_input("Renda líquida mensal (R$)", min_value=0.0, value=4000.0, step=100.0, key="renda_u")
            valor_carro = st.number_input("Valor do carro (R$)", min_value=0.0, value=90000.0, step=1000.0, key="valor_u")
            km_mes = st.number_input("Km rodados por mês", min_value=0.0, value=1000.0, step=50.0, key="km_u")
        with colB:
            consumo = st.number_input("Consumo médio (km/l)", min_value=0.0, value=11.0, step=0.5, key="consumo_u")
            preco_comb = st.number_input("Preço do combustível (R$/l)", min_value=0.0, value=5.90, step=0.1, format="%.2f", key="comb_u")
            manut = st.number_input("Manutenção mensal (R$)", min_value=0.0, value=200.0, step=50.0, key="manut_u")
        with colC:
            seguro_anual = st.number_input("Seguro anual (R$)", min_value=0.0, value=3500.0, step=100.0, key="seguro_u")
            ipva_pct = st.number_input("IPVA (% ao ano)", min_value=0.0, value=4.0, step=0.5, key="ipva_u")
            dep_pct = st.number_input("Depreciação (% ao ano)", min_value=0.0, value=10.0, step=0.5, key="dep_u")

        submitted = st.form_submit_button("Calcular", type="primary", use_container_width=True)

    if submitted:
        i = Inputs(
            renda_liquida=renda, valor_carro=valor_carro, km_mes=km_mes,
            consumo_km_l=consumo, preco_combustivel=preco_comb, manutencao_mensal=manut,
            seguro_anual=seguro_anual, ipva_percent_anual=ipva_pct, depreciacao_percent_anual=dep_pct
        )
        st.session_state["resultado"] = resumo(i)

    res = st.session_state["resultado"]
    if res:
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
            "Valor": [custos["combustivel"], custos["manutencao"], custos["seguro"], custos["ipva"], custos["depreciacao"]]
        })
        fig = px.pie(comp_df, names="Componente", values="Valor", title="Distribuição de custos mensais")
        st.plotly_chart(fig, use_container_width=True)

        st.write(f"**Saldo mensal após o carro:** R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        st.subheader("Recomendações")
        st.write(rec)

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

# -------------------- ABA 2: COMPARADOR --------------------
with tabs[1]:
    st.markdown("Compare **dois veículos** lado a lado e receba uma recomendação automática.")

    with st.form("form_compare"):
        st.subheader("Parâmetros gerais")
        renda_c = st.number_input("Renda líquida mensal (R$)", min_value=0.0, value=4000.0, step=100.0, key="renda_c")

        st.subheader("Carro A")
        colA1, colA2, colA3 = st.columns(3)
        with colA1:
            valor_a = st.number_input("Valor do carro A (R$)", min_value=0.0, value=90000.0, step=1000.0, key="valor_a")
            km_a = st.number_input("Km/mês A", min_value=0.0, value=1000.0, step=50.0, key="km_a")
        with colA2:
            cons_a = st.number_input("Consumo A (km/l)", min_value=0.0, value=11.0, step=0.5, key="cons_a")
            comb_a = st.number_input("Combustível A (R$/l)", min_value=0.0, value=5.90, step=0.1, format="%.2f", key="comb_a")
        with colA3:
            manut_a = st.number_input("Manutenção A (R$)", min_value=0.0, value=200.0, step=50.0, key="manut_a")
            seguro_a = st.number_input("Seguro anual A (R$)", min_value=0.0, value=3500.0, step=100.0, key="seguro_a")
            ipva_a = st.number_input("IPVA A (%/ano)", min_value=0.0, value=4.0, step=0.5, key="ipva_a")
            dep_a = st.number_input("Depreciação A (%/ano)", min_value=0.0, value=10.0, step=0.5, key="dep_a")

        st.markdown("---")
        st.subheader("Carro B")
        colB1, colB2, colB3 = st.columns(3)
        with colB1:
            valor_b = st.number_input("Valor do carro B (R$)", min_value=0.0, value=95000.0, step=1000.0, key="valor_b")
            km_b = st.number_input("Km/mês B", min_value=0.0, value=1000.0, step=50.0, key="km_b")
        with colB2:
            cons_b = st.number_input("Consumo B (km/l)", min_value=0.0, value=12.0, step=0.5, key="cons_b")
            comb_b = st.number_input("Combustível B (R$/l)", min_value=0.0, value=5.90, step=0.1, format="%.2f", key="comb_b")
        with colB3:
            manut_b = st.number_input("Manutenção B (R$)", min_value=0.0, value=220.0, step=50.0, key="manut_b")
            seguro_b = st.number_input("Seguro anual B (R$)", min_value=0.0, value=3600.0, step=100.0, key="seguro_b")
            ipva_b = st.number_input("IPVA B (%/ano)", min_value=0.0, value=4.0, step=0.5, key="ipva_b")
            dep_b = st.number_input("Depreciação B (%/ano)", min_value=0.0, value=10.0, step=0.5, key="dep_b")

        sub_compare = st.form_submit_button("Comparar", type="primary", use_container_width=True)

    if sub_compare:
        A = Inputs(renda_c, valor_a, km_a, cons_a, comb_a, manut_a, seguro_a, ipva_a, dep_a)
        B = Inputs(renda_c, valor_b, km_b, cons_b, comb_b, manut_b, seguro_b, ipva_b, dep_b)
        sumA = resumo(A)
        sumB = resumo(B)

        st.subheader("KPIs comparativos")
        c1, c2, c3 = st.columns(3)
        c1.metric("IAS A", f"{sumA['ias_val']:.1f}% ({sumA['ias_classe']})")
        c2.metric("IAS B", f"{sumB['ias_val']:.1f}% ({sumB['ias_classe']})")
        c3.metric("Diferença de custo/mês", f"R$ {(sumA['total']-sumB['total']):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        d1, d2, d3 = st.columns(3)
        d1.metric("Custo/mês A", f"R$ {sumA['total']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        d2.metric("Custo/mês B", f"R$ {sumB['total']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        d3.metric("Custo por km (A vs B)", f"R$ {sumA['cpk']:.2f} vs R$ {sumB['cpk']:.2f}")

        comp = pd.DataFrame({
            "Indicador": ["Custo mensal", "Custo por km", "Combustível/mês"],
            "A": [sumA["total"], sumA["cpk"], sumA["custos"]["combustivel"]],
            "B": [sumB["total"], sumB["cpk"], sumB["custos"]["combustivel"]],
        })
        comp_melt = comp.melt(id_vars="Indicador", var_name="Carro", value_name="Valor")
        fig2 = px.bar(comp_melt, x="Indicador", y="Valor", color="Carro", barmode="group", title="Comparativo A vs B")
        st.plotly_chart(fig2, use_container_width=True)

        # Recomendação automática: 1) menor IAS; 2) empate -> menor custo/mês; 3) empate -> menor custo/km
        recomend = "A"
        motivo = "menor IAS"
        if sumB["ias_val"] < sumA["ias_val"]:
            recomend, motivo = "B", "menor IAS"
        elif abs(sumA["ias_val"] - sumB["ias_val"]) < 1e-6:
            if sumB["total"] < sumA["total"]:
                recomend, motivo = "B", "menor custo mensal"
            elif abs(sumA["total"] - sumB["total"]) < 1e-6:
                if sumB["cpk"] < sumA["cpk"]:
                    recomend, motivo = "B", "menor custo por km"

        st.success(f"**Recomendação:** Carro **{recomend}** ({motivo}).")
        st.caption("Critérios: 1) IAS, 2) Custo mensal, 3) Custo por km. Ajuste parâmetros para seu uso real.")
