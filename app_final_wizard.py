import streamlit as st
import os
import math
from io import StringIO

# ── Page Configuration & CSS ─────────────────────────────────────────────────
st.set_page_config(layout="wide", page_title="SMART CVD Risk Reduction")
st.markdown("""<style>
/* Sticky header logo container */
.header {
  position: sticky; top: 0; background: #f7f7f7; padding: 10px;
  display: flex; justify-content: flex-end; z-index: 100;
}
/* Card styling */
.card {
  background: #fff; padding: 20px; margin-bottom: 20px;
  border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
/* Full-page watermark behind main content */
.block-container {
  background-image: url('logo.png');
  background-repeat: no-repeat;
  background-position: center center;
  background-size: 200px 200px;
  opacity: 0.1;
}
</style>""", unsafe_allow_html=True)

# ── Header with Logo ──────────────────────────────────────────────────────────
st.markdown('<div class="header">', unsafe_allow_html=True)
if os.path.exists("logo.png"):
    st.image("logo.png", width=150)
else:
    st.warning("⚠️ Please upload 'logo.png' alongside this script.")
st.markdown('</div>', unsafe_allow_html=True)

# ── Sidebar: Demographics & Risk Factors ───────────────────────────────────────
st.sidebar.header("Patient Demographics")
age = st.sidebar.slider("Age (years)", 30, 90, 60, key="age")
sex = st.sidebar.radio("Sex", ["Male", "Female"], key="sex")
weight = st.sidebar.number_input("Weight (kg)", 40.0, 200.0, 75.0, key="weight")
height = st.sidebar.number_input("Height (cm)", 140.0, 210.0, 170.0, key="height")
bmi = weight / ((height / 100) ** 2)
st.sidebar.markdown(f"**BMI:** {bmi:.1f} kg/m²")

st.sidebar.header("Risk Factors")
smoker = st.sidebar.checkbox("Current smoker", key="smoker")
diabetes = st.sidebar.checkbox("Diabetes", key="diabetes")
st.sidebar.markdown("**Known vascular disease in the following territories:**")
vasc_cor = st.sidebar.checkbox("Coronary artery disease", key="vasc_cor")
vasc_cer = st.sidebar.checkbox("Cerebrovascular disease", key="vasc_cer")
vasc_per = st.sidebar.checkbox("Peripheral artery disease", key="vasc_per")
vasc_count = sum([vasc_cor, vasc_cer, vasc_per])
egfr = st.sidebar.slider("eGFR (mL/min/1.73 m²)", 15, 120, 90, key="egfr")

# ── Risk Calculation Functions ─────────────────────────────────────────────────
def estimate_10y_risk(age, sex, sbp, tc, hdl, smoker, diabetes, egfr, crp, vasc):
    sv = 1 if sex == "Male" else 0
    sm = 1 if smoker else 0
    dm = 1 if diabetes else 0
    crp_l = math.log(crp + 1)
    lp = (0.064 * age + 0.34 * sv + 0.02 * sbp + 0.25 * tc
          - 0.25 * hdl + 0.44 * sm + 0.51 * dm
          - 0.2 * (egfr / 10) + 0.25 * crp_l + 0.4 * vasc)
    raw = 1 - 0.900 ** math.exp(lp - 5.8)
    return min(raw * 100, 95.0)

def convert_5yr(r10):
    p = min(r10, 95.0) / 100
    return min((1 - (1 - p) ** 0.5) * 100, 95.0)

def estimate_lifetime_risk(age, r10):
    years = max(85 - age, 0)
    p10 = min(r10, 95.0) / 100
    annual = 1 - (1 - p10) ** (1 / 10)
    return min((1 - (1 - annual) ** years) * 100, 95.0)

def fmt(x):
    return f"{x:.1f}%"

# ── Laboratory Results ─────────────────────────────────────────────────────────
with st.expander("1 – Laboratory Results", expanded=True):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    total_chol = st.number_input("Total Cholesterol (mmol/L)", 2.0, 10.0, 5.2, 0.1, key="lab_tc")
    hdl        = st.number_input("HDL‑C (mmol/L)", 0.5, 3.0, 1.3, 0.1, key="lab_hdl")
    ldl        = st.number_input("LDL‑C (mmol/L)", 0.5, 6.0, 3.0, 0.1, key="lab_ldl")
    crp        = st.number_input("hs‑CRP (mg/L)", 0.1, 20.0, 2.5, 0.1, key="lab_crp")
    hba1c      = st.number_input("HbA₁c (%)", 4.0, 14.0, 7.0, 0.1, key="lab_hba1c")
    tg         = st.number_input("Triglycerides (mmol/L)", 0.3, 5.0, 1.2, 0.1, key="lab_tg")
    sbp        = st.number_input("Current SBP (mmHg)", 80, 220, 140, key="lab_sbp")
    st.markdown('</div>', unsafe_allow_html=True)

