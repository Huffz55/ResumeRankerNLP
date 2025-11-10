from utils import extract_text_from_cv, extract_skills_from_text, extract_experience_years
from preprocessor import preprocess_text, get_stems
# DÜZELTME: 'model' -> 'models' olarak güncellendi (ilk hatanız buydu)
from model import get_sentence_embedding 
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging
import re # YENİ: Eğitim bölümünü ayıklamak için eklendi

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

# --- YENİ YARDIMCI FONKSİYON ---
def extract_education_section(raw_text):
    """
    CV'nin ham metninden (raw_text) 'Eğitim' veya 'Education'
    ile başlayan bölümü Regex ile bulmaya çalışır.
    """
    try:
        # 'Eğitim' veya 'Education' ile başlayan ve bir sonraki ana başlığa
        # (Deneyim, Projeler, Yetkinlikler vb.) kadar olan kısmı alır.
        # re.IGNORECASE: Büyük/küçük harf duyarsız
        # re.DOTALL: '.' karakterinin yeni satırları da içermesi
        match = re.search(
            r'(Eğitim|Education|Öğrenim)(.*?)(Deneyim|Tecrübe|Projeler|Yetkinlikler|Skills|Experience|Referanslar|$)', 
            raw_text, 
            re.IGNORECASE | re.DOTALL
        )
        
        if match:
            # Sadece aradaki metni (eğitim bilgileri) döndür
            logging.info("CV'den 'Eğitim' bölümü başarıyla ayıklandı.")
            return match.group(2).strip()
    except Exception as e:
        logging.warning(f"Eğitim bölümü ayıklanırken hata: {e}")
        
    # Bulamazsa veya hata olursa, en azından kayıp olmasın diye tüm metni döndür (eski davranış)
    logging.warning("Eğitim bölümü ayıklanamadı. CV'nin tamamı kullanılacak.")
    return raw_text

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
    
    # 2. YETKİNLİK PUANI
    # (utils.py'deki akıllı 'extract_skills_from_text' fonksiyonunu kullanıyor)
    cv_skills = set(extract_skills_from_text(clean_cv_text))
    required_skills = set(criteria_json.get("zorunlu_yetkinlikler", []))
    
    score_skills = 0.0
    if required_skills:
        matching_skills = required_skills.intersection(cv_skills)
        score_skills = (len(matching_skills) / len(required_skills)) * 100
        
        logging.info(f"Yetkinlik Eşleşmesi: {len(matching_skills)} / {len(required_skills)}")
        logging.info(f" -> Eşleşenler: {matching_skills}")
        logging.info(f" -> Eksikler: {required_skills.difference(cv_skills)}")
    else:
        logging.info("İlan için zorunlu yetkinlik belirtilmemiş, bu adım atlanıyor.")
        score_skills = 100.0
    
    # 3. DENEYİM PUANI
    # (utils.py'deki akıllı 'extract_experience_years' fonksiyonunu kullanıyor)
    cv_experience = extract_experience_years(clean_cv_text)
    required_experience = criteria_json.get("deneyim_yili", 0)
    
    score_experience = 0.0
    if required_experience > 0:
        if cv_experience >= required_experience:
            score_experience = 100.0
        else:
            # Kısmi puanlama
            score_experience = max(0, (cv_experience / required_experience) * 100)
    else:
        score_experience = 100.0 # Junior ilanı için deneyim önemsiz
        
    logging.info(f"Deneyim Eşleşmesi: CV'de {cv_experience} yıl, İlanda {required_experience} yıl")

    # 4. EĞİTİM PUANI (GÜNCELLENMİŞ BÖLÜM)
    education_text = " ".join(criteria_json.get("egitim_durumu", []))
    score_education = 0.0
    
    if education_text:
        try:
            # GÜNCELLEME: CV'nin tamamı yerine SADECE EĞİTİM BÖLÜMÜNÜ AL
            # (raw_cv_text kullanılır çünkü 'Eğitim' başlığını bulmak için ham hali gerekir)
            education_cv_part = extract_education_section(raw_cv_text)
            
            # Bulunan bölümü temizle
            clean_education_cv_part = preprocess_text(education_cv_part)
            
            # Vektörleri sadece ilgili bölümlerden al
            if clean_education_cv_part:
                cv_vector = get_sentence_embedding(clean_education_cv_part)
            else:
                # Eğer bölüm ayıklanamazsa, eski yönteme (tüm CV) geri dön
                cv_vector = get_sentence_embedding(clean_cv_text)
            
            education_vector = get_sentence_embedding(preprocess_text(education_text))
            score_education = calculate_similarity_score(cv_vector, education_vector)
            
        except Exception as e:
            logging.error(f"Eğitim vektörü hatası: {e}")
            
    # --- FİNAL SKOR (AĞIRLIKLI ORTALAMA) ---
    
    # Ağırlıklar: %50 Yetkinlik, %30 Deneyim, %20 Eğitim
    final_score = (score_skills * 0.5) + (score_experience * 0.3) + (score_education * 0.2)
    
    logging.info(f"Puanlama tamamlandı. Yetkinlik: {score_skills:.2f}, Deneyim: {score_experience:.2f}, Eğitim: {score_education:.2f} -> FİNAL UYGUNLUK: {final_score:.2f}")
    
    return final_score