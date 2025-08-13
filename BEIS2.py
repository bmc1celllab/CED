import json
import re
from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from impedance.models.circuits import CustomCircuit
from impedance.visualization import plot_nyquist
from matplotlib.ticker import MultipleLocator


def extract_test_name_group(test_name):
    if pd.isna(test_name):
        return test_name

    # Case 1: Handle underscore then number (NCM90_PR_686_2 -> NCM90_PR_686)
    match1 = re.match(r"^(.+)_\d+$", test_name)
    if match1:
        return match1.group(1)

    # Case 2: Handle dash then number (CAM1-ST013399-2 -> CAM1-ST013399)
    match2 = re.match(r"^(.+)-\d+$", test_name)
    if match2:
        return match2.group(1)

    # Case 3: For everything else, use the original test name as the group
    return test_name


def add_test_name_group(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add test_name_group column based on test_name patterns.
    """
    df_copy = df.copy()
    test_name_group_values = df_copy["test_name"].apply(extract_test_name_group)
    df_copy.insert(0, "test_name_group", test_name_group_values)
    return df_copy


def dataframe_to_clipboard_string(df):
    """Convert DataFrame to tab-separated string suitable for clipboard copying"""
    return df.to_csv(sep="\t", index=False)


def run_BEIS():
    st.title("Biologic BTExport EIS Analyzer")
    st.text(
        "This will fit your Biologic JSON/CSV data files. Use the EIS Fit Parameters to properly adjust the fit."
    )

    def set_axes(ax, x_min=None, x_max=None, y_min=None, y_max=None):
        if (
            x_min is not None
            and x_max is not None
            and y_min is not None
            and y_max is not None
        ):
            ax.set_xlim([x_min, x_max])
            ax.set_ylim([y_min, y_max])
        else:
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            x_min = 0
            x_max = xlim[1]
            x_range = x_max - x_min
            y_range = ylim[1] - ylim[0]
            max_range = max(x_range, y_range)
            x_max = x_min + max_range
            y_center = (ylim[1] + ylim[0]) / 2
            y_min = y_center - max_range / 2
            y_max = y_center + max_range / 2
            ax.set_xlim([x_min, x_max])
            ax.set_ylim([y_min, y_max])
        ax.set_aspect("equal")

    # Add checkbox and inputs to sidebar
    st.sidebar.header("📐 Axis Settings")
    custom_axes = st.sidebar.checkbox("Manually Set Axes Limits?")
    x_min_val, x_max_val, y_min_val, y_max_val = None, None, None, None

    if custom_axes:
        x_min_val = st.sidebar.number_input("x_min", value=0.0, key="x_min_input")
        x_max_val = st.sidebar.number_input("x_max", value=10.0, key="x_max_input")
        y_min_val = st.sidebar.number_input("y_min", value=-5.0, key="y_min_input")
        y_max_val = st.sidebar.number_input("y_max", value=5.0, key="y_max_input")

    rerun_plots = st.sidebar.button("🔁 Rerun EIS Plot")

    # Upload JSON and CSV files
    json_files = st.file_uploader(
        "Upload JSON files", type="json", accept_multiple_files=True
    )
    csv_files = st.file_uploader(
        "Upload CSV files", type="csv", accept_multiple_files=True
    )

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
                cell_name.append(
                    str(
                        data_json.get("dutType", {}).get("name")
                        or data_json.get("dutType", {}).get("electrode material", "")
                    )
                )
                battery_tester.append(data_json["dut_run"]["hardwareType"])

            # Process CSV files and extract cycle data
            df_cycle_data = {}
            first_charge = []
            first_discharge = []

            for i, csv_file in enumerate(csv_files):
                df = pd.read_csv(csv_file, sep=";")
                df["Q charge / C"] *= 1000 / (3600 * mass[i])
                df["Q discharge / C"] *= 1000 / (3600 * mass[i])
                df_cycle_data[i] = df

                charge_data = df[df["Step number"] == 2]
                discharge_data = df[df["Step number"] == 6]

                first_charge.append(charge_data["Q charge / C"].iloc[-1])
                first_discharge.append(discharge_data["Q discharge / C"].iloc[-1])

            first_ce = np.array(first_discharge) * 100 / np.array(first_charge)

            # Sidebar for frequency inputs
            st.sidebar.header("⚙️ EIS Frequency Settings")
            default_f_ini = 50.0
            default_f_final = 2.0
            f_ini = st.sidebar.number_input(
                "Initial frequency (Hz)", min_value=0.1, value=default_f_ini, step=1.0
            )
            f_final = st.sidebar.number_input(
                "Final frequency (Hz)", min_value=0.01, value=default_f_final, step=0.5
            )

            rerun_eis = st.sidebar.button("🔁 Rerun EIS Analysis")

            # Only recompute if rerun or not yet in session state
            if "eis_results" not in st.session_state or rerun_eis or rerun_plots:
                rct = []
                z_re = []
                z_fit = {}
                all_full_raw_nyquist = []

                st.header("📈 EIS Nyquist Plots")

                for i in range(len(csv_files)):
                    # Store raw full Nyquist data
                    st.subheader(f"Sample {i+1}: {cell_name[i]}")
                    df = df_cycle_data[i]

                    # Full EIS data (raw) for plotting
                    full_eis_data = df[df["Step number"] == 4]
                    # Store raw full Nyquist data
                    all_full_raw_nyquist.append(
                        {
                            "label": f"Sample {i+1}: {cell_name[i]}",
                            "Re": full_eis_data["Re(Z) / Ω"].values,
                            "Im": full_eis_data["-Im(Z) / Ω"].values,
                        }
                    )

                    # EIS data for fitting (filtered by frequency range)
                    eis_data = full_eis_data[
                        (full_eis_data["Frequency / Hz"] > f_final)
                        & (full_eis_data["Frequency / Hz"] < f_ini)
                    ]

                    if eis_data.empty or full_eis_data.empty:
                        st.warning(f"Insufficient EIS data for Sample {i+1}.")
                        continue

                    try:
                        # For fitting
                        re_z = eis_data["Re(Z) / Ω"].values
                        im_z = eis_data["-Im(Z) / Ω"].values
                        freq = eis_data["Frequency / Hz"].values
                        z = re_z + 1j * -1 * im_z

                        # For full plot
                        full_re_z = full_eis_data["Re(Z) / Ω"].values
                        full_im_z = full_eis_data["-Im(Z) / Ω"].values

                        # Fit circuit
                        circuit = CustomCircuit(
                            "R0-p(R1,CPE1)", initial_guess=[0.01, 0.01, 100, 1]
                        )
                        circuit.fit(freq, z)
                        z_fit[i] = circuit.predict(freq)

                        rct.append(circuit.parameters_[1])
                        idx_01hz = (df["Frequency / Hz"] - 0.1).abs().idxmin()
                        z_re.append(df.at[idx_01hz, "Re(Z) / Ω"])

                        # Plot 1: Fit
                        fig1, ax1 = plt.subplots()
                        plot_nyquist(z, fmt="o", ax=ax1)
                        plot_nyquist(z_fit[i], fmt="-", ax=ax1)
                        ax1.set_title("Nyquist Plot (Fit)")
                        ax1.legend(["Data", "Fit"])
                        st.pyplot(fig1)

                        # Plot 2: Full Raw Nyquist
                        fig2, ax2 = plt.subplots()
                        ax2.plot(full_re_z, full_im_z, "-o", markersize=4)
                        set_axes(ax2, x_min_val, x_max_val, y_min_val, y_max_val)
                        ax2.xaxis.set_major_locator(MultipleLocator(1))
                        ax2.yaxis.set_major_locator(MultipleLocator(1))
                        ax2.set_xlabel("Re(Z) / Ω")
                        ax2.set_ylabel("-Im(Z) / Ω")
                        # ax2.set_title("Full Raw Nyquist Plot (Step 4 Data)")
                        # ax2.set_title("Nyquist Plot")
                        ax2.set_title(f"Sample {i+1}: {cell_name[i]}")
                        ax2.grid(True)
                        st.pyplot(fig2)

                    except KeyError as e:
                        st.error(f"Missing column in data: {e}")
                    except Exception as e:
                        st.error(f"Error processing Sample {i+1}: {e}")

                fig_all, ax_all = plt.subplots()
                for entry in all_full_raw_nyquist:
                    ax_all.plot(
                        entry["Re"],
                        entry["Im"],
                        "-o",
                        markersize=4,
                        label=entry["label"],
                    )
                set_axes(ax_all, x_min_val, x_max_val, y_min_val, y_max_val)
                ax_all.set_xlabel("Re(Z) / Ω")
                ax_all.set_ylabel("-Im(Z) / Ω")
                ax_all.set_title("Nyquist Plot")
                ax_all.grid(True)
                ax_all.legend()
                st.pyplot(fig_all)

                # Store results in session state
                st.session_state.eis_results = {"rct": rct, "z_re": z_re}

            #### SUMMARY DISPLAY ####
            z_re = st.session_state.eis_results["z_re"]
            rct = st.session_state.eis_results["rct"]

            final_data = pd.DataFrame(
                {
                    "Cell Name": cell_name,
                    "Mass (g)": mass,
                    "1st Discharge (mAh/g)": first_discharge,
                    "1st Charge (mAh/g)": first_charge,
                    "1st CE (%)": first_ce,
                    "Hardware": battery_tester,
                    "Zre @ 0.1 Hz (Ω)": z_re,
                    "Rct (Ω)": rct,
                }
            )
            st.header("📊 Summary Table")
            st.dataframe(final_data)

            # Download button for summary table
            output = BytesIO()
            final_data.to_excel(output, index=False)
            st.download_button(
                label="📥 Download Summary Excel",
                data=output.getvalue(),
                file_name="Data_First_Cycle.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

            #### BASEROW DISPLAY ####
            current_time = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            final_data_baserow = pd.DataFrame(
                {
                    "sample_name": "",  # left as blank, to be filled in by user
                    "test_name": cell_name,
                    "validated": True,
                    "is_outlier": False,
                    "first_discharge_capacity_mah_g": first_discharge,
                    "first_charge_capacity_mah_g": first_charge,
                    "first_coulombic_efficiency_per": first_ce,
                    "impedance_ohm": z_re,
                    "cathode_fit": rct,
                    "date_time": current_time,
                }
            )

            # Round the numeric values to 2 decimal places
            final_data_baserow = final_data_baserow.round(3)
            final_data_baserow = add_test_name_group(final_data_baserow.copy())

            st.header("📋 Summary Data for Baserow")
            st.dataframe(final_data_baserow)

            # Download button for baserow table as CSV
            csv_data = final_data_baserow.to_csv(index=False)
            st.download_button(
                label="📥 Download Baserow CSV",
                data=csv_data,
                file_name=f"Baserow_Data_{current_time}.csv",
                mime="text/csv",
            )

            st.markdown(
                "This data can be uploaded to Baserow by downloading it as a CSV, then importing in the Baserow UI.\n See screenshots below."
            )
            st.image(
                "baserow_import_file_button.png",
                caption="Step 1: Click 'Import File'",
                width=400,
            )
            st.image(
                "baserow_upload_csv.png",
                caption="Step 2: Hit 'Import as CSV', then hit 'Choose CSV File', then hit 'Import' button in blue. Default settings are correct.",
                width=600,
            )

    else:
        st.info("Please upload both JSON and CSV files to begin.")


if __name__ == "__main__":
    run_BEIS()
