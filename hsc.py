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
st_autorefresh(interval=30000, key="datarefresh") # Auto-update peta tiap 30 detik

st.title("🏍️ Radar Real-Time Komunitas HSC")

# --- 2. SIDEBAR PENDAFTARAN ---
st.sidebar.header("📝 Status Anda")
nama_user = st.sidebar.text_input("Nama Lengkap:")
status_user = st.sidebar.selectbox("Status:", ["Member", "Prospek"])

# Logika NRA: Muncul hanya jika memilih 'Member'
nra_user = "N/A"
if status_user == "Member":
    nra_user = st.sidebar.text_input("NRA (Nomor Register Anggota):")

# Ambil Lokasi GPS
loc = get_geolocation()
lat_saya, lon_saya = -6.2000, 106.8166 # Lokasi cadangan (Jakarta)

if loc and 'coords' in loc:
    lat_saya = loc['coords']['latitude']
    lon_saya = loc['coords']['longitude']
    st.sidebar.success("✅ GPS Terdeteksi")
    
    # Tombol Go Online (Cukup Satu Kali Saja)
    if st.sidebar.button("Go Online 🏍️"):
        if nama_user:
            if status_user == "Member" and not nra_user:
                st.sidebar.error("NRA wajib diisi untuk Member!")
            else:
                # Kirim ke Firebase menggunakan .set() agar pasti terupdate
                db.reference('members').child(nama_user).set({
                    'nama': nama_user,
                    'status': status_user,
                    'nra': nra_user,
                    'lat': lat_saya,
                    'lon': lon_saya,
                    'waktu': pd.Timestamp.now(tz='Asia/Jakarta').strftime('%H:%M:%S')
                })
                st.sidebar.balloons()
                st.sidebar.success(f"Berhasil! Kamu terpantau di radar.")
                st.rerun() # Refresh peta agar marker langsung muncul
        else:
            st.sidebar.error("Silakan isi nama lengkap!")
else:
    st.sidebar.warning("⌛ Menunggu GPS... Klik 'Allow' di browser.")

# --- 3. TAMPILKAN PETA (LOGIKA OJOL) ---
st.subheader("Peta Pantauan Member (Live)")

# Ambil data terbaru dari Firebase
semua_member = db.reference('members').get()

# Buat Map dasar
m = folium.Map(location=[lat_saya, lon_saya], zoom_start=12)

# Tambahkan Marker jika ada member di database
if semua_member:
    for key, info in semua_member.items():
        if isinstance(info, dict) and 'lat' in info and 'lon' in info:
            # Warna: Member Merah, Prospek Biru
            warna = 'red' if info.get('status') == 'Member' else 'blue'
            
            folium.Marker(
                location=[info['lat'], info['lon']],
                popup=folium.Popup(f"<b>{info['nama']}</b><br>NRA: {info['nra']}<br>Jam: {info['waktu']}", max_width=200),
                tooltip=f"{info['nama']} ({info['status']})",
                icon=folium.Icon(color=warna, icon='motorcycle', prefix='fa')
            ).add_to(m)

# Tampilkan peta ke web
folium_static(m, width=1000, height=500)