# ── Therapies ─────────────────────────────────────────────────────────────────
with st.expander("2 – Therapies", expanded=True):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Pre‑admission Lipid‑Lowering Therapy")
    pre_simv_low   = st.checkbox("Simvastatin 20 mg", key="pre_simv_low", help="~30% LDL‑C↓")
    pre_simv_high  = st.checkbox("Simvastatin 40 mg", key="pre_simv_high", help="~35% LDL‑C↓")
    pre_atorv_low  = st.checkbox("Atorvastatin 20 mg", key="pre_atorv_low", help="~45% LDL‑C↓")
    pre_atorv_high = st.checkbox("Atorvastatin 40 mg", key="pre_atorv_high", help="~50% LDL‑C↓")
    pre_rosu_low   = st.checkbox("Rosuvastatin 10 mg", key="pre_rosu_low", help="~45% LDL‑C↓")
    pre_rosu_high  = st.checkbox("Rosuvastatin 20 mg", key="pre_rosu_high", help="~55% LDL‑C↓")
    pre_ez         = st.checkbox("Ezetimibe 10 mg",    key="pre_ez", help="IMPROVE‑IT trial")
    pre_bemp       = st.checkbox("Bempedoic acid",     key="pre_bemp", help="CLEAR Outcomes trial")
    st.markdown("---")
    st.subheader("Initiate/Intensify Lipid‑Lowering Therapy")
    new_simv_low   = st.checkbox("Start Simvastatin 20 mg", key="new_simv_low")
    new_simv_high  = st.checkbox("Start Simvastatin 40 mg", key="new_simv_high")
    new_atorv_low  = st.checkbox("Start Atorvastatin 20 mg", key="new_atorv_low")
    new_atorv_high = st.checkbox("Start Atorvastatin 40 mg", key="new_atorv_high")
    new_rosu_low   = st.checkbox("Start Rosuvastatin 10 mg", key="new_rosu_low")
    new_rosu_high  = st.checkbox("Start Rosuvastatin 20 mg", key="new_rosu_high")
    new_ez         = st.checkbox("Add Ezetimibe 10 mg",    key="new_ez")
    new_bemp       = st.checkbox("Add Bempedoic acid",     key="new_bemp")

    # Calculate anticipated LDL‑C drop
    post_ldl = ldl
    reductions = {
        "Simvastatin 20 mg":0.30, "Simvastatin 40 mg":0.35,
        "Atorvastatin 20 mg":0.45, "Atorvastatin 40 mg":0.50,
        "Rosuvastatin 10 mg":0.45, "Rosuvastatin 20 mg":0.55,
        "Ezetimibe 10 mg":0.20,   "Bempedoic acid":0.18
    }
    for drug, key in [
        ("Simvastatin 20 mg","pre_simv_low"), ("Simvastatin 20 mg","new_simv_low"),
        ("Simvastatin 40 mg","pre_simv_high"),("Simvastatin 40 mg","new_simv_high"),
        ("Atorvastatin 20 mg","pre_atorv_low"),("Atorvastatin 20 mg","new_atorv_low"),
        ("Atorvastatin 40 mg","pre_atorv_high"),("Atorvastatin 40 mg","new_atorv_high"),
        ("Rosuvastatin 10 mg","pre_rosu_low"),  ("Rosuvastatin 10 mg","new_rosu_low"),
        ("Rosuvastatin 20 mg","pre_rosu_high"), ("Rosuvastatin 20 mg","new_rosu_high")
    ]:
        if st.session_state.get(key):
            post_ldl *= (1 - reductions[drug])
    if st.session_state["pre_ez"] or st.session_state["new_ez"]:
        post_ldl *= (1 - reductions["Ezetimibe 10 mg"])
    if st.session_state["pre_bemp"] or st.session_state["new_bemp"]:
        post_ldl *= (1 - reductions["Bempedoic acid"])
    post_ldl = max(post_ldl, 0.5)

    # Highlight the projected LDL‑C and drop
    drop = ldl - post_ldl
    st.markdown(f"**Projected LDL‑C:** {post_ldl:.1f} mmol/L  (↓ {drop:.1f} mmol/L)", unsafe_allow_html=True)

    # Gate advanced therapies
    pcsk9 = st.checkbox("PCSK9 inhibitor", key="pcsk9", disabled=(post_ldl <= 1.8), help="FOURIER trial")
    inclis = st.checkbox("Inclisiran", key="inclis", disabled=(post_ldl <= 1.8), help="ORION‑10 trial")
    st.markdown('</div>', unsafe_allow_html=True)

# ── Results & Recommendations ─────────────────────────────────────────────────
with st.expander("3 – Results & Recommendations"):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    vasc = vasc_count
    r10 = estimate_10y_risk(age, sex, sbp, total_chol, hdl, smoker, diabetes, egfr, crp, vasc)
    r5 = convert_5yr(r10)
    lt = estimate_lifetime_risk(age, r10) if age < 85 else None
    st.subheader("Risk Estimates")
    if lt is not None:
        st.write(f"5‑year: **{fmt(r5)}**, 10‑year: **{fmt(r10)}**, Lifetime: **{fmt(lt)}**")
    else:
        st.write(f"5‑year: **{fmt(r5)}**, 10‑year: **{fmt(r10)}**, Lifetime: **N/A**")
    chart_data = {"5‑year": r5, "10‑year": r10}
    if lt is not None: chart_data["Lifetime"] = lt
    st.bar_chart(chart_data)
    if lt is not None:
        arr = r10 - lt
        rrr = arr / r10 * 100 if r10 else 0
        nnt = 100 / arr if arr else None
        st.write(f"ARR: {arr:.1f} pp, RRR: {rrr:.1f}%, NNT: {nnt:.0f}")
    else:
        st.write("ARR/RRR/NNT not applicable for age ≥ 85")
    csv = StringIO()
    csv.write("Metric,Value
")
    csv.write(f"5yr,{r5:.1f}
10yr,{r10:.1f}
")
    if lt is not None: csv.write(f"Lifetime,{lt:.1f}
")
    st.download_button("Download Results (CSV)", csv.getvalue(), "cvd_results.csv", "text/csv")
    st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("Created by Samuel Panday — 21/04/2025")
st.markdown("PRIME team, King's College Hospital")
st.markdown("For informational purposes; not a substitute for medical advice.")
