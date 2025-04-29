import streamlit as st
from datetime import datetime
import pandas as pd

# === Data Awal ===

diagnoses = {
    "P01": "Pseudomonas Hydrophylla",
    "P02": "Bintik Putih (White Spot)",
    "P03": "Trematoda",
    "P04": "Lernea Sp"
}

evidence = {
    "G01": "Borok pada Kulit",
    "G02": "Pendarahan pada Kulit",
    "G03": "Lemah",
    "G04": "Kurus",
    "G05": "Nafsu Makan Hilang",
    "G06": "Kulit Gelap",
    "G07": "Kulit Kasar",
    "G08": "Susah Bernapas",
    "G09": "Infeksi Kulit Kepala, Badan Belakang, Insang, dan Sirip",
    "G10": "Pendarahan pada Daging"
}

base_knowledge = {
    "G01": {"diagnoses": ["P01", "P04"], "densitas": 0.82},
    "G02": {"diagnoses": ["P01", "P02", "P04"], "densitas": 0.73},
    "G03": {"diagnoses": ["P01", "P02"], "densitas": 0.85},
    "G04": {"diagnoses": ["P01"], "densitas": 0.78},
    "G05": {"diagnoses": ["P01", "P03"], "densitas": 0.70},
    "G06": {"diagnoses": ["P02"], "densitas": 0.82},
    "G07": {"diagnoses": ["P02"], "densitas": 0.87},
    "G08": {"diagnoses": ["P02"], "densitas": 0.76},
    "G09": {"diagnoses": ["P03"], "densitas": 0.73},
    "G10": {"diagnoses": ["P04"], "densitas": 0.88}
}

treatment_suggestions = {
    "P01": "Pengobatan dengan antibiotik untuk infeksi bakteri.",
    "P02": "Perawatan dengan garam untuk mengurangi infeksi dan meningkatkan kekebalan.",
    "P03": "Pemberian obat cacing dan meningkatkan kualitas air.",
    "P04": "Pemakaian obat eksternal untuk mengatasi infeksi parasit."
}

# === Fungsi Kombinasi Dempster-Shafer ===

def combine_mass(m1, m2):
    combined = {}
    conflict = 0.0

    for h1, v1 in m1.items():
        for h2, v2 in m2.items():
            if h1 == ("Theta",):
                intersection = h2
            elif h2 == ("Theta",):
                intersection = h1
            else:
                intersection = tuple(sorted(set(h1).intersection(set(h2))))

            if not intersection:
                conflict += v1 * v2
            else:
                combined[intersection] = combined.get(intersection, 0) + v1 * v2

    if conflict != 1:
        for key in combined:
            combined[key] = combined[key] / (1 - conflict)

    return combined

# === Fungsi Inferensi ===

def dempster_shafer_inference(evidence_list, base_knowledge):
    mass_functions = []

    for gejala in evidence_list:
        if gejala in base_knowledge:
            data = base_knowledge[gejala]
            diagnoses_list = data["diagnoses"]
            density = data["densitas"]

            mass = {}
            diagnoses_tuple = tuple(sorted(diagnoses_list))
            mass[diagnoses_tuple] = density
            mass[("Theta",)] = 1 - density

            mass_functions.append(mass)

    if not mass_functions:
        return {}

    current_mass = mass_functions[0]
    for next_mass in mass_functions[1:]:
        current_mass = combine_mass(current_mass, next_mass)

    return current_mass

# === Riwayat Diagnosa ===

if "riwayat" not in st.session_state:
    st.session_state.riwayat = []

# === Sidebar Navigasi ===

menu = st.sidebar.radio("Pilihan Menu", ["🏠 Beranda", "🧪 Diagnosa", "📋 Riwayat Diagnosa", "📖 Tentang Penyakit"])

# === Halaman Beranda ===

if menu == "🏠 Beranda":
    st.title("🏠 Selamat Datang di FishShiel AI")
    
    st.write("""
        **FishShield AI** adalah sebuah sistem berbasis kecerdasan buatan (AI) yang dirancang untuk mendiagnosis dan mengidentifikasi penyakit pada ikan lele secara akurat dan efisien. Menggunakan metode *Dempster-Shafer*, sistem ini menggabungkan data gejala yang diamati pada ikan dengan basis pengetahuan mengenai penyakit ikan untuk memberikan prediksi yang lebih tepat. FishShield AI tidak hanya membantu para petani ikan dalam mendeteksi penyakit dengan cepat, tetapi juga menyediakan rekomendasi pengobatan yang dapat dilakukan untuk mencegah kerugian yang lebih besar. Dengan adanya fitur seperti riwayat diagnosa dan saran pengobatan, sistem ini dapat membantu meningkatkan keberlanjutan dan produktivitas dalam budidaya ikan lele, serta memberikan kontribusi pada kualitas hidup ikan yang lebih baik.
        
        Silakan pilih menu **🧪 Diagnosa** di sebelah kiri untuk memulai analisis.
    """)

# === Halaman Diagnosa ===

