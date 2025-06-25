def run_CD_any_cycle():
    import streamlit as st
    import pandas as pd
    import matplotlib.pyplot as plt

    st.title("Voltage vs. Capacity of Single Cycle")

    uploaded_files = st.file_uploader("📂 Upload Excel Files", type=["xlsx"], accept_multiple_files=True)

    if uploaded_files:
        data_per_file = []
        all_cycles = set()

        for file in uploaded_files:
            try:
                sheet1 = pd.read_excel(file, sheet_name=0, header=None)
                mass = sheet1.iloc[4, 7]

                if pd.isna(mass) or mass == 0:
                    st.warning(f"⚠️ Skipping {file.name}: Invalid mass in Sheet1!H5")
                    continue

                df = pd.read_excel(file, sheet_name=1)
                df.columns = df.columns.str.strip()

                required = ["Cycle Index", "Voltage (V)", "Charge Capacity (Ah)", "Discharge Capacity (Ah)"]
                if not all(col in df.columns for col in required):
                    st.warning(f"⚠️ Skipping {file.name}: Missing required columns.")
                    continue

                all_cycles.update(df["Cycle Index"].dropna().unique())
                sheet1 = pd.read_excel(file, sheet_name=0, header=None)
                graph_label = str(sheet1.iloc[1, 3])  # D2 = row 1, col 3
                data_per_file.append({
                    "name": graph_label,
                    "mass": mass,
                    "df": df
                })

            except Exception as e:
                st.error(f"❌ Error reading {file.name}: {e}")

        if not data_per_file:
            st.stop()

        selected_cycle = st.selectbox("🔁 Select Cycle Index to Plot:", sorted(all_cycles))

        # Matplotlib color cycle
        color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']

        tab1, tab2 = st.tabs(["🧃 Overlay Plot", "📄 Individual Plots"])

        st.sidebar.header("📐 Axis Presets")

        # Preset options (simulate radio buttons with checkboxes)
        zoomed = st.sidebar.checkbox("🔍 1st Cycle Intersection View (X: 100–140, Y: 3.75–3.90)")
        full_range = st.sidebar.checkbox("📊 1st Cycle Charge (X: 225–260, Y: 4.20–4.35)")
        discharge_range = st.sidebar.checkbox("📊 1st Cycle Disharge (X: 220–235, Y: 2.45–2.6)")
        custom = st.sidebar.checkbox("⚙️ Custom Input Bounds")

        # Default bounds (None = autoscale)
        x_min = x_max = y_min = y_max = None

        # Apply presets based on first match
        if zoomed:
            x_min, x_max = 100, 140
            y_min, y_max = 3.75, 3.90
        elif full_range:
            x_min, x_max = 225, 260
            y_min, y_max = 4.2, 4.35
        elif discharge_range:
            x_min, x_max = 220, 235
            y_min, y_max = 2.45, 2.6
        elif custom:
            x_min = st.sidebar.number_input("X Min (Capacity)", value=0.0)
            x_max = st.sidebar.number_input("X Max (Capacity)", value=300.0)
            y_min = st.sidebar.number_input("Y Min (Voltage)", value=2.0)
            y_max = st.sidebar.number_input("Y Max (Voltage)", value=4.5)

        with tab1:
            st.subheader("Overlay Plot (Static)")

            fig, ax = plt.subplots()
            fig.patch.set_facecolor("white")
            ax.set_facecolor("white")

            for i, data in enumerate(data_per_file):
                df = data["df"]
                mass = data["mass"]
                name = data["name"]
                color = color_cycle[i % len(color_cycle)]

                df_cycle = df[df["Cycle Index"] == selected_cycle]
                if df_cycle.empty:
                    continue

                voltage = df_cycle["Voltage (V)"]
                charge = (df_cycle["Charge Capacity (Ah)"] * 1000) / mass
                discharge = (df_cycle["Discharge Capacity (Ah)"] * 1000) / mass

                ax.plot(discharge, voltage, label=name, color=color, linestyle='-')
                ax.plot(charge, voltage, color=color, linestyle='--')
                if x_min is not None and x_max is not None:
                    ax.set_xlim(x_min, x_max)
                if y_min is not None and y_max is not None:
                    ax.set_ylim(y_min, y_max)

            ax.set_xlabel("Capacity (mAh/g)", color="black")
            ax.set_ylabel("Voltage (V)", color="black")
            ax.set_title(f"Overlay Plot — Cycle {selected_cycle}", color="black")
            ax.legend()
            ax.tick_params(colors='black')
            st.pyplot(fig)

        with tab2:
            st.subheader("Individual File Plots")

            for i, data in enumerate(data_per_file):
                df = data["df"]
                mass = data["mass"]
                name = data["name"]
                color = color_cycle[i % len(color_cycle)]

                df_cycle = df[df["Cycle Index"] == selected_cycle]
                if df_cycle.empty:
                    st.warning(f"⚠️ No data for Cycle {selected_cycle} in {name}.")
                    continue

                voltage = df_cycle["Voltage (V)"]
                charge = (df_cycle["Charge Capacity (Ah)"] * 1000) / mass
                discharge = (df_cycle["Discharge Capacity (Ah)"] * 1000) / mass

                fig, ax = plt.subplots()
                fig.patch.set_facecolor("white")
                ax.set_facecolor("white")

                ax.plot(discharge, voltage, label=name, color=color, linestyle='-')
                ax.plot(charge, voltage, color=color, linestyle='--')

                ax.set_xlabel("Capacity (mAh/g)", color="black")
                ax.set_ylabel("Voltage (V)", color="black")
                ax.set_title(f"{name} — Cycle {selected_cycle}", color="black")
                ax.legend()
                ax.tick_params(colors='black')
                st.pyplot(fig)
