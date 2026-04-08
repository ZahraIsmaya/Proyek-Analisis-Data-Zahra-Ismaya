import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import gdown
import os

sns.set(style='dark')

# ===================== LOAD DATA =====================
if not os.path.exists("main_data.csv"):
    gdown.download(
        "https://drive.google.com/uc?id=1BQBPKoqDFjdq2IfmkXepmn3RyyFmA0G6",
        "main_data.csv"
    )

all_df = pd.read_csv("main_data.csv")
all_df["datetime"] = pd.to_datetime(all_df["datetime"])

# ===================== EDA (WAJIB DI ATAS) =====================
all_df["year"] = all_df["datetime"].dt.year
all_df["month"] = all_df["datetime"].dt.month
all_df["hour"] = all_df["datetime"].dt.hour

all_df["air_quality_category"] = pd.cut(
    all_df["PM2.5"],
    bins=[0, 50, 100, 150, all_df["PM2.5"].max()],
    labels=["Baik", "Sedang", "Tidak Sehat", "Berbahaya"]
)

# ===================== HELPER =====================
def create_monthly_avg_df(df):
    return df.resample('ME', on='datetime')['PM2.5'].mean().reset_index()

def create_hourly_avg_df(df):
    return df.groupby("hour")["PM2.5"].mean().reset_index()

def create_category_df(df):
    cat = df["air_quality_category"].value_counts(normalize=True) * 100
    cat = cat.reset_index()
    cat.columns = ["kategori", "persentase"]
    return cat

def create_station_avg_df(df):
    return df.groupby("station")["PM2.5"].mean().sort_values().reset_index()

def create_extreme_df(df):
    extreme = df[df["PM2.5"] > 150]
    return extreme.groupby("year").size().reset_index(name="jumlah")

# ===================== SIDEBAR =====================
min_date = all_df["datetime"].min().date()
max_date = all_df["datetime"].max().date()

with st.sidebar:
    st.title("Filter")
    start_date, end_date = st.date_input(
        "Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# ===================== FILTER =====================
main_df = all_df[
    (all_df["datetime"] >= pd.to_datetime(start_date)) &
    (all_df["datetime"] <= pd.to_datetime(end_date))
]

monthly_avg_df = create_monthly_avg_df(main_df)
hourly_avg_df  = create_hourly_avg_df(main_df)
category_df    = create_category_df(main_df)
station_avg_df = create_station_avg_df(main_df)
extreme_df     = create_extreme_df(main_df)

# ===================== DASHBOARD =====================
st.title("Air Quality Dashboard (2013–2017)")

# ===================== METRIC =====================
col1, col2, col3 = st.columns(3)
col1.metric("Rata-rata PM2.5", round(main_df["PM2.5"].mean(),2))
col2.metric("PM2.5 Tertinggi", round(main_df["PM2.5"].max(),2))
col3.metric("PM2.5 Terendah", round(main_df["PM2.5"].min(),2))

# ==================================================
# 1. TREND PM2.5
# ==================================================
st.subheader("1. Tren PM2.5 (2013–2017)")

fig, ax = plt.subplots(figsize=(14,5))
ax.plot(monthly_avg_df["datetime"], monthly_avg_df["PM2.5"], marker='o')
ax.set_xlabel("Tahun")
ax.set_ylabel("PM2.5")
st.pyplot(fig)

# ==================================================
# 2. FAKTOR CUACA
# ==================================================
st.subheader("2. Pengaruh Faktor Cuaca")

fig, ax = plt.subplots(figsize=(8,5))
sns.heatmap(
    main_df[["PM2.5","TEMP","WSPM","DEWP","PRES"]].corr(),
    annot=True, cmap="coolwarm", ax=ax
)
st.pyplot(fig)

fig, ax = plt.subplots(figsize=(6,4))
sns.scatterplot(data=main_df, x="WSPM", y="PM2.5", alpha=0.3)
ax.set_title("PM2.5 vs Kecepatan Angin")
st.pyplot(fig)

# ==================================================
# 3. KATEGORI UDARA
# ==================================================
st.subheader("3. Persentase Kualitas Udara")

fig, ax = plt.subplots(figsize=(8,4))
sns.barplot(data=category_df, x="kategori", y="persentase", ax=ax)
ax.set_ylabel("Persentase (%)")
st.pyplot(fig)

# ==================================================
# 4. PERBANDINGAN LOKASI
# ==================================================
st.subheader("4. Perbandingan PM2.5 Antar Lokasi")

fig, ax = plt.subplots(figsize=(14,5))
sns.barplot(data=station_avg_df, x="station", y="PM2.5", ax=ax)
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)

fig, ax = plt.subplots(figsize=(14,5))
sns.boxplot(data=main_df, x="station", y="PM2.5", ax=ax)
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)

# ==================================================
# 5. POLA JAM
# ==================================================
st.subheader("5. Pola PM2.5 Berdasarkan Jam")

fig, ax = plt.subplots(figsize=(10,4))
ax.plot(hourly_avg_df["hour"], hourly_avg_df["PM2.5"], marker='o')
ax.set_xticks(range(0,24))
ax.set_xlabel("Jam")
ax.set_ylabel("PM2.5")
st.pyplot(fig)

# ==================================================
# 6. KEJADIAN EKSTREM
# ==================================================
st.subheader("6. Kejadian PM2.5 Ekstrem (>150)")

fig, ax = plt.subplots(figsize=(8,5))
sns.barplot(data=extreme_df, x="year", y="jumlah", ax=ax)
ax.set_ylabel("Jumlah Hari")
st.pyplot(fig)

# ===================== FOOTER =====================
st.caption("Zahra Ismaya © 2026")
