from utils import (
    extract_text_from_cv,
    extract_experience_years,
    get_stems,
    extract_skills_from_stems
)

from preprocessor import preprocess_text
from model import get_sentence_embedding
from sklearn.metrics.pairwise import cosine_similarity
import logging

MIN_MANDATORY_SKILL_RATIO = 0.3  # %30 eşik


def calculate_similarity_score(vec1, vec2):
    try:
        score = cosine_similarity(
            vec1.reshape(1, -1),
            vec2.reshape(1, -1)
        )[0][0]
        return max(0, score * 100)
    except Exception as e:
        logging.error(f"Kosinüs benzerliği hatası: {e}")
        return 0.0


def get_suitability_score(cv_file_path, criteria_json):
    logging.info(f"Uygunluk puanlaması başlıyor: {cv_file_path}")

    # 1️⃣ CV METNİ ÇIKARMA VE ÖN İŞLEME
    raw_cv_text = extract_text_from_cv(cv_file_path)
    if not raw_cv_text:
        return 0.0

    clean_cv_text = preprocess_text(raw_cv_text)
    if not clean_cv_text:
        return 0.0

    # 2️⃣ CV YETKİNLİKLERİNİ ÇIKARMA
    # Hem kökleri hem de kelimelerin orijinal hallerini (lowercase) alıyoruz
    cv_stems = set(get_stems(clean_cv_text)) 
    cv_skills = set(extract_skills_from_stems(cv_stems))
    
    # Debug için log: CV'den ne çıktı?
    logging.info(f"CV'den çıkarılan yetkinlikler: {list(cv_skills)}")

    # 3️⃣ İLAN KRİTERLERİNİ HAZIRLAMA (Standardize edilmiş)
    # Kriterleri direkt set olarak alıyoruz, get_stems'in bozma riskine karşı 
    # ham hallerini de listeye dahil ediyoruz.
    def prepare_criteria(key):
        raw_list = criteria_json.get(key, [])
        criteria_set = set()
        for s in raw_list:
            s_clean = s.lower().strip()
            criteria_set.add(s_clean)
            # Eğer kelime çokluysa parçalarını da ekle (Örn: "Rest API" -> "rest", "api")
            if " " in s_clean:
                criteria_set.update(s_clean.split())
        return criteria_set

    mandatory_reqs = prepare_criteria("zorunlu_yetkinlikler")
    optional_reqs = prepare_criteria("istenen_yetkinlikler")

    # --- ZORUNLU YETKİNLİK ELEME (SOFT MATCH) ---
    if mandatory_reqs:
        # Kesişimi manuel yapıyoruz çünkü substring kontrolü daha güvenli
        mandatory_matches = {s for s in mandatory_reqs if s in cv_skills or any(s in skill for skill in cv_skills)}
        mandatory_ratio = len(mandatory_matches) / len(mandatory_reqs)

        logging.info(
            f"Zorunlu Yetkinlik: {len(mandatory_matches)} / {len(mandatory_reqs)} "
            f"→ Eşleşenler: {sorted(list(mandatory_matches))}"
        )

        if mandatory_ratio < MIN_MANDATORY_SKILL_RATIO:
            logging.info(f"❌ Eşik (%{MIN_MANDATORY_SKILL_RATIO*100}) geçilemedi (Oran: {mandatory_ratio:.2f}) → ELENDİ")
            return 0.0

    # --- SKOR HESAPLAMA ---
    # Yetkinlik Skoru
    m_score = len(mandatory_matches) / len(mandatory_reqs) if mandatory_reqs else 1.0
    
    optional_matches = {s for s in optional_reqs if s in cv_skills or any(s in skill for skill in cv_skills)}
    o_score = len(optional_matches) / len(optional_reqs) if optional_reqs else 0.0

    score_skills = (m_score * 0.7 + o_score * 0.3) * 100

    # 4️⃣ DENEYİM SKORU (Bonus Puanlı)
    cv_experience = extract_experience_years(clean_cv_text)
    required_experience = criteria_json.get("deneyim_yili", 0)

    if required_experience > 0:
        # İstediğinden fazlaysa 100 üzerinden bonus ver, azsa orantıla
        exp_ratio = cv_experience / required_experience
        score_experience = min(110.0, exp_ratio * 100) 
    else:
        score_experience = 100.0

    # 5️⃣ EĞİTİM SKORU (BERT Geliştirmesi)
    score_education = 80.0 # Default orta değer
    education_criteria = criteria_json.get("egitim_durumu", [])
    
    if education_criteria:
        edu_text = " ".join(education_criteria)
        try:
            # SBERT ile benzerlik
            cv_vec = get_sentence_embedding(clean_cv_text[:1000]) # Sadece baş kısımlar (eğitim genelde üsttedir)
            edu_vec = get_sentence_embedding(preprocess_text(edu_text))
            sim_score = calculate_similarity_score(cv_vec, edu_vec)
            # BERT skorunu biraz yukarı çekiyoruz (Bias) çünkü CV çok gürültülüdür
            score_education = min(100.0, sim_score + 20.0) 
        except Exception as e:
            logging.error(f"Eğitim vektörü hatası: {e}")

    # 6️⃣ FİNAL SKOR (Ağırlıklı Toplam)
    final_score = (
        score_skills * 0.5 +
        score_experience * 0.3 +
        score_education * 0.2
    )

    logging.info(
        f"SONUÇ → Yetkinlik: {score_skills:.1f}, Deneyim: {score_experience:.1f}, "
        f"Eğitim: {score_education:.1f} | FİNAL: {final_score:.2f}"
    )

    return round(final_score, 2)
