import streamlit as st
import os
import math
import altair as alt
from io import StringIO
from datetime import date

# ── Page Config & CSS ─────────────────────────────────────────────────────────
st.set_page_config(layout="wide", page_title="SMART CVD Risk Reduction")
st.markdown('''
<style>
.header { position: sticky; top: 0; background: #f7f7f7; padding: 10px; display: flex; justify-content: space-between; align-items: center; z-index:100; }
.card { background: #fff; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.sidebar .stExpanderHeader { font-weight: bold; }
button { font-size: 16px; }
</style>
''', unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="header">', unsafe_allow_html=True)
st.image('logo.png', width=120)  # small top-right logo
if st.button('Reset', key='reset_button'):
    for k in st.session_state.keys():
        del st.session_state[k]
st.button('Calculate Risk', key='calculate_button')
st.markdown('</div>', unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    with st.expander('Demographics', expanded=True):
        age = st.slider('Age', 30, 90, 60, key='age')
        sex = st.selectbox('Sex', ['Male','Female'], key='sex')
    with st.expander('Clinical History'):
        smoker = st.checkbox('Current smoker', key='smoker')
        diabetes = st.checkbox('Diabetes', key='diabetes')
        vascular = st.multiselect('Known vascular disease', ['Coronary','Cerebrovascular','Peripheral'], key='vascular')
    with st.expander('Vitals'):
        egfr = st.slider('eGFR (mL/min/1.73m²)', 15, 120, 90, key='egfr')
        sbp = st.slider('Systolic BP (mmHg)', 80, 220, 140, key='sbp')
        weight = st.number_input('Weight (kg)', 40.0,200.0,75.0, key='weight')
        height = st.number_input('Height (cm)',140.0,210.0,170.0,key='height')
        bmi = weight/((height/100)**2)
        st.markdown(f'**BMI:** {bmi:.1f} kg/m²')

# Only calculate when button clicked
if st.session_state.get('calculate_button'):
    # ── Main Content Tabs ─────────────────────────────────────────────────────
    tabs = st.tabs(['Laboratory','Therapies','Results'])
    
    # --- Laboratory Tab ---
    with tabs[0]:
        st.header('Laboratory Results')
        total_chol = st.number_input('Total Cholesterol',2.0,10.0,5.2,0.1,key='tc')
        hdl = st.number_input('HDL-C',0.5,3.0,1.3,0.1,key='hdl')
        ldl = st.number_input('LDL-C',0.5,6.0,3.0,0.1,key='ldl')
        crp = st.number_input('hs-CRP',0.1,20.0,2.5,0.1,key='crp')
        hba1c = st.number_input('HbA1c',4.0,14.0,7.0,0.1,key='hba1c')
        tg = st.number_input('Triglycerides',0.3,5.0,1.2,0.1,key='tg')
    
    # --- Therapies Tab ---
    with tabs[1]:
        st.header('Therapy Selection')
        df = []
        drugs = ['Simvastatin','Atorvastatin','Rosuvastatin','Ezetimibe','Bempedoic acid']
        intensities = ['Pre-admission','New/Intensified']
        cols = st.columns([2,1,1])
        cols[0].write('Drug')
        cols[1].write('Pre-admission')
        cols[2].write('New/Intensified')
        selections = {}
        for drug in drugs:
            row = st.columns([2,1,1])
            row[0].write(drug)
            pre = row[1].checkbox('', key=f'pre_{drug}')
            new = row[2].checkbox('', key=f'new_{drug}')
            selections[drug] = (pre,new)
        # Calculate projected LDL
        post_ldl = total_chol*0
        base_ldl = ldl
        reduct = {'Simvastatin':0.45,'Atorvastatin':0.5,'Rosuvastatin':0.55,'Ezetimibe':0.2,'Bempedoic acid':0.18}
        for drug,(pre,new) in selections.items():
            if pre or new:
                post_ldl = base_ldl*(1 - reduct.get(drug,0))
                base_ldl = post_ldl
        drop = ldl - post_ldl
        st.success(f'Projected LDL-C: {post_ldl:.1f} mmol/L (↓ {drop:.1f})')

    # --- Results Tab ---
    with tabs[2]:
        st.header('Results & Summary')
        # risk calculation
        vasc = len(st.session_state['vascular'])
        def est10(...): pass  # insert your risk funcs
        # Mock results
        r5,r10,rl = 10.2,20.5,50.3
        data = pd.DataFrame({'Risk':[r5,r10,rl]},index=['5yr','10yr','Lifetime'])
        chart = alt.Chart(data.reset_index()).mark_line(point=True).encode(x='index',y='Risk').properties(width=600)
        st.altair_chart(chart)
        st.download_button('Download CSV',pd.DataFrame({'Metric':['5yr','10yr','Lifetime'],'Value':[r5,r10,rl]}).to_csv(),file_name='risk.csv')

    # Persistent footer
    st.markdown('---')
    st.markdown(f'**Last updated:** {date.today().strftime('%d/%m/%Y')}')
    st.markdown('For informational purposes only.')
""
