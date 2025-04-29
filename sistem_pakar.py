# Knowledge Base

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
                if intersection in combined:
                    combined[intersection] += v1 * v2
                else:
                    combined[intersection] = v1 * v2

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


# ======= Streamlit App =======

import streamlit as st

st.title("🧪 Sistem Pakar Diagnosa Penyakit Ikan Lele")
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
            sorted_hasil = sorted(hasil.items(), key=lambda x: x[1], reverse=True)
            for hipotesis, belief in sorted_hasil:
                if hipotesis == ("Theta",):
                    st.markdown(f"**Ketidakpastian (Θ):** `{belief:.4f}`")
                else:
                    nama = " atau ".join(diagnoses.get(h, h) for h in hipotesis)
                    st.markdown(f"**{nama}:** `{belief:.4f}`")
        else:
            st.info("Tidak ada hasil inferensi ditemukan.")