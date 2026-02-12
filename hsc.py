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
st_autorefresh(interval=30000, key="datarefresh")

st.title("🏍️ Radar Real-Time Komunitas HSC")

# --- 2. SIDEBAR STATUS ---
st.sidebar.header("📝 Status Anda")
nama_user = st.sidebar.text_input("Nama Lengkap:")
status_user = st.sidebar.selectbox("Status:", ["Member", "Prospek"])
nra_user = st.sidebar.text_input("NRA:") if status_user == "Member" else "N/A"

# Deteksi GPS
loc = get_geolocation()
lat_saya, lon_saya = -6.2000, 106.8166 # Lokasi cadangan

if loc and 'coords' in loc:
    lat_saya = loc['coords']['latitude']
    lon_saya = loc['coords']['longitude']
    st.sidebar.success("✅ GPS Terdeteksi")
    
    if st.sidebar.button("Go Online 🏍️"):
        if nama_user:
            # Menggunakan child().set() untuk memastikan data masuk/terupdate
            db.reference('members').child(nama_user).set({
                'nama': nama_user,
                'status': status_user,
                'nra': nra_user,
                'lat': lat_saya,
                'lon': lon_saya,
                'waktu': pd.Timestamp.now(tz='Asia/Jakarta').strftime('%H:%M:%S')
            })
            st.sidebar.balloons()
            st.sidebar.success(f"Berhasil Online!")
            st.rerun()
        else:
            st.sidebar.error("Isi Nama dulu!")
else:
    st.sidebar.warning("⌛ Menunggu GPS... Pastikan klik 'Allow' di browser.")

# --- 3. TAMPILKAN PETA ---
st.subheader("Peta Pantauan Member")
semua_member = db.reference('members').get()
m = folium.Map(location=[lat_saya, lon_saya], zoom_start=12)

if semua_member:
    for key, info in semua_member.items():
        if isinstance(info, dict) and 'lat' in info:
            warna = 'red' if info.get('status') == 'Member' else 'blue'
            folium.Marker(
                location=[info['lat'], info['lon']],
                popup=f"<b>{info['nama']}</b><br>NRA: {info['nra']}",
                icon=folium.Icon(color=warna, icon='motorcycle', prefix='fa')
            ).add_to(m)

folium_static(m, width=1000, height=500)