def run_BEIS():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import json
    import matplotlib.pyplot as plt
    from io import BytesIO
    from impedance.models.circuits import CustomCircuit
    from impedance.visualization import plot_nyquist

    st.title("Biologic BTExport EIS Analyzer")
    st.text ("This will fit your Biologic JSON/CSV data files. Use the EIS Fit Parameters to properly adjust the fit.")

    # Upload JSON and CSV files
    json_files = st.file_uploader("Upload JSON files", type="json", accept_multiple_files=True)
    csv_files = st.file_uploader("Upload CSV files", type="csv", accept_multiple_files=True)

    if json_files and csv_files:
        if len(json_files) != len(csv_files):
            st.error("Please upload an equal number of .json and .csv files.")
        else:
            # Parse metadata from JSON files
            mass = []
            cell_name = []
            battery_tester = []

            for json_file in json_files:
                data_json = json.load(json_file)
                mass.append(float(data_json["dutType"]["nominal capacity"][:-4]) / 250)
                cell_name.append(data_json["dutType"]["name"])
                battery_tester.append(data_json["dut_run"]["hardwareType"])

            # Process CSV files and extract cycle data
            df_cycle_data = {}
            first_charge = []
            first_discharge = []

            for i, csv_file in enumerate(csv_files):
                df = pd.read_csv(csv_file, sep=";")
                df["Q charge / C"] *= (1000 / (3600 * mass[i]))
                df["Q discharge / C"] *= (1000 / (3600 * mass[i]))
                df_cycle_data[i] = df

                charge_data = df[df["Step number"] == 2]
                discharge_data = df[df["Step number"] == 6]

                first_charge.append(charge_data["Q charge / C"].iloc[-1])
                first_discharge.append(discharge_data["Q discharge / C"].iloc[-1])

            first_ce = np.array(first_discharge) * 100 / np.array(first_charge)

            # Sidebar for frequency inputs
            st.sidebar.header("⚙️ EIS Frequency Settings")
            default_f_ini = 75.0
            default_f_final = 2.0
            f_ini = st.sidebar.number_input("Initial frequency (Hz)", min_value=0.1, value=default_f_ini, step=1.0)
            f_final = st.sidebar.number_input("Final frequency (Hz)", min_value=0.01, value=default_f_final, step=0.5)

            rerun_eis = st.sidebar.button("🔁 Rerun EIS Analysis")

            # Only recompute if rerun or not yet in session state
            if "eis_results" not in st.session_state or rerun_eis:
                rct = []
                z_re = []
                z_fit = {}

                st.header("📈 EIS Nyquist Plots")

                for i in range(len(csv_files)):
                    st.subheader(f"Sample {i+1}: {cell_name[i]}")
                    df = df_cycle_data[i]

                    # EIS Fitting
                    eis_data = df[(df["Step number"] == 4) &
                                (df["Frequency / Hz"] > f_final) &
                                (df["Frequency / Hz"] < f_ini)]

                    z = eis_data["Re(Z) / Ω"].values + 1j * -1 * eis_data["-Im(Z) / Ω"].values
                    circuit = CustomCircuit("R0-p(R1,CPE1)", initial_guess=[0.01, .01, 100, 1])
                    circuit.fit(eis_data["Frequency / Hz"].values, z)
                    z_fit[i] = circuit.predict(eis_data["Frequency / Hz"].values)

                    rct.append(circuit.parameters_[1])
                    idx_01hz = (df["Frequency / Hz"] - 0.1).abs().idxmin()
                    z_re.append(df.at[idx_01hz, "Re(Z) / Ω"])

                    fig, ax = plt.subplots()
                    plot_nyquist(z, fmt='o', ax=ax)
                    plot_nyquist(z_fit[i], fmt='-', ax=ax)
                    ax.set_title("Nyquist Plot")
                    ax.legend(["Data", "Fit"])
                    st.pyplot(fig)

                # Store results in session state
                st.session_state.eis_results = {
                    "rct": rct,
                    "z_re": z_re
                }

            # Summary display
            rct = st.session_state.eis_results["rct"]
            z_re = st.session_state.eis_results["z_re"]

            final_data = pd.DataFrame({
                "Cell Name": cell_name,
                "Mass (g)": mass,
                "1st Discharge (mAh/g)": first_discharge,
                "1st Charge (mAh/g)": first_charge,
                "1st CE (%)": first_ce,
                "Hardware": battery_tester,
                "Zre @ 0.1 Hz (Ω)": z_re,
                "Rct (Ω)": rct
            })

            st.header("📊 Summary Table")
            st.dataframe(final_data)

            # Excel download
            output = BytesIO()
            final_data.to_excel(output, index=False)
            st.download_button(
                label="📥 Download Summary Excel",
                data=output.getvalue(),
                file_name="Data_First_Cycle.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("Please upload both JSON and CSV files to begin.")
