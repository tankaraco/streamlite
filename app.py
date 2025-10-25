import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------
st.set_page_config(
    page_title="👼 Solar PV Energy Dashboard",
    layout="wide",
    page_icon="👼"
)

# -----------------------------------------------------------
# Custom Styling
# -----------------------------------------------------------
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom right, #fffdf5, #fdfaf1);
        color: #222222;
        font-family: 'Segoe UI', sans-serif;
    }
    .main-title {
        font-size: 36px;
        font-weight: 700;
        color: #f5a623;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 5px;
        letter-spacing: 0.5px;
    }
    .subtitle {
        text-align: center;
        color: #666666;
        font-size: 16px;
        margin-top: -10px;
        margin-bottom: 25px;
    }
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(to right, transparent, #f5a623, transparent);
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #fffdfa;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(245,166,35,0.15);
    }
    .metric-value {
        font-size: 22px;
        font-weight: 700;
        color: #333333;
    }
    .metric-label {
        font-size: 13px;
        color: #777777;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# Title Section
# -----------------------------------------------------------
st.markdown("""
    <div class="main-title">👼 Solar PV Energy Dashboard</div>
    <div class="subtitle">Hello droppie ⚡</div>
    <hr>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# Load Data
# -----------------------------------------------------------
excel_file = "ITA_PG_Bastardo_community_REV4.xlsx"  # Update filename

try:
    df = pd.read_excel(excel_file, sheet_name=2)
    st.success(f"✅ File '{excel_file}' loaded successfully (3rd sheet)")

    # --- Data Cleaning ---
    df.columns = df.columns.str.strip()
    daily_df = df[["Date", "Daily generated electricity [kWh]"]].dropna()
    hourly_df = df[["Date/Time", "Hourly generated electricity [kWh]"]].dropna()

    daily_df["Date"] = pd.to_datetime(daily_df["Date"])
    hourly_df["Date/Time"] = pd.to_datetime(hourly_df["Date/Time"])
    daily_df["Daily generated electricity [kWh]"] = daily_df["Daily generated electricity [kWh]"].abs()
    hourly_df["Hourly generated electricity [kWh]"] = hourly_df["Hourly generated electricity [kWh]"].abs()

    # -----------------------------------------------------------
    # Sidebar Filters
    # -----------------------------------------------------------
    st.sidebar.header("🔍 Filters")
    start_date, end_date = st.sidebar.date_input(
        "Select date range",
        [daily_df["Date"].min().date(), daily_df["Date"].max().date()]
    )

    mask_daily = (daily_df["Date"].dt.date >= start_date) & (daily_df["Date"].dt.date <= end_date)
    mask_hourly = (hourly_df["Date/Time"].dt.date >= start_date) & (hourly_df["Date/Time"].dt.date <= end_date)

    daily_df = daily_df.loc[mask_daily]
    hourly_df = hourly_df.loc[mask_hourly]

    # -----------------------------------------------------------
    # KPI Section
    # -----------------------------------------------------------
    st.subheader("📊 Key Performance Indicators")

    col1, col2, col3, col4 = st.columns(4)
    total_energy = daily_df["Daily generated electricity [kWh]"].sum()
    avg_daily = daily_df["Daily generated electricity [kWh]"].mean()
    peak_daily = daily_df["Daily generated electricity [kWh]"].max()
    peak_hourly = hourly_df["Hourly generated electricity [kWh]"].max()

    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_energy:,.2f} kWh</div><div class='metric-label'>⚡ Total Energy</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{avg_daily:,.2f} kWh</div><div class='metric-label'>📅 Avg Daily</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{peak_daily:,.2f} kWh</div><div class='metric-label'>🌞 Peak Daily</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{peak_hourly:,.2f} kWh</div><div class='metric-label'>⌚ Peak Hourly</div></div>", unsafe_allow_html=True)

    # -----------------------------------------------------------
    # Tabs
    # -----------------------------------------------------------
    tab1, tab2, tab3 = st.tabs(["📈 Daily Energy", "⏱️ Hourly Energy", "📋 Raw Data"])

    # --- Daily Energy Chart ---
    with tab1:
        fig1 = px.bar(
            daily_df,
            x="Date",
            y="Daily generated electricity [kWh]",
            color="Daily generated electricity [kWh]",
            color_continuous_scale="sunset",
            template="plotly_white"
        )
        fig1.update_layout(
            margin=dict(l=10, r=10, t=40, b=30),
            title="🌅 Daily Generated Electricity",
            title_x=0.5,
            xaxis_title="Date",
            yaxis_title="Energy [kWh]",
            hovermode="x unified",
            font=dict(size=12),
        )
        st.plotly_chart(fig1, use_container_width=True)

    # --- Hourly Energy Chart ---
    with tab2:
        hourly_df["Hour"] = hourly_df["Date/Time"].dt.hour
        hourly_by_hour = hourly_df.groupby("Hour")["Hourly generated electricity [kWh]"].mean().reset_index()

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=hourly_by_hour["Hour"],
            y=hourly_by_hour["Hourly generated electricity [kWh]"],
            mode="lines+markers",
            line=dict(color="#2ECC71", width=3),
            marker=dict(size=8, color="#27AE60"),
            name="Hourly Energy"
        ))
        fig2.update_layout(
            margin=dict(l=10, r=10, t=40, b=30),
            title="⏱️ Average Hourly Generated Electricity",
            xaxis_title="Hour of Day",
            yaxis_title="Energy [kWh]",
            template="plotly_white",
            title_x=0.5,
            hovermode="x",
            font=dict(size=12)
        )
        st.plotly_chart(fig2, use_container_width=True)

    # --- Raw Data ---
    with tab3:
        st.write("**Daily Data**")
        st.dataframe(daily_df.style.background_gradient(cmap="YlOrBr"), use_container_width=True)
        st.write("**Hourly Data**")
        st.dataframe(hourly_df.style.background_gradient(cmap="Greens"), use_container_width=True)

except FileNotFoundError:
    st.warning(f"⚠️ Excel file '{excel_file}' not found. Please upload or place it in the same folder.")
