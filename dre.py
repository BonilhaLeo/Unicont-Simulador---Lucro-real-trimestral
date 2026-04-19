import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulador Lucro Real Trimestral", layout="wide")

# --- AJUSTE VISUAL: FONTE AMPLIADA ---
st.markdown("""
    <style>
        p, span, label, input, th, td {
            font-size: 19px !important;
        }
        h1 { font-size: 2.3rem !important; }
        h3 { font-size: 1.6rem !important; }
        h4 { font-size: 1.3rem !important; }
    </style>
""", unsafe_allow_html=True)

def formata_br(valor):
    return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')

st.title("📊 Painel Contábil - Lucro Real Trimestral")
st.markdown("Estrutura fixa de apuração com IRPJ/CSLL sobre a base de cálculo.")

# --- 1. ENTRADA DE DADOS ---
st.header("1. Lançamentos do Período")
col_v, col_c, col_d = st.columns(3)

with col_v:
    st.markdown("#### 📤 Vendas / Débitos")
    v18 = st.number_input("Vendas a 18%", min_value=0.0, value=0.0, format="%.2f")
    v12 = st.number_input("Vendas a 12%", min_value=0.0, value=3528.73, format="%.2f")
    v7 = st.number_input("Vendas a 7%", min_value=0.0, value=0.0, format="%.2f")
    v4 = st.number_input("Vendas a 4%", min_value=0.0, value=0.0, format="%.2f")
    v0 = st.number_input("Vendas a 0%", min_value=0.0, value=0.0, format="%.2f")
    v_out = st.number_input("Outros Débitos (R$)", min_value=0.0, value=0.0, format="%.2f")
    vendas_totais = v18 + v12 + v7 + v4 + v0 + v_out

with col_c:
    st.markdown("#### 📥 Compras / Créditos")
    c18 = st.number_input("Compras a 18%", min_value=0.0, value=0.0, format="%.2f")
    c12 = st.number_input("Compras a 12%", min_value=0.0, value=0.0, format="%.2f")
    c7 = st.number_input("Compras a 7%", min_value=0.0, value=0.0, format="%.2f")
    c4 = st.number_input("Compras a 4%", min_value=0.0, value=0.0, format="%.2f")
    c0 = st.number_input("Compras a 0%", min_value=0.0, value=0.0, format="%.2f")
    c_out = st.number_input("Outros Créditos (R$)", min_value=0.0, value=0.0, format="%.2f")
    compras_totais = c18 + c12 + c7 + c4 + c0 + c_out

with col_d:
    st.markdown("#### 🏢 Custos e Despesas")
    cmv = st.number_input("C.M.V", min_value=0.0, value=2008.53, format="%.2f")
    despesas = st.number_input("Despesas", min_value=0.0, value=0.0, format="%.2f")

st.divider()

# --- 2. CÁLCULOS TRIBUTÁRIOS ---
icms_v = (v18*0.18) + (v12*0.12) + (v7*0.07) + (v4*0.04)
icms_c = (c18*0.18) + (c12*0.12) + (c7*0.07) + (c4*0.04)
icms_net = icms_v - icms_c

base_pc_v = max(0, vendas_totais - icms_v)
p_deb, co_deb = base_pc_v * 0.0165, base_pc_v * 0.0760

base_pc_c = max(0, compras_totais - icms_c)
p_cred, co_cred = base_pc_c * 0.0165, base_pc_c * 0.0760

p_net = p_deb - p_cred
co_net = co_deb - co_cred

receita_liq = vendas_totais - icms_v - p_deb - co_deb
lucro_bruto = receita_liq - cmv
base_ir_cs = lucro_bruto - despesas

if base_ir_cs > 0:
    csll_9 = base_ir_cs * 0.09
    irpj_15 = base_ir_cs * 0.15
    irpj_add = max(0, base_ir_cs - 60000) * 0.10
else:
    csll_9 = irpj_15 = irpj_add = 0.0

lucro_liquido = base_ir_cs - (csll_9 + irpj_15 + irpj_add)

# --- 3. EXIBIÇÃO ---
c1, c2 = st.columns([1, 1.5])

with c1:
    st.markdown("### 🧾 Guias a Recolher")
    def box(label, valor):
        if valor < 0: st.success(f"**{label} (Crédito):** {formata_br(valor)}")
        elif valor > 0: st.error(f"**{label} (A Pagar):** {formata_br(valor)}")
        else: st.write(f"**{label}:** R$ 0,00")

    box("ICMS", icms_net)
    box("PIS", p_net)
    box("COFINS", co_net)
    box("IRPJ (15% + 10%)", irpj_15 + irpj_add)
    box("CSLL (9%)", csll_9)

with c2:
    st.markdown("### 📊 DRE")
    dre_map = {
        "Descrição": [
            "RECEITA BRUTA", "(-) ICMS", "(-) PIS", "(-) COFINS", "RECEITA LÍQUIDA",
            "(-) C.M.V", "LUCRO BRUTO", "(-) DESPESAS", "BASE PARA O IRPJ E A CSLL",
            "(-) 9% CSLL", "(-) 15% IRPJ", "(-) 10% Adicional IRPJ", "LUCRO LÍQUIDO"
        ],
        "Valor": [
            formata_br(vendas_totais), formata_br(-icms_v), formata_br(-p_deb), formata_br(-co_deb), formata_br(receita_liq),
            formata_br(-cmv), formata_br(lucro_bruto), formata_br(-despesas), formata_br(base_ir_cs),
            formata_br(-csll_9), formata_br(-irpj_15), formata_br(-irpj_add), formata_br(lucro_liquido)
        ]
    }
    st.dataframe(pd.DataFrame(dre_map), use_container_width=True, hide_index=True)
