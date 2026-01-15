def run_PCimp ():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from impedance.models.circuits import CustomCircuit
    from impedance.visualization import plot_nyquist
    from io import StringIO
    import io
    import os

    st.title("🦘 Pouch Cell EIS")

    # ---------- Utility Function ----------
    def set_equal_axes(ax, x_data, y_data, fixed_max=None, buffer_ratio=0.05):
        x_min, x_max = x_data.min(), x_data.max()
        y_min, y_max = y_data.min(), y_data.max()

        x_range = x_max - x_min
        y_range = y_max - y_min
        max_range = max(x_range, y_range)

        # Use fixed max if provided
        if fixed_max is not None:
            max_limit = fixed_max
        else:
            max_limit = max(x_max, -y_min, y_max, -x_min)  # include negatives for symmetry

        # Add buffer
        max_limit *= (1 + buffer_ratio)

        # Set symmetrical limits
        ax.set_xlim(0, max_limit)
        ax.set_ylim(0, max_limit)
        ax.set_aspect('equal')

    # ---------- Upload Section ----------
    uploaded_files = st.file_uploader(
        "Upload one or more Excel files", type=["xlsx"], accept_multiple_files=True
    )

    all_data = []
    impedance_data = {}

    tab1, tab2, tab3 = st.tabs(["EIS Fitting", "Individual File Plots", "Combined File Plots"])

    with tab1:
        st.header("EIS Fitting")
        # Sidebar: frequency filter
        st.sidebar.header("Frequency Range Filter")
        f_min = st.sidebar.number_input("Minimum Frequency (Hz)", value=3.5)
        f_max = st.sidebar.number_input("Maximum Frequency (Hz)", value=20.0)


        st.sidebar.header("Initial Guess Parameters")
        r0_guess = st.sidebar.number_input("Initial guess for R0 (Ohm)", value=0.1, key="r0_guess")
        r1_guess = st.sidebar.number_input("Initial guess for R1 (Ohm)", value=0.1, key="r1_guess")
        q1_guess = st.sidebar.number_input("Initial guess for Q1 (CPE-T)", value=100.0, key="q1_guess")
        alpha1_guess = st.sidebar.number_input("Initial guess for alpha1", value=0.9, key="alpha1_guess")
        initial_guess = [r0_guess, r1_guess, q1_guess, alpha1_guess]

        # File uploader

        # Step ID input
        cycle_ids_input = st.text_input("Enter EIS Cycle IDs (comma-separated)", "9")
        try:
            cycle_ids = [int(s.strip()) for s in cycle_ids_input.split(",")]
        except:
            cycle_ids = []

        # Store fit results
        fit_results = []

        if uploaded_files and cycle_ids:
            for file in uploaded_files:
                try:
                    df = pd.read_excel(file, sheet_name = 4)
                except Exception as e:
                    st.error(f"Error reading {file.name}: {e}")
                    continue

                for cycle in cycle_ids:
                    try:
                        cycle_data = df[df["Cycle_ID"] == cycle]
                        if cycle_data.empty:
                            st.warning(f"No data found in {file.name} for cycle {cycle}")
                            continue

                        fit_data = cycle_data[
                            (cycle_data["Frequency"] >= f_min) & (cycle_data["Frequency"] <= f_max)
                        ]

                        if fit_data.empty:
                            st.warning(f"No frequencies in range for {file.name} cycle {cycle}")
                            continue

                        freq = fit_data["Frequency"].values
                        z_re = fit_data["Zreal"].values
                        z_im = fit_data["Zimg"].values
                        Z = z_re + 1j * z_im



                        # Fit circuit
                        circuit_str = "R0 - p(R1, CPE1)"

                        circuit = CustomCircuit(circuit_str, initial_guess=initial_guess)
                        circuit.fit(freq, Z)


                        # # Get parameters
                        # try:
                        #     param_names = circuit.get_param_names()
                        #     param_values = circuit.parameters_
                        #     # Ensure names are strings (avoid list-as-key)
                        #     param_names = [str(p) for p in param_names]
                        #     param_dict = dict(zip(param_names, param_values))
                        # except Exception as p_error:
                        #     st.error(f"Error extracting parameters from {file.name} Step {step}: {p_error}")
                        #     continue
                        params = circuit.parameters_
                        R0, R1, Q1, alpha1 = params

                        fit_results.append({
                            "File": file.name,
                            "Cycle": cycle,
                            "R1 (Ohm)": round(R1, 4),
                            "R0 (Ohm)": round(R0, 4),
                            "Q1 (CPE-T)": round(Q1, 6),
                            "alpha1": round(alpha1, 4)
                        })

                        # Plot Nyquist
                        fig, ax = plt.subplots()
                        plot_nyquist(Z, fmt='o', scale=10, ax=ax)
                        plot_nyquist(circuit.predict(freq), fmt='-', scale=5, ax=ax)
                        ax.set_title(f"{file.name} | Step {step}")
                        ax.legend(["Data", "Fit"])
                        st.pyplot(fig)

                    except Exception as e:
                        st.error(f"Error processing {file.name} cycle {cycle}: {e}")
            # Show table of fit results
            if fit_results:
                st.subheader("Fitted Circuit Parameters")
                result_df = pd.DataFrame(fit_results)
                st.dataframe(result_df)

                # Download
                csv = result_df.to_csv(index=False).encode("utf-8")
                st.download_button("Download Fit Results", csv, "fit_results.csv", "text/csv")
            else:
                st.info("No fit results extracted.")

    with tab2:
        st.header("Multiple EIS plots of a single sample")
        # ---------- Individual File Plots ----------
        if uploaded_files:
            st.subheader("📁 Individual File Plots")

            for uploaded_file in uploaded_files:
                try:
                    df = pd.read_excel(uploaded_file, sheet_name=2)  # 3rd sheet

                    if {'Cycle_ID', 'Zreal', 'Zimg'}.issubset(df.columns):
                        df["Source_File"] = uploaded_file.name
                        all_data.append(df)

                        st.markdown(f"**📊 {uploaded_file.name}**")
                        # Compute global x max across all plots
                        global_x_max = max(df["Zreal"].max() for df in all_data)

                        fig, ax = plt.subplots()

                        for cycle_id, group in df.groupby("Cycle_ID"):
                            ax.plot(group["Zreal"], -group["Zimg"], linestyle=':', marker='o', markersize = 3,
                                    label=f"Cycle {cycle_id}")

                        x_data = df["Zreal"]
                        y_data = -df["Zimg"]
                        set_equal_axes(ax, x_data, y_data, fixed_max=global_x_max)


                        ax.set_xlabel("Zreal")
                        ax.set_ylabel("-Zimg")
                        ax.set_title(f"Nyquist Plot: {uploaded_file.name}")
                        ax.grid(True)
                        ax.legend(fontsize="small")
                        st.pyplot(fig)

                        # Download
                        buffer = io.BytesIO()
                        fig.savefig(buffer, format="png")
                        buffer.seek(0)
                        st.download_button(
                            label=f"📥 Download Plot for {uploaded_file.name}",
                            data=buffer,
                            file_name=f"{uploaded_file.name.replace('.xlsx', '')}_NyquistPlot.png",
                            mime="image/png"
                        )

                    else:
                        st.warning(f"⚠️ Missing required columns in {uploaded_file.name}")

                except Exception as e:
                    st.error(f"❌ Error reading {uploaded_file.name}: {e}")

    with tab3:
        st.header("EIS of single cycle for multiple samples")
        # ---------- Combined Plot by Cycle_ID ----------
        if all_data:
            st.subheader("🔗 Combined Plot by Selected Cycle_ID")

            combined_df = pd.concat(all_data, ignore_index=True)

            cycle_ids = sorted(combined_df["Cycle_ID"].dropna().unique())
            selected_cycle = st.selectbox("Select a Cycle_ID to plot", cycle_ids)

            if selected_cycle is not None:
                filtered_df = combined_df[combined_df["Cycle_ID"] == selected_cycle]

                st.markdown(f"**Cycle_ID: {selected_cycle}**")

                fig, ax = plt.subplots()

                for file_name, group in filtered_df.groupby("Source_File"):
                    ax.plot(group["Zreal"], -group["Zimg"], linestyle=':', marker='o', markersize = 3, label=file_name)

                x_data = filtered_df["Zreal"]
                y_data = -filtered_df["Zimg"]
                set_equal_axes(ax, x_data, y_data)


                ax.set_xlabel("Zreal")
                ax.set_ylabel("-Zimg")
                ax.set_title(f"Combined Nyquist Plot - Cycle_ID {selected_cycle}")
                ax.grid(True)
                ax.legend(title="Source File", fontsize="small")
                st.pyplot(fig)

                # Download
                buffer = io.BytesIO()
                fig.savefig(buffer, format="png")
                buffer.seek(0)
                st.download_button(
                    label="📥 Download Combined Plot",
                    data=buffer,
                    file_name=f"CycleID_{selected_cycle}_Combined_NyquistPlot.png",
                    mime="image/png"
                )





