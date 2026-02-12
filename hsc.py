import streamlit as st
from streamlit_js_eval import get_geolocation
from streamlit_folium import folium_static
import folium
from firebase_admin import db, credentials, initialize_app, _apps
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG DATABASE (URL KAMU) ---
# Pastikan URL diakhiri dengan tanda miring /
database_url = "https://biker-tacker-default-rtdb.asia-southeast1.firebasedatabase.app/"

if not _apps:
    initialize_app(options={'databaseURL': database_url})

# Set halaman agar tampil penuh
st.set_page_config(page_title="HSC Radar", layout="wide")

# Refresh otomatis setiap 20 detik agar posisi member lain terupdate
st_autorefresh(interval=20000, key="datarefresh")

st.title("🏍️ Radar Real-Time Komunitas HSC")

# --- 2. FITUR AMBIL LOKASI OTOMATIS ---
st.sidebar.header("📍 Status Lokasi Kamu")
nama_member = st.sidebar.text_input("Masukkan Nama Member/Prospek:")

# Fungsi mengambil GPS dari Browser HP
loc = get_geolocation()

if loc:
    lat = loc['coords']['latitude']
    lon = loc['coords']['longitude']
    
    st.sidebar.success(f"GPS Aktif")
    
    if nama_member:
        # Simpan/Update ke Firebase
        ref = db.reference(f'members/{nama_member}')
        ref.set({
            'lat': lat,
            'lon': lon,
            'status': 'Online',
            'last_seen': st.session_state.get('datarefresh', 0)
        })
        st.sidebar.info(f"Halo {nama_member}, posisimu terbagi!")
    else:
        st.sidebar.warning("Isi nama agar rekan lain bisa melihatmu.")
else:
    st.sidebar.error("Klik 'Allow/Izinkan' GPS pada browser HP kamu.")

# --- 3. TAMPILKAN RADAR MAP ---
st.subheader("Peta Pantauan Member")

# Ambil data semua member dari Firebase
ref = db.reference('members')
data_members = ref.get()

# Titik awal peta (Default ke lokasi user jika ada, jika tidak ke Jakarta)
start_lat = lat if loc else -6.2000
start_lon = lon if loc else 106.8166

m = folium.Map(location=[start_lat, start_lon], zoom_start=13)

if data_members:
    for nama, info in data_members.items():
        # Bedakan warna marker kita dengan orang lain
        warna = "red" if nama == nama_member else "blue"
        
        folium.Marker(
            [info['lat'], info['lon']],
            popup=f"Member: {nama}",
            tooltip=nama,
            icon=folium.Icon(color=warna, icon='motorcycle', prefix='fa')
        ).add_to(m)

folium_static(m, width=1000)

# --- 4. DAFTAR MEMBER ONLINE ---
with st.expander("Lihat Daftar Member Online"):
    if data_members:
        for nama in data_members.keys():
            st.write(f"✅ {nama}")
    else:
        st.write("Belum ada member online.")