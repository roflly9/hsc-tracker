import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from streamlit_js_eval import get_geolocation
from firebase_admin import db, credentials, initialize_app, _apps
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG DATABASE ---
# Pastikan URL ini benar-benar lengkap seperti di bawah
database_url = "https://biker-tacker-default-rtdb.asia-southeast1.firebasedatabase.app/"

if not _apps:
    initialize_app(options={'databaseURL': database_url})

# Set konfigurasi halaman (Harus di bagian atas)
st.set_page_config(page_title="HSC Radar", layout="wide")

# Auto-refresh tiap 30 detik
st_autorefresh(interval=30000, key="datarefresh")

st.title("🏍️ Radar Real-Time Komunitas HSC")

# --- 2. FITUR PENDAFTARAN (SIDEBAR) ---
st.sidebar.header("📝 Pendaftaran Member Online")

nama_user = st.sidebar.text_input("Nama Lengkap:")
status_user = st.sidebar.selectbox("Status:", ["Member", "Prospek"])

nra_user = ""
if status_user == "Member":
    nra_user = st.sidebar.text_input("Masukkan NRA (Nomor Register Anggota):")

# Tombol untuk kirim lokasi
loc = get_geolocation()

if loc:
    lat = loc['coords']['latitude']
    lon = loc['coords']['longitude']
    st.sidebar.success("📍 GPS Terdeteksi")
    
    if st.sidebar.button("Go Online 🏍️"):
        if nama_user:
            if status_user == "Member" and not nra_user:
                st.sidebar.error("NRA wajib diisi!")
            else:
                # Simpan ke Firebase
                ref = db.reference(f'members/{nama_user}')
                ref.set({
                    'nama': nama_user,
                    'status': status_user,
                    'nra': nra_user if status_user == "Member" else "N/A",
                    'lat': lat,
                    'lon': lon,
                    'waktu': str(pd.Timestamp.now(tz='Asia/Jakarta'))
                })
                st.sidebar.balloons()
                st.sidebar.success(f"Gaspol, {nama_user}!")
        else:
            st.sidebar.error("Nama harus diisi!")
else:
    st.sidebar.warning("Tunggu GPS / Klik 'Allow' di browser HP.")

# --- 3. TAMPILKAN PETA ---
st.subheader("Peta Pantauan Member")

ref = db.reference('members')
data_members = ref.get()

# Gunakan lokasi user sebagai pusat peta, jika tidak ada pakai Jakarta
center_lat = lat if loc else -6.2000
center_lon = lon if loc else 106.8166

m = folium.Map(location=[center_lat, center_lon], zoom_start=13)

if data_members:
    for nama, info in data_members.items():
        # Member = Merah, Prospek = Biru
        warna = "red" if info.get('status') == "Member" else "blue"
        folium.Marker(
            [info['lat'], info['lon']],
            popup=f"{nama} ({info.get('status')})",
            tooltip=nama,
            icon=folium.Icon(color=warna, icon='motorcycle', prefix='fa')
        ).add_to(m)

folium_static(m, width=1000)