import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Airbnb NYC EDA",
    page_icon="✈️",
    layout="wide"
)

st.title("🗽 Airbnb NYC 2019: Data Exploratory")
st.markdown("Dashboard interaktif untuk menganalisis harga dan sebaran properti Airbnb di New York City.")
# 2. Load Data (dengan Caching agar cepat)
@st.cache_data
def load_data():
    df = pd.read_csv("AB_NYC_2019.csv")
    # Sedikit data cleaning
    df.drop(['id', 'host_name', 'last_review'], axis=1, inplace=True)
    df = df[df['price'] > 0] # Hapus harga 0 (error data)
    return df

df = load_data()
# 3. Sidebar untuk Filter
st.sidebar.header("Filter Data")

# Filter Neighbourhood Group (Multiselect)
all_groups = sorted(df['neighbourhood_group'].unique())
selected_groups = st.sidebar.multiselect("Pilih Wilayah:", all_groups, default=all_groups)

# Filter Room Type (Multiselect)
all_room_types = sorted(df['room_type'].unique())
selected_room_types = st.sidebar.multiselect("Tipe Ruangan:", all_room_types, default=all_room_types)

# Filter Harga (Slider)
min_price = int(df['price'].min())
max_price = int(df['price'].max())
# Kita batasi max slider di 1000 agar mudah digeser, meski data asli ada yang 10.000
price_range = st.sidebar.slider("Rentang Harga (USD):", min_price, 1000, (min_price, 500))

# Menerapkan Filter ke DataFrame
filtered_df = df[
    (df['neighbourhood_group'].isin(selected_groups)) &
    (df['room_type'].isin(selected_room_types)) &
    (df['price'].between(price_range[0], price_range[1]))
]

# 4. Menampilkan KPI Utama
st.subheader("📊 Key Metrics")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Listings", f"{filtered_df.shape[0]:,}")
with col2:
    avg_price = filtered_df['price'].mean()
    st.metric("Rata-rata Harga", f"${avg_price:.2f}")
with col3:
    total_reviews = filtered_df['number_of_reviews'].sum()
    st.metric("Total Reviews", f"{total_reviews:,}")

st.markdown("---")

# 5. Visualisasi Peta & Distribusi
col_map, col_chart = st.columns([2, 1]) # Rasio lebar 2:1

with col_map:
    st.subheader("📍 Peta Sebaran Properti")
    # Menggunakan mapbox style 'open-street-map' atau 'carto-positron' agar tidak perlu API Key
    fig_map = px.scatter_mapbox(
        filtered_df,
        lat="latitude",
        lon="longitude",
        color="price",
        size="number_of_reviews", # Ukuran titik berdasarkan popularitas
        color_continuous_scale=px.colors.cyclical.IceFire,
        size_max=15,
        zoom=10,
        mapbox_style="carto-positron",
        hover_name="name",
        hover_data={"neighbourhood": True, "price": True}
    )
    st.plotly_chart(fig_map, use_container_width=True)

with col_chart:
    st.subheader("💰 Distribusi Harga")
    fig_hist = px.histogram(
        filtered_df, 
        x="price", 
        nbins=30, 
        title="Frekuensi Harga Sewa",
        color_discrete_sequence=['#136F63'] # Warna Emerald
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# 6. Analisis Rata-rata Harga per Room Type
st.subheader("Compare: Harga Rata-rata per Tipe Ruangan")
avg_price_room = filtered_df.groupby('room_type')['price'].mean().reset_index()

fig_bar = px.bar(
    avg_price_room,
    x='room_type',
    y='price',
    color='room_type',
    text_auto='.2s',
    template="plotly_white",
    title="Rata-rata Harga (USD) per Kategori"
)
st.plotly_chart(fig_bar, use_container_width=True)

# Menampilkan Data Raw (Opsional - taruh di bawah/expander)
with st.expander("Lihat Data Mentah (Tabel)"):
    st.dataframe(filtered_df.head(100))