elif menu == "🧪 Diagnosa":
    st.title("🧪 Diagnosa Penyakit Ikan Lele")
    st.write("Silakan pilih gejala yang dialami ikan lele Anda:")

    selected_gejala = []
    with st.form("gejala_form"):
        for kode, desc in evidence.items():
            if st.checkbox(f"{kode} - {desc}"):
                selected_gejala.append(kode)

        submitted = st.form_submit_button("Diagnosa")

    if submitted:
        if not selected_gejala:
            st.warning("Silakan pilih minimal satu gejala.")
        else:
            hasil = dempster_shafer_inference(selected_gejala, base_knowledge)

            st.subheader("🩺 Hasil Diagnosa:")
            if hasil:
                # Menyusun data hasil diagnosa ke dalam tabel
                diagnosa_data = []
                sorted_hasil = sorted(hasil.items(), key=lambda x: x[1], reverse=True)

                # Cek apakah semua belief = 0 atau hanya Theta yang ada
                only_theta = all(hipotesis == ("Theta",) or belief == 0 for hipotesis, belief in sorted_hasil)

                if only_theta:
                    diagnosa_data.append({
                        "Nama Penyakit": "-",
                        "Persentase": "-",
                        "Keterangan": "Tidak ada penyakit terdeteksi",
                        "Ketidakpastian": "-",
                        "Saran Pengobatan": "-"
                    })
                else:
                    for hipotesis, belief in sorted_hasil:
                        if hipotesis == ("Theta",) or belief == 0:
                            continue  # Lewati Theta dan penyakit dengan belief 0

                        belief_percentage = belief * 100
                        nama = " atau ".join(diagnoses.get(h, h) for h in hipotesis)
                        treatment = treatment_suggestions.get(hipotesis[0], "Saran pengobatan tidak tersedia.")
                        keterangan = (
                            "Ringan" if belief_percentage <= 40 else
                            "Sedang" if belief_percentage <= 60 else
                            "Berat" if belief_percentage <= 80 else
                            "Mati"
                        )
                        diagnosa_data.append({
                            "Nama Penyakit": nama,
                            "Persentase": f"{belief_percentage:.2f}%",
                            "Keterangan": keterangan,
                            "Ketidakpastian": f"{(100 - belief_percentage):.2f}%",
                            "Saran Pengobatan": treatment
                        })


                df = pd.DataFrame(diagnosa_data)
                st.write(df)
                
                # Menyimpan riwayat diagnosa
                waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.riwayat.append({
                    "waktu": waktu,
                    "gejala": selected_gejala,
                    "hasil": df.to_dict(orient="records")
                })
            else:
                st.info("Tidak ada hasil inferensi ditemukan.")

# === Halaman Riwayat Diagnosa ===

elif menu == "📋 Riwayat Diagnosa":
    st.title("📋 Riwayat Diagnosa")
    if st.session_state.riwayat:
        for i, data in enumerate(reversed(st.session_state.riwayat), 1):
            st.markdown(f"### Diagnosa ke-{i}")
            st.markdown(f"- 🕒 Waktu: `{data['waktu']}`")
            st.markdown(f"- 🔍 Gejala: {', '.join(evidence[g] for g in data['gejala'])}")
            st.markdown(f"- 💡 Hasil: ")
            
            # Menampilkan hasil dalam tabel riwayat
            df_riwayat = pd.DataFrame(data['hasil'])
            st.write(df_riwayat)
            st.markdown("---")
    else:
        st.info("Belum ada riwayat diagnosa.")

# === Halaman Tentang Penyakit ===

elif menu == "📖 Tentang Penyakit":
    st.title("📖 Tentang Penyakit Ikan Lele")

    st.subheader("1. Pseudomonas Hydrophylla")
    st.markdown("""
    Merupakan penyakit bakteri yang menyebabkan borok, pendarahan, dan pembusukan jaringan pada ikan.
    Disebabkan oleh bakteri *Pseudomonas hydrophila* yang menyerang saat kondisi air buruk dan stres tinggi pada ikan.
    """)

    st.subheader("2. White Spot (Bintik Putih)")
    st.markdown("""
    Disebabkan oleh parasit protozoa *Ichthyophthirius multifiliis*. Gejalanya berupa bintik-bintik putih pada kulit, sirip, dan insang.
    Umumnya muncul karena suhu air yang rendah dan sanitasi kolam yang buruk.
    """)

    st.subheader("3. Trematoda")
    st.markdown("""
    Infeksi oleh cacing pipih parasit yang menyerang kulit, insang, atau organ dalam ikan.
    Menyebabkan iritasi, luka, serta penurunan nafsu makan dan pertumbuhan ikan.
    """)

    st.subheader("4. Lernea sp (Cacing Jangkar)")
    st.markdown("""
    Parasit berbentuk seperti jangkar yang menempel di tubuh ikan, menyebabkan luka terbuka dan infeksi sekunder.
    Penularannya terjadi di kolam yang tidak steril dan padat tebar tinggi.
    """)
