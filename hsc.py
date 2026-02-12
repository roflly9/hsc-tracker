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

# Ambil Lokasi GPS
loc = get_geolocation()

# DEBUG: Hapus baris ini jika sudah berhasil
# st.write("Data GPS dari Browser:", loc) 

if loc and 'coords' in loc:
    lat_saya = loc['coords']['latitude']
    lon_saya = loc['coords']['longitude']
    st.sidebar.success(f"✅ GPS OK: {lat_saya:.4f}, {lon_saya:.4f}")
    
    if st.sidebar.button("Go Online 🏍️"):
        if nama_user:
            try:
                # Mengirim data langsung ke folder 'members'
                db.reference('members').child(nama_user).set({
                    'nama': nama_user,
                    'status': status_user,
                    'nra': nra_user,
                    'lat': lat_saya,
                    'lon': lon_saya,
                    'waktu': pd.Timestamp.now(tz='Asia/Jakarta').strftime('%H:%M:%S')
                })
                st.sidebar.balloons()
                st.sidebar.success("BERHASIL! Cek Firebase sekarang.")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Gagal kirim ke Firebase: {e}")
        else:
            st.sidebar.error("Isi Nama dulu!")
else:
    st.sidebar.warning("⌛ Menunggu GPS... Pastikan izin Lokasi di HP AKTIF.")
    lat_saya, lon_saya = -6.2000, 106.8166 # Default Jakarta