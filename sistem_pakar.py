# ===== Knowledge Base =====
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
    "G09": "Infeksi Kulit",
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

# ===== Fungsi Kombinasi (Dempster's Rule) =====
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

# ===== Fungsi Inferensi =====
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

# ===== Fungsi Belief dan Plausibility =====
def belief(subset, mass):
    return sum(v for k, v in mass.items() if set(k).issubset(set(subset)))

def plausibility(subset, mass):
    subset = set(subset)
    return sum(v for k, v in mass.items() if set(k) & subset or k == ("Theta",))

# ===== Eksekusi Diagnosa (Contoh Gejala: G03, G07, G02) =====
input_gejala = ["G03", "G07", "G02"]
hasil_mass = dempster_shafer_inference(input_gejala, base_knowledge)

print("=== Mass Function Gabungan ===")
for k, v in hasil_mass.items():
    print(f"{k}: {v:.4f}")

print("\n=== Belief & Plausibility ===")
for kode, nama in diagnoses.items():
    bel = belief([kode], hasil_mass)
    pl = plausibility([kode], hasil_mass)
    print(f"{nama} → Belief: {bel:.4f}, Plausibility: {pl:.4f}, Ignorance: {(pl - bel):.4f}")