# --- 2. FITUR PENDAFTARAN & AMBIL LOKASI ---
st.sidebar.header("📝 Pendaftaran Member Online")

# Input Data Member
nama_user = st.sidebar.text_input("Nama Lengkap:")
status_user = st.sidebar.selectbox("Status:", ["Member", "Prospek"])

# Logika kolom NRA: Hanya muncul jika pilih 'Member'
nra_user = ""
if status_user == "Member":
    nra_user = st.sidebar.text_input("Masukkan NRA (Nomor Register Anggota):")

# Fungsi mengambil GPS dari Browser
loc = get_geolocation()

if loc:
    lat = loc['coords']['latitude']
    lon = loc['coords']['longitude']
    
    st.sidebar.success("📍 GPS Terdeteksi")
    
    # Tombol untuk Submit/Online
    if st.sidebar.button("Go Online 🏍️"):
        if nama_user:
            # Jika Member, wajib isi NRA. Jika Prospek, langsung lolos.
            if status_user == "Member" and not nra_user:
                st.sidebar.error("NRA wajib diisi untuk Member!")
            else:
                # Simpan data lengkap ke Firebase
                ref = db.reference(f'members/{nama_user}')
                ref.set({
                    'nama': nama_user,
                    'status_keanggotaan': status_user,
                    'nra': nra_user if status_user == "Member" else "N/A",
                    'lat': lat,
                    'lon': lon,
                    'update_terakhir': str(pd.Timestamp.now()) # Perlu import pandas as pd
                })
                st.sidebar.balloons()
                st.sidebar.success(f"Selamat berkendara, {nama_user}!")
        else:
            st.sidebar.error("Nama tidak boleh kosong!")
else:
    st.sidebar.warning("Silakan klik 'Allow' pada izin lokasi browser.")