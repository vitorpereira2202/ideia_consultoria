# pdf_report.py
from fpdf import FPDF

def _sanitize(text: str) -> str:
    """Converte caracteres tipográficos para equivalentes ASCII/Latin-1."""
    if not isinstance(text, str):
        return str(text)
    return (
        text.replace("—", "-")
            .replace("–", "-")
            .replace("…", "...")
            .replace("“", '"').replace("”", '"')
            .replace("‘", "'").replace("’", "'")
    )

def gerar_pdf_bytes(kpis: dict, barras: dict, notas: str) -> bytes:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=12)

    # Título
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, _sanitize("AutoSmart - Relatório Financeiro do Veículo"), ln=1)

    # Intro
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 7, _sanitize("Resumo do custo mensal com IAS (Índice AutoSmart) e custo por km."))

    # KPIs
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, _sanitize("KPIs principais"), ln=1)
    pdf.set_font("Helvetica", "", 11)
    for rotulo, valor in kpis.items():
        pdf.cell(0, 7, _sanitize(f"{rotulo}: {valor}"), ln=1)

    # Barras proporcionais
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, _sanitize("Distribuição de custos mensais (R$)"), ln=1)
    pdf.set_font("Helvetica", "", 11)
    max_val = max(1, max(barras.values())) if barras else 1
    for nome, val in barras.items():
        largura = min(100, (val / max_val) * 100)
        pdf.cell(40, 6, _sanitize(nome))
        x = pdf.get_x(); y = pdf.get_y() + 1.5
        pdf.rect(x, y, 105, 4)
        pdf.set_fill_color(0, 0, 0)
        pdf.rect(x, y, largura, 4, "F")
        pdf.ln(6)

    # Recomendações
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, _sanitize("Recomendações"), ln=1)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, _sanitize(notas))

    # Retorna bytes de forma compatível com diferentes versões do fpdf2
    raw = pdf.output(dest="S")
    if isinstance(raw, (bytes, bytearray)):
        return bytes(raw)
    # em algumas versões retorna str latin-1
    return str(raw).encode("latin-1")

# teste