def run_data_analysis():
    import streamlit as st
    import pandas as pd
    import matplotlib.pyplot as plt
    from io import BytesIO
    import io

    # Set up page
    st.title("Data Analysis")
    st.text("Upload your data files.")
    
    # Upload multiple Excel files
    uploaded_files = st.file_uploader("📂 Upload Excel files", type=["xlsx"], accept_multiple_files=True)

    tab1, tab2, tab3 = st.tabs(["First Cycle Data", "Capacity Retention (NO EIS)", "Custom Data Analysis"])

    with tab1:
        st.subheader("🔍 Cycle Data from Cycle Number")
        if uploaded_files:
            dataframes = []
            for file in uploaded_files:
                try:
                    df = pd.read_excel(file, sheet_name=2)  # Sheet 3 (0-indexed)
                    df.columns = df.columns.str.strip()
                    df = df.iloc[:-1]  # Drop last row (e.g., "Total" row)
                    dataframes.append((file.name, df))
                except Exception as e:
                    st.error(f"Error reading {file.name}: {e}")

            # Store in session state
            st.session_state["dataframes"] = dataframes

        # Input: Cycle Index
        cycle_input = st.number_input("Enter Cycle Index (from column D):", min_value=1, step=1, key="cycle_input")

        # Lookup button
        if st.button("Lookup") and "dataframes" in st.session_state:
            results = []

            for name, df in st.session_state["dataframes"]:
                df.columns = df.columns.str.strip()  # Clean column names

                required_cols = ["Cycle Index", "mAh/g", "Coulombic Efficiency (%)"]
                if all(col in df.columns for col in required_cols):
                    match = df[df["Cycle Index"] == cycle_input]

                    if not match.empty:
                        mah_per_g = match.iloc[0]["mAh/g"]
                        ce_percent = match.iloc[0]["Coulombic Efficiency (%)"]

                        # Avoid division by zero
                        try:
                            charge_capacity = mah_per_g / (ce_percent / 100)
                        except ZeroDivisionError:
                            charge_capacity = None

                        result_row = {
                            "File": name,
                            "Cycle Index": cycle_input,
                            "Discharge Capacity (mAh/g)": round(mah_per_g, 4),
                            "Charge Capacity (calculated)": round(charge_capacity, 4) if charge_capacity is not None else "Div by 0",
                            "Coulombic Efficiency (%)": round(ce_percent, 4)
                        }
                    else:
                        result_row = {
                            "File": name,
                            "Cycle Index": cycle_input,
                            "Discharge Capacity (mAh/g)": "Not Found",
                            "Charge Capacity (calculated)": "Not Found",
                            "Coulombic Efficiency (%)": "Not Found"
                        }
                else:
                    st.error(f"Missing required columns in file: {name}")
                    continue

                results.append(result_row)

            # Store results
            st.session_state["code4_results"] = results

        # Show results
        if "code4_results" in st.session_state:
            st.subheader("📋 Lookup Results")
            result_df = pd.DataFrame(st.session_state["code4_results"])
            st.dataframe(result_df)

            # Download option
            csv = result_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name="code4_cycle_lookup.csv",
                mime="text/csv"
            )

    with tab2:
        dataframes = []
        dataframes_new = []

        if uploaded_files:
            dataframes = []
            for file in uploaded_files:
                try:
                    df = pd.read_excel(file, sheet_name=2)  # Sheet 3
                    df.columns = df.columns.str.strip()
                    df = df.iloc[:-1]  # drop the last row
                    sheet1 = pd.read_excel(file, sheet_name=0, header=None)
                    graph_label = str(sheet1.iloc[1, 3])  # D2 = row 1, col 3
                    dataframes.append((file.name, df))
                    dataframes_new.append((file.name, df, graph_label))
                except Exception as e:
                    st.error(f"Error reading {file.name}: {e}")
            st.session_state["dataframes"] = dataframes
        st.subheader("Capacity Retention % vs Cycle Index")
        overlay_fig, overlay_ax = plt.subplots()
        valid_plot_count = 0

        for name, df, graph_label in dataframes_new:
            st.markdown(f"**{graph_label}**")

            df.columns = df.columns.str.strip()
            #df = df[(df["Cycle Index"] >= cycle_range[0]) & (df["Cycle Index"] <= cycle_range[1])]

            if "Cycle Index" in df.columns and "mAh/g" in df.columns:
                try:
                    baseline = df.iloc[4]["mAh/g"]

                    if pd.isna(baseline) or baseline == 0:
                        st.error(f"⚠️ Invalid baseline in row 5 of `{name}`.")
                        continue

                    # Calculate retention %
                    retention = (df["mAh/g"] / baseline) * 100
                    cycle_index = df["Cycle Index"]

                    # Plot individual
                    fig, ax = plt.subplots()
                    ax.plot(cycle_index, retention, color="green", marker="o")
                    ax.set_xlabel("Cycle Index")
                    ax.set_ylabel("Retention (%)")
                    ax.set_title(f"{graph_label} — Retention vs Cycle Index")
                    ax.grid(True)
                    st.pyplot(fig)

                    # Enable download
                    buf = BytesIO()
                    fig.savefig(buf, format="png", bbox_inches="tight")
                    buf.seek(0)
                    st.download_button(
                        label="📥 Download This Plot as PNG",
                        data=buf,
                        file_name=f"{name.replace('.xlsx','')}_Retention_vs_CycleIndex.png",
                        mime="image/png"
                    )

                    # Add to overlay
                    overlay_ax.plot(cycle_index, retention, label=graph_label)
                    valid_plot_count += 1

                except Exception as e:
                    st.error(f"❌ Error processing `{name}`: {e}")
            else:
                st.error("❌ Columns 'Cycle Index' and 'mAh/g' not found.")
            st.markdown("--")

        # Show combined overlay plot
        if valid_plot_count > 1:
            st.subheader("🧃 Overlay Plot: Retention % vs Cycle Index")

            overlay_ax.set_xlabel("Cycle Index")
            overlay_ax.set_ylabel("Retention (%)")
            overlay_ax.set_title("Retention vs Cycle Index")
            overlay_ax.grid(True)
            overlay_ax.legend()

            st.pyplot(overlay_fig)

            # Download overlay
            overlay_buf = BytesIO()
            overlay_fig.savefig(overlay_buf, format="png", bbox_inches="tight")
            overlay_buf.seek(0)
            st.download_button(
                label="📥 Download Overlay Plot as PNG",
                data=overlay_buf,
                file_name="Overlay_Retention_vs_CycleIndex.png",
                mime="image/png"
            )
        elif valid_plot_count == 1:
            st.info("Only one valid file — overlay plot not shown.")
        else:
            st.warning("No valid retention plots to display.")

        fig_combined, ax_combined = plt.subplots()
        valid_plot_count = 0
        overlay_buffers = []  # To handle overlay download

    with tab3:
        sheet_number = st.number_input("Sheet index (0-based)", min_value=0, step=1)

        if uploaded_files:
            try:
                # Load full sheet from first file to extract headers properly
                preview_df = pd.read_excel(uploaded_files[0], sheet_name=sheet_number)
                headers = preview_df.columns.tolist()
            except Exception as e:
                st.error(f"Could not read sheet: {e}")
                st.stop()

            # Step 3: X and Y axis selection
            x_axis = st.selectbox("Select X-axis column", headers)
            y_axis_1 = st.selectbox("Select Y-axis column", headers)
            use_y2 = st.checkbox("Plot a second Y-axis? (Y2)")

            y_axis_2 = None
            if use_y2:
                y_axis_2 = st.selectbox("Select Y-axis (Secondary)", [col for col in headers if col != y_axis_1])

            # Step 4: Optional Cycle Index filter
            st.subheader("Optional Filters")
            use_cycle_filter = st.checkbox("Filter by cycle index column?")

            if use_cycle_filter:
                cycle_col = st.selectbox("Select the cycle index column", headers)
                filter_type = st.radio("Filter Type", ["Single Value", "Range"])
                if filter_type == "Single Value":
                    single_cycle = st.number_input("Cycle Index value", step=1, format="%d")
                    cycle_range = None
                else:
                    c1, c2 = st.columns(2)
                    start = c1.number_input("Start Cycle Index", step=1, format="%d")
                    end = c2.number_input("End Cycle Index", step=1, format="%d")
                    cycle_range = (start, end)
                    single_cycle = None
            else:
                cycle_col = None
                single_cycle = None
                cycle_range = None

            # Step 4.5: Optional axis limits
            use_axis_filter = st.checkbox("Apply custom axis limits?")

            x_limits = (None, None)
            y1_limits = (None, None)
            y2_limits = (None, None)

            if use_axis_filter:
                st.markdown("**X-Axis Limits**")
                col1, col2 = st.columns(2)
                with col1:
                    x_limits = list(x_limits)
                    x_limits[0] = st.number_input("X-axis min", value=0.0)
                with col2:
                    x_limits[1] = st.number_input("X-axis max", value=100.0)

                st.markdown("**Y1-Axis Limits (Primary)**")
                col3, col4 = st.columns(2)
                with col3:
                    y1_limits = list(y1_limits)
                    y1_limits[0] = st.number_input("Y1-axis min", value=0.0)
                with col4:
                    y1_limits[1] = st.number_input("Y1-axis max", value=100.0)

                if use_y2:
                    st.markdown("**Y2-Axis Limits (Secondary)**")
                    col5, col6 = st.columns(2)
                    with col5:
                        y2_limits = list(y2_limits)
                        y2_limits[0] = st.number_input("Y2-axis min", value=0.0)
                    with col6:
                        y2_limits[1] = st.number_input("Y2-axis max", value=100.0)


            # Step 4.6: Optional line style
            use_custom_style = st.checkbox("Customize line style?")

            line_style = '-'
            show_markers = False
            if use_custom_style:
                line_style_options = {
                    "Solid (-)": '-',
                    "Dashed (--)": '--',
                    "Dash-dot (-.)": '-.',
                    "Dotted (:)": ':',
                    "No line (only points)": 'None'
                }
                line_style_label = st.selectbox("Select line style", list(line_style_options.keys()))
                line_style = line_style_options[line_style_label]
                show_markers = st.checkbox("Show markers (points at every data point)?")


            # Step 5: Plotting
            st.subheader("Plot")

            fig, ax1 = plt.subplots(figsize=(10, 6))
            ax2 = ax1.twinx() if use_y2 else None

            for file in uploaded_files:
                try:
                    # Legend name from Sheet 1, Cell D2
                    legend_df = pd.read_excel(file, sheet_name=0, header=None)
                    legend_name = legend_df.iloc[1, 3] if legend_df.shape[1] > 3 and legend_df.shape[0] > 1 else file.name

                    # Load selected sheet
                    df = pd.read_excel(file, sheet_name=sheet_number)

                    # Filter by cycle column if enabled
                    if cycle_col and cycle_col in df.columns:
                        if single_cycle is not None:
                            df = df[df[cycle_col] == single_cycle]
                        elif cycle_range is not None:
                            df = df[df[cycle_col].between(cycle_range[0], cycle_range[1])]

                    # Convert x and y to numeric, drop NaNs
                    df[x_axis] = pd.to_numeric(df[x_axis], errors='coerce')
                    df[y_axis_1] = pd.to_numeric(df[y_axis_1], errors='coerce')
                    # Special rule: if y-axis is 'Zimg', multiply it by -1
                    if y_axis_1.lower() in ['zimg', 'zimag', 'imag(z)']:
                        df[y_axis_1] = -1 * df[y_axis_1]
                    df = df.dropna(subset=[x_axis, y_axis_1])

                    # Determine marker and line style
                    is_no_line = line_style in ['None', '', ' ']
                    marker_style = 'o' if show_markers or is_no_line else None
                    line_style_final = None if is_no_line else line_style

                    # Plot
                    # Plot Y1 (primary)
                    ax1.plot(
                        df[x_axis],
                        df[y_axis_1],
                        label=f"{legend_name} - {y_axis_1}",
                        linestyle=line_style_final,
                        marker=marker_style,
                        color='tab:blue'  # Consistent color for primary axis
                    )

                    # Plot Y2 (secondary)
                    if use_y2 and y_axis_2 in df.columns:
                        df[y_axis_2] = pd.to_numeric(df[y_axis_2], errors='coerce')
                        df = df.dropna(subset=[y_axis_2])

                        # Special Zimg logic for y2 as well
                        if y_axis_2.lower().strip().replace(' ', '') in ['zimg', 'zimag', 'imag(z)', "z''"]:
                            df[y_axis_2] = -1 * df[y_axis_2]

                        ax2.plot(
                            df[x_axis],
                            df[y_axis_2],
                            label=f"{legend_name} - {y_axis_2}",
                            linestyle=line_style_final,
                            marker=marker_style,
                            color='tab:red'  # Different color for secondary axis
                        )

                except Exception as e:
                    st.error(f"Error with file {file.name}: {e}")

            # Title and labels
        # Title and labels
            title_text = f"{y_axis_1}" + (f" & {y_axis_2}" if use_y2 else "") + f" vs. {x_axis}"
            ax1.set_title(title_text)
            ax1.set_xlabel(x_axis)
            ax1.set_ylabel(y_axis_1, color='tab:blue')
            ax1.legend()
            if ax2:
                ax2.set_ylabel(y_axis_2, color='tab:red')
            # Apply axis limits if selected
            if use_axis_filter:
                ax1.set_xlim(x_limits)
                ax1.set_ylim(y1_limits)
                if ax2 and use_y2:
                    ax2.set_ylim(y2_limits)

            st.pyplot(fig)

            # Step 6: Download the plot
            st.subheader("Download Plot")
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            st.download_button(
                label="Download plot as PNG",
                data=buf.getvalue(),
                file_name=f"{title_text}.png",
                mime="image/png"
            )