import streamlit as st
from bd_2_test import run_data_analysis
from cell_files import run_object_creation
from FC_MATCH_V3 import run_fc_match
from BEIS import run_BEIS
from CD_1 import run_CD_any_cycle
from PCimp import run_PCimp
from ici import run_ici

st.set_page_config(page_title="Cell Engineering Website", layout="wide")
st.title("🔋 Redwood Materials Cell Engineering")

mode = st.sidebar.radio("Select Mode:", ["📊 Data Analysis", "🔥 FC MATCHING", "🧱 Object File Creation", "🧠 Biologic EIS", "🦦 Single Cycle C/D", "🦘 Pouch Cell EIS", "💯 ICI Analysis"])

if mode == "📊 Data Analysis":
    run_data_analysis()
elif mode == "🔥 FC MATCHING":
    run_fc_match()
elif mode == "🧱 Object File Creation":
    run_object_creation()
elif mode == "🧠 Biologic EIS":
    run_BEIS()
elif mode == "🦦 Single Cycle C/D":
    run_CD_any_cycle()
elif mode == "🦘 Pouch Cell EIS":
    run_PCimp()
elif mode == "💯 ICI Analysis":
    run_ici()