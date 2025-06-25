import streamlit as st
import pandas as pd
import os

# Import all logic modules
from code_one import run as run_arb_object
from code_two import run_new_bio_object
from code_three import run as run_old_bio_object

def run_object_creation():
    st.header("🧱 Object File Creation")
    
    uploaded_file = st.file_uploader("📂 Upload Excel file", type=["xlsx"])

# Path to your reference file (adjust path if needed)
    ref_file_path = "OBJECT_FILES.xlsx"  # Or full path like "reference/CF_REF_FILE.xlsx"

# Check if reference file exists and show download button
    if os.path.exists(ref_file_path):
        with open(ref_file_path, "rb") as ref_file:
          st.download_button(
                label="📄 Download CF_REF_FILE",
                data=ref_file,
                file_name="CF_REF_FILE.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ CF_REF_FILE not found. Please ensure it is placed correctly.")

    file_type = st.selectbox("Select object file type:", ["ARBIN", "NEW BIOLOGIC", "OLD BIOLOGIC"])  # , "OLD BIOLOGIC"])


    if uploaded_file:
        # Sheet mapping per logic
        sheet_mapping = {
            "ARBIN": "ARBIN",
            "NEW BIOLOGIC": "NB",
            "OLD BIOLOGIC": "OB",  # if needed
        }

        try:
            sheet_name = sheet_mapping[file_type]
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=None)
            st.subheader("🔍 Preview of Uploaded Data")
            st.dataframe(df.head())

            if st.button("Run and Generate Files"):
                if file_type == "ARBIN":
                    zip_data, zip_name = run_arb_object(df, component_name="cathode")
                elif file_type == "NEW BIOLOGIC":
                    zip_data, zip_name = run_new_bio_object(df)
                elif file_type == "OLD BIOLOGIC":
                    zip_data, zip_name = run_old_bio_object(df)

                st.success("✅ Files generated!")
                st.download_button(
                    label="📥 Download Generated Files",
                    data=zip_data,
                    file_name=zip_name,
                    mime="application/zip"
                )

        except Exception as e:
            st.error(f"❌ Error processing file: {e}")
