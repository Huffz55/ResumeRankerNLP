from utils import extract_text_from_cv, extract_skills_from_text, extract_experience_years
from preprocessor import preprocess_text
from model import get_sentence_embedding
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

def calculate_similarity_score(vec1, vec2):
    """
    İki BERT vektörü arasındaki kosinüs benzerliğini hesaplar (0-100 arası).
    """
    try:
        vec1_2d = vec1.reshape(1, -1)
        vec2_2d = vec2.reshape(1, -1)
        score = cosine_similarity(vec1_2d, vec2_2d)[0][0]
        return max(0, score * 100)
    except Exception as e:
        logging.error(f"Kosinüs benzerliği hesaplama hatası: {e}")
        return 0.0

# --- YENİ ANA FONKSİYON ---
def get_suitability_score(cv_file_path, criteria_json):
    """
    YENİ ANA FONKSİYON:
    Kural tabanlı (Yetkinlik, Deneyim) ve Anlamsal (Eğitim)
    kontrolleri birleştirerek UYGUNLUK PUANI hesaplar.
    """
    logging.info(f"Uygunluk puanlaması başlıyor: {cv_file_path}")
    
    # 1. CV'den metni çıkar ve temizle
    raw_cv_text = extract_text_from_cv(cv_file_path)
    if not raw_cv_text:
        return 0.0
    
    clean_cv_text = preprocess_text(raw_cv_text)
    if not clean_cv_text:
        return 0.0

    # --- PUANLAMA MODÜLLERİ ---
    
    # 2. YETKİNLİK PUANI (Kural Tabanlı - ZEMBEREK ENTEGRE EDİLDİ)
    
    # Adım 2a: Zemberek'i kullanarak temiz metinden kökleri (stems) al
    cv_stems = get_stems(clean_cv_text)
    
    # Adım 2b: Kök listesini kullanarak CV'deki yetkinlikleri bul
    # (utils'deki yeni fonksiyonumuzu çağırıyoruz)
    cv_skills = set(extract_skills_from_stems(cv_stems))
    
    # Adım 2c: İlandan GEREKLİ yetkinlikleri al
    # (Bu listenin utils'deki KÖK veritabanıyla eşleşmesi gerekir)
    required_skills = set(criteria_json.get("zorunlu_yetkinlikler", []))
    
    score_skills = 0.0
    if required_skills:
        # Gerekli yetkinliklerin yüzde kaçı CV'de mevcut?
        matching_skills = required_skills.intersection(cv_skills)
        score_skills = (len(matching_skills) / len(required_skills)) * 100
        
        # Loglama: Hangi yetkinliklerin eşleştiğini görmek için
        logging.info(f"Yetkinlik Eşleşmesi (Kök): {len(matching_skills)} / {len(required_skills)}")
        logging.info(f" -> Eşleşenler: {matching_skills}")
        logging.info(f" -> Eksikler: {required_skills.difference(cv_skills)}")
    else:
        logging.info("İlan için zorunlu yetkinlik belirtilmemiş, bu adım atlanıyor.")
        score_skills = 100.0 # Eğer zorunlu bir şey yoksa, puanı tam ver (veya 0.0, karara bağlı)
    
    # 3. DENEYİM PUANI (Kural Tabanlı)
    cv_experience = extract_experience_years(clean_cv_text)
    required_experience = criteria_json.get("deneyim_yili", 0)
    
    score_experience = 0.0
    if required_experience > 0:
        if cv_experience >= required_experience:
            score_experience = 100.0 # Kriteri karşılıyor
        else:
            # Kriterin yarısını karşılıyorsa %50 puan ver
            score_experience = (cv_experience / required_experience) * 100 
    else:
        # Eğer 0 yıl (Junior) aranıyorsa, deneyim önemsizdir.
        score_experience = 100.0 # Herkes uygundur (0 yıl da dahil)
    logging.info(f"Deneyim Eşleşmesi: CV'de {cv_experience} yıl, İlanda {required_experience} yıl")

    # 4. EĞİTİM PUANI (Anlamsal - BERT'i burada kullanıyoruz)
    # Eğitim, "Bilgisayar Müh." yerine "Bilişim Sistemleri" gibi
    # benzer anlamlı olabileceği için burada anlamsal karşılaştırma mantıklıdır.
    education_text = " ".join(criteria_json.get("egitim_durumu", []))
    score_education = 0.0
    
    if education_text:
        try:
            # CV'nin tamamı yerine "Eğitim" bölümü bulunabilir (İleri Seviye)
            # Şimdilik CV'nin tamamının vektörünü alıyoruz
            cv_vector = get_sentence_embedding(clean_cv_text)
            education_vector = get_sentence_embedding(preprocess_text(education_text))
            score_education = calculate_similarity_score(cv_vector, education_vector)
        except Exception as e:
            logging.error(f"Eğitim vektörü hatası: {e}")
            
    # --- FİNAL SKOR (AĞIRLIKLI ORTALAMA) ---
    
    # Ağırlıklar: %50 Yetkinlik, %30 Deneyim, %20 Eğitim
    # Bu ağırlıkları işveren de belirleyebilir!
    
    final_score = (score_skills * 0.5) + (score_experience * 0.3) + (score_education * 0.2)
    
    logging.info(f"Puanlama tamamlandı. Yetkinlik: {score_skills:.2f}, Deneyim: {score_experience:.2f}, Eğitim: {score_education:.2f} -> FİNAL UYGUNLUK: {final_score:.2f}")
    
    return final_score