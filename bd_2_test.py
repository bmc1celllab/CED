def run_data_analysis():
    import streamlit as st
    import pandas as pd
    import matplotlib.pyplot as plt
    from io import BytesIO

    # Set up page
    st.title("Data Analysis")
    st.text("Upload your data files. You can use the sidebar to adjust the cycles it graphs. There will also be an option to adjust the x-axis and y-axis minimums and maximums. These values will overwrite the cycle index chosen.")


    # --- Define your 5 code functions ---
    # Capacity Retention vs. Cycle Index
    def code_1(dataframes_new, x_min, x_max, y_min, y_max, cycle_range):
        st.subheader("📈 Code 1: Capacity Retention % vs Cycle Index")

        overlay_fig, overlay_ax = plt.subplots()
        valid_plot_count = 0

        for name, df, graph_label in dataframes_new:
            st.markdown(f"**{graph_label}**")

            df.columns = df.columns.str.strip()
            df = df[(df["Cycle Index"] >= cycle_range[0]) & (df["Cycle Index"] <= cycle_range[1])]


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
                    if x_min is not None and x_max is not None:
                        ax.set_xlim(x_min, x_max)
                    if y_min is not None and y_max is not None:
                        ax.set_ylim(y_min, y_max)
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
            if x_min is not None and x_max is not None:
                overlay_ax.set_xlim(x_min, x_max)
            if y_min is not None and y_max is not None:
                overlay_ax.set_ylim(y_min, y_max)
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

    # CE vs. Cycle #
    def code_2(dataframes_new, x_min, x_max, y_min, y_max, cycle_range):
        st.subheader("📈 Code 2: Plot Voltage vs Cycle Index")

        overlay_fig, overlay_ax = plt.subplots()
        valid_plot_count = 0

        for name, df, graph_label in dataframes_new:
            st.markdown(f"**{graph_label}**")

            df.columns = df.columns.str.strip()
            df = df[(df["Cycle Index"] >= cycle_range[0]) & (df["Cycle Index"] <= cycle_range[1])]


            if "Cycle Index" in df.columns and "Coulombic Efficiency (%)" in df.columns:
                x = df["Cycle Index"]
                y = df["Coulombic Efficiency (%)"]

                # Plot individual
                fig, ax = plt.subplots()
                ax.plot(x, y, color="red", marker="o")
                if x_min is not None and x_max is not None:
                    ax.set_xlim(x_min, x_max)
                if y_min is not None and y_max is not None:
                    ax.set_ylim(y_min, y_max)
                ax.set_xlabel("Cycle Index")
                ax.set_ylabel("Coulombic Efficiency (%)")
                ax.set_title(f"{graph_label} — Coulombic Efficiency (%) vs Cycle Index")
                ax.grid(True)
                st.pyplot(fig)

                # Save to buffer
                buf = BytesIO()
                fig.savefig(buf, format="png", bbox_inches="tight")
                buf.seek(0)
                st.download_button(
                    label="📥 Download This Plot as PNG",
                    data=buf,
                    file_name=f"{name.replace('.xlsx','')}_Coulombic Efficiency (%)_vs_CycleIndex.png",
                    mime="image/png"
                )

                # Add to overlay
                overlay_ax.plot(x, y, label=graph_label)
                valid_plot_count += 1

            else:
                st.error("❌ Required columns 'Cycle Index' and 'Coulombic Efficiency (%)' not found.")
            st.markdown("---")

        # Show overlay plot
        if valid_plot_count > 1:
            st.subheader("🧃 Overlay Plot: Coulombic Efficiency (%) vs Cycle Index")
            overlay_ax.set_xlabel("Cycle Index")
            overlay_ax.set_ylabel("Coulombic Efficiency (%)")
            overlay_ax.set_title("Coulombic Efficiency (%) vs Cycle Index")
            if x_min is not None and x_max is not None:
                overlay_ax.set_xlim(x_min, x_max)
            if y_min is not None and y_max is not None:
                overlay_ax.set_ylim(y_min, y_max)
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
                file_name="Overlay_Voltage_vs_CycleIndex.png",
                mime="image/png"
            )

        elif valid_plot_count == 1:
            st.info("Only one valid file — overlay plot not shown.")
        else:
            st.warning("No valid Voltage vs Cycle Index plots to display.")

    # Discharge Capacity vs. Cycle Index
    def code_3(dataframes_new, x_min, x_max, y_min, y_max, cycle_range):
        st.subheader("📈 Code 3: Plot mAh/g vs Cycle Index")

        fig_combined, ax_combined = plt.subplots()
        valid_plot_count = 0
        overlay_buffers = []  # To handle overlay download

        for name, df, graph_label in dataframes_new:
            st.markdown(f"**{graph_label}**")

            df.columns = df.columns.str.strip()
            df = df[(df["Cycle Index"] >= cycle_range[0]) & (df["Cycle Index"] <= cycle_range[1])]


            if "Cycle Index" in df.columns and "mAh/g" in df.columns:
                x = df["Cycle Index"]
                y = df["mAh/g"]

                # Individual plot
                fig, ax = plt.subplots()
                ax.plot(x, y, marker='o', linestyle='-', color='blue')
                if x_min is not None and x_max is not None:
                    ax.set_xlim(x_min, x_max)
                if y_min is not None and y_max is not None:
                    ax.set_ylim(y_min, y_max)
                ax.set_xlabel("Cycle Index")
                ax.set_ylabel("mAh/g")
                ax.set_title(f"{graph_label} — mAh/g vs Cycle Index")
                st.pyplot(fig)

                # Save to image buffer
                buf = BytesIO()
                fig.savefig(buf, format="png", bbox_inches="tight")
                buf.seek(0)
                st.download_button(
                    label="📥 Download This Plot as PNG",
                    data=buf,
                    file_name=f"{name.replace('.xlsx','')}_Cycle_vs_mAhg.png",
                    mime="image/png"
                )

                # Add to combined
                ax_combined.plot(x, y, label=graph_label)
                valid_plot_count += 1
            else:
                st.error("❌ Required columns 'Cycle Index' and 'mAh/g' not found.")
            st.markdown("---")

        # Show combined plot if at least 2 valid files
        if valid_plot_count > 1:
            st.subheader("📊 Combined Overlay Plot")

            ax_combined.set_xlabel("Cycle Index")
            ax_combined.set_ylabel("mAh/g")
            ax_combined.set_title("mAh/g vs Cycle Index")
            if x_min is not None and x_max is not None:
                ax_combined.set_xlim(x_min, x_max)
            if y_min is not None and y_max is not None:
                ax_combined.set_ylim(y_min, y_max)

            ax_combined.legend()

            # Display
            st.pyplot(fig_combined)

            # Save to buffer and allow download
            overlay_buf = BytesIO()
            fig_combined.savefig(overlay_buf, format="png", bbox_inches="tight")
            overlay_buf.seek(0)
            st.download_button(
                label="📥 Download Overlay Plot as PNG",
                data=overlay_buf,
                file_name="Overlay_Cycle_vs_mAhg.png",
                mime="image/png"
            )
        elif valid_plot_count == 1:
            st.info("Only one valid file — overlay not shown.")
        else:
            st.warning("No valid plots to display.")

    # Charge vs. Discharge for One Cycle
    def code_4(dataframes):
        st.subheader("🔍 Cycle Data from Cycle Number")

        cycle_input = st.number_input("Enter Cycle Index (from column D):", min_value=0, step=1, key="cycle_input")

        if st.button("Lookup"):
            results = []

            for name, df in dataframes:
                df.columns = df.columns.str.strip()  # Clean up column names

                # Validate necessary columns
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
                            "Discharge Capacity": round(mah_per_g, 4),
                            "Charge Capacity": round(charge_capacity, 4) if charge_capacity is not None else "Div by 0",
                            "Coulombic Efficiency (%)": round(ce_percent, 4)
                        }
                    else:
                        result_row = {
                            "File": name,
                            "Cycle Index": cycle_input,
                            "mAh/g": "Not Found",
                            "Coulombic Efficiency (%)": "Not Found",
                            "Charge Capacity (calculated)": "Not Found"
                        }
                    results.append(result_row)
                else:
                    st.error(f"Missing required columns in file: {name}")

            st.session_state["code4_results"] = results

        # Display the results table
        if "code4_results" in st.session_state:
            st.subheader("📋 Lookup Results")
            result_df = pd.DataFrame(st.session_state["code4_results"])
            st.dataframe(result_df)

            # CSV download option
            csv = result_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name="code4_cycle_lookup.csv",
                mime="text/csv"
            )

    # Upload multiple Excel files
    uploaded_files = st.file_uploader("📂 Upload Excel files", type=["xlsx"], accept_multiple_files=True)

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

    if "dataframes" in st.session_state:
        code_option = st.selectbox("Choose a code to run:", ["Code 4"])
        if code_option == "Code 4":
            code_4(st.session_state["dataframes"])

    # Determine global cycle index range from all uploaded files
    all_cycle_indices = []

    for _, df, _ in dataframes_new:
        if "Cycle Index" in df.columns:
            all_cycle_indices.extend(df["Cycle Index"].dropna().tolist())

    cycle_min = int(min(all_cycle_indices)) if all_cycle_indices else 0
    cycle_max = int(max(all_cycle_indices)) if all_cycle_indices else 200

    # Sidebar: Cycle Index filter slider
    st.sidebar.markdown("## 🎚️ Filter by Cycle Index")
    cycle_range = st.sidebar.slider(
        "Select range of Cycle Index to display",
        min_value=cycle_min,
        max_value=cycle_max,
        value=(cycle_min, cycle_max),
        step=1,
        key="cycle_range_slider"
)

    # --- Display 5 buttons to run code blocks ---
    if dataframes:
        st.markdown("### 👉 Select a code to run:")
        bounds_enabled = st.sidebar.checkbox("Custom Axis Bounds", value = False)
        x_min = x_max = y_min = y_max = None

        if bounds_enabled:
            st.sidebar.markdown("## 📐 Axis Bounds")
            x_min = st.sidebar.number_input("X Min", value=0.0)
            x_max = st.sidebar.number_input("X Max", value=250.0)
            y_min = st.sidebar.number_input("Y Min", value=0.0)
            y_max = st.sidebar.number_input("Y Max", value=250.0)

        rerun = st.sidebar.button("🔄 Rerun Selected Plot")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Capacity Retention") or (rerun and st.session_state.get("active_code") == "code_1"):
                st.session_state["active_code"] = "code_1"
                code_1(dataframes_new, x_min, x_max, y_min, y_max, cycle_range)

        with col2:
            if st.button("Coulombic Efficiency vs. Cycle Index") or (rerun and st.session_state.get("active_code") == "code_2"):
                st.session_state["active_code"] = "code_2"
                code_2(dataframes_new, x_min, x_max, y_min, y_max, cycle_range)

        with col3:
            if st.button("mAh/g vs. Cycle Index") or (rerun and st.session_state.get("active_code") == "code_3"):
                st.session_state["active_code"] = "code_3"
                code_3(dataframes_new, x_min, x_max, y_min, y_max, cycle_range)

