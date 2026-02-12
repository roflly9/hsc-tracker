import streamlit as st
from streamlit_js_eval import get_geolocation
from streamlit_folium import folium_static
import folium
from firebase_admin import db, credentials, initialize_app, _apps

# --- CONFIG DATABASE ---
database_url = "ISI_DENGAN_URL_FIREBASE_KAMU"

if not _apps:
    initialize_app(options={'databaseURL': database_url})

st.set_page_config(page_title="Radar Komunitas Motor", layout="wide")
st.title("🏍️ Radar Real-Time Member")

# --- FITUR 1: AMBIL LOKASI HP OTOMATIS ---
st.sidebar.header("Status Lokasi Kamu")
loc = get_geolocation()

if loc:
    lat = loc['coords']['latitude']
    lon = loc['coords']['longitude']
    
    st.sidebar.success(f"GPS Terdeteksi!")
    nama_member = st.sidebar.text_input("Masukkan Nama Kamu untuk Online:", key="nama")
    
    if nama_member:
        # Kirim data ke Firebase otomatis
        ref = db.reference(f'members/{nama_member}')
        ref.set({
            'lat': lat,
            'lon': lon,
            'status': 'Aktif'
        })
        st.sidebar.info(f"Halo {nama_member}, posisimu terpantau rekan lain.")
else:
    st.sidebar.warning("Silakan aktifkan GPS dan izinkan browser mengakses lokasi.")

# --- FITUR 2: TAMPILKAN RADAR ---
ref = db.reference('members')
all_members = ref.get()

# Titik tengah peta (bisa disesuaikan atau ambil dari posisi user terakhir)
center_lat = -6.2000
center_lon = 106.8166

m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

if all_members:
    for nama, info in all_members.items():
        # Tambahkan marker tiap member
        icon_color = "blue" if nama != nama_member else "red"
        folium.Marker(
            [info['lat'], info['lon']],
            popup=f"Member: {nama}",
            tooltip=nama,
            icon=folium.Icon(color=icon_color, icon='motorcycle', prefix='fa')
        ).add_to(m)

folium_static(m, width=700)