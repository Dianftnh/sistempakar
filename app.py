from flask import Flask, render_template, request

app = Flask(__name__)

# Data lengkap gejala, densitas, dan asosiasi penyakit
gejala = {
    "G01": {"nama": "Borok pada kulit", "densitas": 0.82, "penyakit": ["P01", "P04"]},
    "G02": {"nama": "Pendarahan pada kulit", "densitas": 0.73, "penyakit": ["P01", "P02", "P04"]},
    "G03": {"nama": "Lemah", "densitas": 0.85, "penyakit": ["P01", "P02"]},
    "G04": {"nama": "Kurus", "densitas": 0.78, "penyakit": ["P01"]},
    "G05": {"nama": "Nafsu makan hilang", "densitas": 0.70, "penyakit": ["P01", "P03"]},
    "G06": {"nama": "Kulit gelap", "densitas": 0.82, "penyakit": ["P02"]},
    "G07": {"nama": "Kulit kasar", "densitas": 0.87, "penyakit": ["P02"]},
    "G08": {"nama": "Susah bernapas", "densitas": 0.76, "penyakit": ["P02"]},
    "G09": {"nama": "Infeksi kulit kepala, badan belakang, insang dan sirip", "densitas": 0.73, "penyakit": ["P03"]},
    "G10": {"nama": "Pendarahan pada daging", "densitas": 0.88, "penyakit": []}
}

# Nama penyakit
penyakit_map = {
    "P01": "Pseudomonas hydrophylla",
    "P02": "White spot (Bintik putih)",
    "P03": "Trematoda",
    "P04": "Lernea sp"
}

@app.route('/', methods=['GET', 'POST'])
def index():
    hasil = None
    if request.method == 'POST':
        selected = request.form.getlist('gejala')
        hasil = hitung_dempster(selected)
    return render_template('index.html', gejala=gejala, hasil=hasil, penyakit_map=penyakit_map)

def hitung_dempster(gejala_terpilih):
    if not gejala_terpilih:
        return {"probabilitas": {}, "diagnosa_utama": None}

    kombinasi = {}

    for kode in gejala_terpilih:
        info = gejala[kode]
        d = info['densitas']
        gejala_penyakit = info['penyakit']

        belief = {}
        for p in gejala_penyakit:
            belief[p] = d

        belief["theta"] = 1 - d

        if not kombinasi:
            kombinasi = belief
            continue

        kombinasi = gabungkan_belief(kombinasi, belief)

    hasil_probabilitas = {}
    for k, v in kombinasi.items():
        if k == "theta":
            continue
        persen = round(v * 100, 2)
        tingkat = interpretasi(v)
        hasil_probabilitas[k] = {
            "probabilitas": persen,
            "tingkat": tingkat
        }

    if not hasil_probabilitas:
        return {"probabilitas": {}, "diagnosa_utama": None}

    # Ambil diagnosis dengan nilai tertinggi
    diagnosis_utama = max(hasil_probabilitas, key=lambda k: hasil_probabilitas[k]["probabilitas"])

    return {
        "probabilitas": hasil_probabilitas,
        "diagnosa_utama": diagnosis_utama
    }

def interpretasi(nilai):
    if nilai == 0:
        return "Sehat"
    elif 0 < nilai <= 0.4:
        return "Ringan"
    elif 0.41 <= nilai <= 0.6:
        return "Sedang"
    elif 0.61 <= nilai <= 0.8:
        return "Berat"
    elif 0.81 <= nilai <= 1:
        return "Mati"

def gabungkan_belief(m1, m2):
    kombinasi = {}
    konflik = 0.0

    for h1, v1 in m1.items():
        for h2, v2 in m2.items():
            if h1 == h2 and h1 != "theta":
                key = h1
            elif h1 == "theta":
                key = h2
            elif h2 == "theta":
                key = h1
            else:
                key = "conflict"

            if key == "conflict":
                konflik += v1 * v2
            else:
                kombinasi[key] = kombinasi.get(key, 0) + v1 * v2

    # Normalisasi
    if konflik < 1:
        for k in kombinasi:
            kombinasi[k] = kombinasi[k] / (1 - konflik)
    else:
        kombinasi = {}

    return kombinasi

if __name__ == '__main__':
    app.run(debug=True)
