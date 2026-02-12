import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from streamlit_js_eval import get_geolocation
from firebase_admin import db, credentials, initialize_app, _apps
from streamlit_autorefresh import st_autorefresh

# --- 1. KONEKSI DATABASE ---
database_url = "https://biker-tacker-default-rtdb.asia-southeast1.firebasedatabase.app/"

if not _apps:
    initialize_app(options={'databaseURL': database_url})

st.set_page_config(page_title="HSC Radar", layout="wide")
st_autorefresh(interval=30000, key="datarefresh") # Refresh tiap 30 detik

st.title("🏍️ Radar Real-Time Komunitas HSC")

# --- 2. SIDEBAR PENDAFTARAN ---
st.sidebar.header("📝 Status Anda")
nama_user = st.sidebar.text_input("Nama Lengkap:")
status_user = st.sidebar.selectbox("Status:", ["Member", "Prospek"])
nra_user = st.sidebar.text_input("NRA:") if status_user == "Member" else "N/A"

loc = get_geolocation()
lat_saya, lon_saya = -6.2000, 106.8166 # Default Jakarta jika GPS mati

if loc and 'coords' in loc:
    lat_saya = loc['coords']['latitude']
    lon_saya = loc['coords']['longitude']
    
    if st.sidebar.button("Go Online 🏍️"):
        if nama_user:
            ref = db.reference(f'members/{nama_user}')
            ref.set({
                'nama': nama_user,
                'status': status_user,
                'nra': nra_user,
                'lat': lat_saya,
                'lon': lon_saya,
                'waktu': str(pd.Timestamp.now(tz='Asia/Jakarta'))
            })
            st.sidebar.success(f"Kamu sedang Online!")
        else:
            st.sidebar.error("Isi nama dulu!")

# --- 3. TAMPILAN PETA ALA OJOL ---
st.subheader("Peta Pantauan Member (Live)")

# Ambil semua data dari Firebase
ref_map = db.reference('members')
semua_member = ref_map.get()

# Buat Base Map (Menggunakan Google Maps Hybrid Style via Folium)
m = folium.Map(location=[lat_saya, lon_saya], zoom_start=12, tiles='OpenStreetMap')

# Tambahkan Marker untuk setiap member yang ada di database
if semua_member:
    for nama, info in semua_member.items():
        if 'lat' in info and 'lon' in info:
            # Tentukan warna: Member = Merah, Prospek = Biru
            warna = 'red' if info.get('status') == 'Member' else 'blue'
            
            # Isi teks saat marker diklik (Popup)
            isi_popup = f"""
                <b>{info['nama']}</b><br>
                Status: {info['status']}<br>
                NRA: {info['nra']}<br>
                Update: {info.get('waktu', 'N/A')}
            """
            
            folium.Marker(
                location=[info['lat'], info['lon']],
                popup=folium.Popup(isi_popup, max_width=300),
                tooltip=info['nama'],
                icon=folium.Icon(color=warna, icon='motorcycle', prefix='fa')
            ).add_to(m)

# Tampilkan Peta di Streamlit
folium_static(m, width=1000, height=500)