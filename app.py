import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Page settings
st.set_page_config(page_title="☀️ PV Energy Dashboard", layout="wide")
st.title("☀️ Solar PV Dashboard")

# Upload Excel file
uploaded_file = st.file_uploader("Upload PV Data (Excel file)", type=["xlsx"])

if uploaded_file:
    # Load 3rd sheet (index = 2)
    df = pd.read_excel(uploaded_file, sheet_name=2)
    st.success("✅ File loaded successfully (3rd sheet)")

    # Clean column names
    df.columns = df.columns.str.strip()

    # Separate daily and hourly data
    daily_df = df[["Date", "Daily generated electricity [kWh]"]].dropna()
    hourly_df = df[["Date/Time", "Hourly generated electricity [kWh]"]].dropna()

    # Convert to datetime
    daily_df["Date"] = pd.to_datetime(daily_df["Date"])
    hourly_df["Date/Time"] = pd.to_datetime(hourly_df["Date/Time"])

    # Convert negative values to positives
    daily_df["Daily generated electricity [kWh]"] = daily_df["Daily generated electricity [kWh]"].abs()
    hourly_df["Hourly generated electricity [kWh]"] = hourly_df["Hourly generated electricity [kWh]"].abs()

    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    start_date, end_date = st.sidebar.date_input(
        "Select date range",
        [daily_df["Date"].min().date(), daily_df["Date"].max().date()]
    )

    mask_daily = (daily_df["Date"].dt.date >= start_date) & (daily_df["Date"].dt.date <= end_date)
    mask_hourly = (hourly_df["Date/Time"].dt.date >= start_date) & (hourly_df["Date/Time"].dt.date <= end_date)

    daily_df = daily_df.loc[mask_daily]
    hourly_df = hourly_df.loc[mask_hourly]

    # KPIs
    st.subheader("📊 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Energy (kWh)", f"{daily_df['Daily generated electricity [kWh]'].sum():.2f}")
    col2.metric("Average Daily Energy (kWh)", f"{daily_df['Daily generated electricity [kWh]'].mean():.2f}")
    col3.metric("Peak Daily (kWh)", f"{daily_df['Daily generated electricity [kWh]'].max():.2f}")
    col4.metric("Peak Hourly (kWh)", f"{hourly_df['Hourly generated electricity [kWh]'].max():.2f}")

    # Daily energy chart
    st.subheader("🌅 Daily Generated Energy")
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    ax1.bar(daily_df["Date"], daily_df["Daily generated electricity [kWh]"], color="orange")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Energy [kWh]")
    ax1.set_title("Daily Generated Electricity")
    st.pyplot(fig1)

    # Hourly chart: show hour on x-axis
    st.subheader("⏱️ Hourly Generated Energy (by Hour of Day)")
    hourly_df["Hour"] = hourly_df["Date/Time"].dt.hour
    hourly_by_hour = hourly_df.groupby("Hour")["Hourly generated electricity [kWh]"].mean()
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    ax2.plot(hourly_by_hour.index, hourly_by_hour.values, marker='o', color="green")
    ax2.set_xlabel("Hour of Day")
    ax2.set_ylabel("Energy [kWh]")
    ax2.set_title("Average Hourly Generated Electricity")
    ax2.set_xticks(range(0, 24))
    st.pyplot(fig2)

    # Optional: show raw data
    with st.expander("📋 View Raw Data"):
        st.write("**Daily Data**")
        st.dataframe(daily_df)
        st.write("**Hourly Data**")
        st.dataframe(hourly_df)

else:
    st.info("👈 Upload your Excel file to begin.")
