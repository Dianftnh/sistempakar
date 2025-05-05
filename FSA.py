import streamlit as st
import pandas as pd
from datetime import datetime

# Import dari file inference
from sistem_pakar import diagnoses, evidence, base_knowledge, dempster_shafer_inference, belief, plausibility

# Riwayat diagnosa disimpan di session
if "riwayat" not in st.session_state:
    st.session_state.riwayat = []

st.title("🐟 Diagnosa Penyakit Ikan - FishShiel AI")

menu = st.sidebar.selectbox("Menu", ["Beranda", "Diagnosa", "Riwayat"])

if menu == "Beranda":
    st.header("Selamat Datang di FishShiel AI")
    st.write("""
    Aplikasi ini menggunakan metode Dempster-Shafer untuk mendiagnosa penyakit pada ikan lele berdasarkan gejala yang dipilih.
    """)

elif menu == "Diagnosa":
    st.header("🧪 Diagnosa Penyakit")
    selected_gejala = []

    with st.form("form_gejala"):
        for kode, deskripsi in evidence.items():
            if st.checkbox(f"{kode} - {deskripsi}"):
                selected_gejala.append(kode)
        submit = st.form_submit_button("Diagnosa Sekarang")

    if submit:
        if not selected_gejala:
            st.warning("Silakan pilih minimal satu gejala.")
        else:
            hasil_mass = dempster_shafer_inference(selected_gejala, base_knowledge)

            data_hasil = []
            for kode, nama in diagnoses.items():
                bel = belief([kode], hasil_mass)
                pl = plausibility([kode], hasil_mass)
                ignoransi = pl - bel
                if bel > 0:
                    data_hasil.append({
                        "Penyakit": nama,
                        "Belief (%)": f"{bel*100:.2f}",
                        "Plausibility (%)": f"{pl*100:.2f}",
                        "Ignoransi (%)": f"{ignoransi*100:.2f}"
                    })

            if data_hasil:
                df = pd.DataFrame(data_hasil).sort_values(by="Belief (%)", ascending=False)
                st.subheader("📋 Hasil Diagnosa")
                st.dataframe(df)

                waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.riwayat.append({
                    "waktu": waktu,
                    "gejala": selected_gejala,
                    "hasil": df
                })
            else:
                st.info("Tidak ditemukan hasil yang relevan berdasarkan gejala yang dipilih.")

elif menu == "Riwayat":
    st.header("📋 Riwayat Diagnosa")
    if st.session_state.riwayat:
        for i, item in enumerate(reversed(st.session_state.riwayat), 1):
            st.markdown(f"### Diagnosa ke-{i}")
            st.markdown(f"🕒 {item['waktu']}")
            st.markdown(f"🔍 Gejala: {', '.join(evidence[g] for g in item['gejala'])}")
            st.dataframe(item["hasil"])
            st.markdown("---")
    else:
        st.info("Belum ada riwayat diagnosa.")
