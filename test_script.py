import logging
import os
# GÜNCELLENDİ: Yeni ana fonksiyonumuzu import ediyoruz
from scorer import get_suitability_score 

logging.basicConfig(level=logging.INFO)

# --- AYARLAR ---
CV_KLASOR_YOLU = "CV_Klasoru" 

# --- Test 1: Junior İlan ---
JUNIOR_ILAN_JSON = {
  "zorunlu_yetkinlikler": ["python", "api", "sql", "git"], # Bilgi bankamızla eşleşmesi için küçük harf
  "egitim_durumu": ["Bilgisayar Mühendisliği", "Yazılım Mühendisliği"],
  "deneyim_yili": 0
}

# --- Test 2: Senior İlan ---
SENIOR_ILAN_JSON = {
  "zorunlu_yetkinlikler": ["python", "django", "api", "postgresql", "docker", "ci/cd"],
  "egitim_durumu": ["Bilgisayar Mühendisliği"],
  "deneyim_yili": 5 # 5 Yıl deneyim şartı
}
# --- ---

def run_test(ilan_adi, kriterler):
    logging.info(f"--- UYGUNLUK TESTİ BAŞLATILIYOR: [{ilan_adi}] ---")
    all_scores = []
    
    if not os.path.isdir(CV_KLASOR_YOLU):
        logging.error(f"HATA: '{CV_KLASOR_YOLU}' klasörü bulunamadı.")
        return

    for filename in os.listdir(CV_KLASOR_YOLU):
        if filename.endswith('.pdf') or filename.endswith('.docx'):
            full_path = os.path.join(CV_KLASOR_YOLU, filename)
            try:
                # YENİ FONKSİYONU ÇAĞIR
                puan = get_suitability_score(
                    cv_file_path=full_path, 
                    criteria_json=kriterler
                )
                all_scores.append((filename, puan))
            except Exception as e:
                logging.error(f"'{filename}' puanlanırken hata: {e}")
                all_scores.append((filename, 0.0))

    # Sırala
    ranked_scores = sorted(all_scores, key=lambda item: item[1], reverse=True)

    # Yazdır
    print("\n" + "="*40)
    print(f"  UYGUNLUK SIRALAMASI: [{ilan_adi}]")
    print("="*40)
    for i, (filename, puan) in enumerate(ranked_scores):
        print(f"  {i+1}. {filename:<30} | PUAN: {puan:>6.2f} / 100.00")
    print("="*40 + "\n")


if __name__ == "__main__":
    # Önce Junior ilan için sıralama yap
    run_test("Junior Python Developer", JUNIOR_ILAN_JSON)
    
    # Sonra Senior ilan için sıralama yap
    run_test("Senior Python Developer", SENIOR_ILAN_JSON)