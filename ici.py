def run_ici():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.stats import linregress
    from scipy.interpolate import interp1d

    st.title("Lithium Diffusion Coefficient Analysis (ICI Method)")

    # === INPUT SECTION ===

    st.sidebar.header("Input Parameters")
    rp = st.sidebar.number_input("Mean Particle Radius (cm)", value=0.0002, format="%.5f")
    charge_step = st.sidebar.number_input("Charge Step Index", value=8)
    pause_step = st.sidebar.number_input("Pause Step Index", value=7)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Upload Data Files")

    # Grouped file upload by sample
    sample_files = {}
    sample_names = st.sidebar.text_area("Enter Sample Names (one per line)", "14769\n14785\n14830").splitlines()

    for sample_name in sample_names:
        uploaded = st.sidebar.file_uploader(f"Upload files for sample: {sample_name}", type="xlsx", accept_multiple_files=True)
        if uploaded:
            sample_files[sample_name] = uploaded

    # === MAIN ANALYSIS ===
    if not sample_files:
        st.warning("Please upload files to begin analysis.")
        st.stop()

    summary_data = []
    fig, axes = plt.subplots(2, 1, figsize=(15, 12), sharex=True)
    colors = plt.cm.tab20.colors

    for i, (sample_name, file_list) in enumerate(sample_files.items()):
        color = colors[i % len(colors)]
        valid_voltage_ranges = []
        interp_chg_diff = []

        for file in file_list:
            df = pd.read_excel(file, sheet_name=1)
            D_Li_c = []
            file_label = file.name

            ICI_steps = list(range(3, df['Cycle Index'].max() - 1))

            for step in ICI_steps:
                charge_data = df[(df['Cycle Index'] == step) & (df['Step Index'] == charge_step)].copy()
                pause_data = df[(df['Cycle Index'] == step) & (df['Step Index'] == pause_step)].copy()
                next_pause_data = df[(df['Cycle Index'] == step + 1) & (df['Step Index'] == pause_step)].copy()

                if not (charge_data.empty or pause_data.empty or next_pause_data.empty):
                    try:
                        tau = charge_data['Test Time (s)'].iloc[-1] - charge_data['Test Time (s)'].iloc[0]
                        t0 = pause_data['Test Time (s)'].iloc[0]
                        mask = (pause_data['Test Time (s)'] - t0 >= 0.1) & (pause_data['Test Time (s)'] - t0 <= 5)
                        dEt_data = pause_data[mask]

                        if not dEt_data.empty:
                            sqrt_t = np.sqrt(dEt_data['Test Time (s)'] - t0)
                            voltage = dEt_data['Voltage (V)']
                            slope, *_ = linregress(sqrt_t, voltage)
                            dEt = abs(slope)
                            dEs = abs(next_pause_data['Voltage (V)'].iloc[0] - pause_data['Voltage (V)'].iloc[0])
                            Eeq_vals = pause_data['Voltage (V)'].iloc[0]

                            if dEt != 0 and tau != 0:
                                D = (4 / (np.pi * 9)) * ((rp / tau) ** 2) * ((dEs / dEt) ** 2)
                                D_Li_c.append({'Step': step, 'Diff_coef_c (cm^2/s)': D, 'Eeq_c (V)': Eeq_vals})
                    except Exception as e:
                        st.error(f"{file_label} CHARGE: Error at step {step} - {e}")

            results_df_c = pd.DataFrame(D_Li_c)

            if not results_df_c.empty:
                axes[0].scatter(results_df_c['Eeq_c (V)'], results_df_c['Diff_coef_c (cm^2/s)'],
                                label=f"{sample_name}", color=color, s=30, edgecolors='black', alpha=0.6)

                sorted_data = results_df_c.sort_values('Eeq_c (V)')
                vmin = sorted_data['Eeq_c (V)'].min()
                vmax = sorted_data['Eeq_c (V)'].max()
                valid_voltage_ranges.append((vmin, vmax))
                interp_chg_diff.append((sorted_data['Eeq_c (V)'], sorted_data['Diff_coef_c (cm^2/s)']))

        if valid_voltage_ranges:
            vmin_all = max(v[0] for v in valid_voltage_ranges)
            vmax_all = min(v[1] for v in valid_voltage_ranges)
            voltage_grid = np.linspace(vmin_all, vmax_all, 1000)

            interp_matrix = []
            for v_vals, d_vals in interp_chg_diff:
                interp_func = interp1d(v_vals, d_vals, kind='linear', bounds_error=False, fill_value=np.nan)
                interp_matrix.append(interp_func(voltage_grid))

            chg_matrix = np.array(interp_matrix)
            mean_chg_diff = np.nanmean(chg_matrix, axis=0)
            std_chg_diff = np.nanstd(chg_matrix, axis=0)

            axes[1].plot(voltage_grid, mean_chg_diff, color=color, linewidth=2.5, label=f"{sample_name} Mean")
            axes[1].fill_between(voltage_grid, mean_chg_diff - std_chg_diff, mean_chg_diff + std_chg_diff,
                                color=color, alpha=0.3)

            max_idx = np.nanargmax(mean_chg_diff)
            max_voltage = voltage_grid[max_idx]
            max_diff_val = mean_chg_diff[max_idx]
            max_std_val = std_chg_diff[max_idx]

            summary_data.append({
                "Sample": sample_name,
                "Voltage (V)": round(max_voltage, 3),
                "Mean Diff Coef (cm^2/s)": max_diff_val,
                "Std Dev": max_std_val,
                "Diff Coef (cm^2/s)": f"{max_diff_val:.2e} ± {max_std_val:.2e}"
            })

    # === FINAL FORMATTING ===
    axes[0].set_title('ICI Calculated Li Diff Coefficients', fontsize=18, fontweight='bold')
    axes[0].set_ylabel('Li Diff Coef (cm$^2$/s)', fontsize=16, fontweight='bold')
    axes[0].set_xlabel('Cell Potential (V)')
    axes[0].grid(True, linestyle='--', alpha=0.6)

    axes[1].set_title("Mean and Standard Deviation", fontsize=18, fontweight='bold')
    axes[1].set_ylabel('Li Diff Coef (cm$^2$/s)', fontsize=16, fontweight='bold')
    axes[1].set_xlabel('Cell Potential (V)', fontsize=16, fontweight='bold')
    axes[1].grid(True, linestyle='--', alpha=0.6)
    axes[1].legend(fontsize=15)

    plt.tight_layout()
    fig.subplots_adjust(top=0.9)
    st.pyplot(fig)

    # === DISPLAY SUMMARY ===
    summary_df = pd.DataFrame(summary_data)
    st.subheader("Summary Table: Max Diffusion Coefficients")
    st.dataframe(summary_df)