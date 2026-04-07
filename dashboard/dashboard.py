import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import gdown
import os
sns.set(style='dark')

# LOAD DATA
if not os.path.exists("main_data.csv"):
    gdown.download(
        "https://drive.google.com/uc?id=1vYYxQdKuiqAMrzvyx_XkHjnZ-3KoMXnp",
        "main_data.csv"
    )
all_df = pd.read_csv("main_data.csv")
all_df["datetime"] = pd.to_datetime(all_df["datetime"]) 

# HELPER FUNCTION
def create_monthly_avg_df(df):
    monthly_avg = df.resample(rule='ME', on='datetime').agg({
        "PM2.5": "mean"
    }).reset_index()
    return monthly_avg

def create_hourly_avg_df(df):
    hourly_avg = df.groupby("hour")["PM2.5"].mean().reset_index()
    return hourly_avg

def create_category_df(df):
    category_df = df["air_quality_category"].value_counts().reset_index()
    category_df.columns = ["kategori", "jumlah"]
    return category_df

def create_seasonal_df(df):
    seasonal_df = df.groupby("season")["PM2.5"].mean().reset_index()
    return seasonal_df

# SIDEBAR FILTER
min_date = all_df["datetime"].min().date()
max_date = all_df["datetime"].max().date()

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    station = st.selectbox("Pilih Lokasi", all_df["station"].unique())

# FILTER DATA
main_df = all_df[
    (all_df["datetime"] >= pd.to_datetime(start_date)) &
    (all_df["datetime"] <= pd.to_datetime(end_date)) &
    (all_df["station"] == station)
]

monthly_avg_df = create_monthly_avg_df(main_df)
hourly_avg_df  = create_hourly_avg_df(main_df)
category_df    = create_category_df(main_df)
seasonal_df    = create_seasonal_df(main_df)

# DASHBOARD
st.header("Air Quality Dashboard")

# METRIC CARDS
col1, col2, col3 = st.columns(3)
with col1:
    avg_pm = round(main_df["PM2.5"].mean(), 2)
    st.metric("Rata-rata PM2.5", value=avg_pm)
with col2:
    max_pm = round(main_df["PM2.5"].max(), 2)
    st.metric("PM2.5 Tertinggi", value=max_pm)
with col3:
    min_pm = round(main_df["PM2.5"].min(), 2)
    st.metric("PM2.5 Terendah", value=min_pm)

# 1. TREND KUALITAS UDARA
st.subheader("Trend Kualitas Udara")

fig, ax = plt.subplots(figsize=(16, 5))
ax.plot(
    monthly_avg_df["datetime"],
    monthly_avg_df["PM2.5"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.set_xlabel("Bulan")
ax.set_ylabel("Rata-rata PM2.5")
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)

# 2. DISTRIBUSI
st.subheader("Distribusi Kualitas Udara")

fig, ax = plt.subplots(figsize=(10, 4))
sns.histplot(main_df["PM2.5"], bins=50, ax=ax, color="#90CAF9")
ax.set_xlabel("PM2.5")
ax.set_ylabel("Frekuensi")
st.pyplot(fig)

# 3. HUBUNGAN FAKTOR
st.subheader("Hubungan Antar Faktor")

fig, ax = plt.subplots(figsize=(10,6))
sns.heatmap(
    main_df[["PM2.5","TEMP","WSPM","NO2","CO"]].corr(),
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    ax=ax
)
st.pyplot(fig)

# 4. KATEGORI UDARA
st.subheader("Kategori Kualitas Udara")

fig, ax = plt.subplots(figsize=(8, 4))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="kategori",
    y="jumlah",
    data=category_df.sort_values("jumlah", ascending=False),
    palette=colors,
    ax=ax
)
ax.set_xlabel(None)
ax.set_ylabel("Jumlah")
st.pyplot(fig)

# 5. PERBANDINGAN LOKASI
st.subheader("Perbandingan Antar Lokasi")

fig, ax = plt.subplots(figsize=(14, 5))
sns.boxplot(data=all_df, x="station", y="PM2.5", ax=ax, color="#90CAF9")
ax.tick_params(axis='x', rotation=45)
ax.set_xlabel(None)
st.pyplot(fig)

# 6. POLA BERDASARKAN JAM
st.subheader("Pola Kualitas Udara Berdasarkan Jam")

fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(
    hourly_avg_df["hour"],
    hourly_avg_df["PM2.5"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.set_xlabel("Jam")
ax.set_ylabel("Rata-rata PM2.5")
ax.set_xticks(range(0, 24))
st.pyplot(fig)

# 7. SEASONAL ANALYSIS
st.subheader("Analisis Musiman")

fig, ax = plt.subplots(figsize=(8, 4))
sns.boxplot(data=main_df, x="season", y="PM2.5", ax=ax, color="#90CAF9")
ax.set_xlabel("Musim")
ax.set_ylabel("PM2.5")
st.pyplot(fig)

# FOOTER
st.caption("Zahra Ismaya © 2026")

