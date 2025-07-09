def run_PCimp ():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from impedance.models.circuits import CustomCircuit
    from impedance.visualization import plot_nyquist
    import io

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

    tab1, tab2, tab3 = st.tabs(["EIS Fitting", "Individual File Plots", "Combined File Plots"])

    with tab1:
        st.header("EIS Fitting")
        selected_step_id = st.number_input("Enter EIS Step Index to Extract")

        if uploaded_files:
            for uploaded_file in uploaded_files:
                try:
                    df = pd.read_excel(uploaded_file, sheet_name=2)


                    if not {"Zreal", "Zimg", "Frequency"}.issubset(df.columns):
                        st.warning(f"⚠️ {uploaded_file.name} is missing necessary columns.")
                        continue

                    # Extract impedance data
                    # Drop rows with missing or non-numeric values
                    df_clean = df[["Frequency", "Zreal", "Zimg"]].copy()
                    df_clean = df_clean.apply(pd.to_numeric, errors="coerce").dropna()

                    frequencies = df_clean["Frequency"].values.astype(float)
                    Z = df_clean["Zreal"].values.astype(float) + 1j * df_clean["Zimg"].values.astype(float)


                    # Fit with R0-p(R1,C1) circuit
                    circuit = CustomCircuit(initial_guess=[".001", "10", "100"], circuit="R0-p(R1,C1)")
                    circuit.fit(frequencies, Z)

                    # Plot
                    fig, ax = plt.subplots()
                    plot_nyquist(ax, Z, fmt="o", label="Data")
                    plot_nyquist(ax, circuit.predict(frequencies), fmt="-", label="Fit")
                    ax.legend()
                    ax.set_title(f"Nyquist Fit - {uploaded_file.name}")
                    ax.set_xlabel("Zreal")
                    ax.set_ylabel("-Zimg")
                    ax.grid(True)
                    st.pyplot(fig)

                    # Download button
                    buf = io.BytesIO()
                    fig.savefig(buf, format="png")
                    buf.seek(0)
                    st.download_button(
                        label=f"📥 Download Plot - {uploaded_file.name}",
                        data=buf,
                        file_name=f"{uploaded_file.name.replace('.xlsx', '')}_nyquist.png",
                        mime="image/png"
                    )

                except Exception as e:
                    st.error(f"❌ Error processing {uploaded_file.name}: {e}")


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
