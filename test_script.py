import logging
import os
from scorer import get_suitability_score

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

CV_KLASOR_YOLU = "CV_Klasoru"

# --- JUNIOR İLAN ---
JUNIOR_ILAN_JSON = {
    # 🔴 ELEME KRİTERİ
    "zorunlu_yetkinlikler": ["python", "api", "sql", "git"],

    # 🟡 PUAN ARTTIRICI
    "istenen_yetkinlikler": ["docker", "linux", "rest", "unit test"],

    "egitim_durumu": [
        "Bilgisayar Mühendisliği",
        "Yazılım Mühendisliği"
    ],

    "deneyim_yili": 0
}

# --- SENIOR İLAN ---
SENIOR_ILAN_JSON = {
    # 🔴 ELEME KRİTERİ
    "zorunlu_yetkinlikler": [
        "python", "django", "api",
        "postgresql", "docker", "ci/cd"
    ],

    # 🟡 PUAN ARTTIRICI
    "istenen_yetkinlikler": [
        "kafka", "redis", "aws",
        "linux", "microservice"
    ],

    "egitim_durumu": ["Bilgisayar Mühendisliği"],
    "deneyim_yili": 5
}

# --- TEST İLAN ---
TEST_ILAN_JSON = {
    "yetkinlikler": [
        "rest api",
        "git",
        "redis",
        "api",
        "fastapi",
        "django",
        "javascript",
        "docker",
        "python",
        "html",
        "postgresql",
        "css",
        "sql",
        "linux"
    ],
    "egitim_durumu": [],
    "deneyim_yili": 2
}



def run_test(ilan_adi, kriterler):
    logging.info(f"--- UYGUNLUK TESTİ BAŞLATILIYOR: [{ilan_adi}] ---")

    all_scores = []

    if not os.path.isdir(CV_KLASOR_YOLU):
        logging.error(f"HATA: '{CV_KLASOR_YOLU}' klasörü bulunamadı.")
        return

    for filename in os.listdir(CV_KLASOR_YOLU):
        if filename.lower().endswith((".pdf", ".docx")):
            full_path = os.path.join(CV_KLASOR_YOLU, filename)

            try:
                puan = get_suitability_score(
                    cv_file_path=full_path,
                    criteria_json=kriterler
                )
                all_scores.append((filename, puan))
            except Exception as e:
                logging.error(f"'{filename}' puanlanırken hata: {e}")
                all_scores.append((filename, 0.0))

    # 🔢 PUANA GÖRE SIRALA
    ranked_scores = sorted(all_scores, key=lambda x: x[1], reverse=True)

    # 🖨️ YAZDIR
    print("\n" + "=" * 50)
    print(f"  UYGUNLUK SIRALAMASI: {ilan_adi}")
    print("=" * 50)

    for i, (filename, puan) in enumerate(ranked_scores, start=1):
        print(f"{i:>2}. {filename:<30} | PUAN: {puan:>6.2f} / 100")

    print("=" * 50 + "\n")


if __name__ == "__main__":
    run_test("Junior Python Developer", JUNIOR_ILAN_JSON)
    run_test("Senior Python Developer", SENIOR_ILAN_JSON)
    run_test("Test Python Developer", TEST_ILAN_JSON)