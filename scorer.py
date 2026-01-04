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

MIN_MATCH_RATIO = 0.2 

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
    cv_stems = set(get_stems(clean_cv_text))
    cv_skills = set(extract_skills_from_stems(cv_stems))
    
    logging.info(f"CV'den çıkarılan yetkinlikler: {list(cv_skills)}")

    # 3️⃣ İLAN KRİTERLERİNİ HAZIRLAMA
    target_skills = set()
    raw_list = criteria_json.get("yetkinlikler", [])
    
    for s in raw_list:
        s_clean = s.lower().strip()
        target_skills.add(s_clean)
        if " " in s_clean:
            target_skills.update(s_clean.split())

    if not target_skills:
        logging.warning("İlanda hiç yetkinlik kriteri yok, skor 0 dönülüyor.")
        return 0.0

    # --- YETKİNLİK EŞLEŞTİRME ---
    matched_skills = {
        s for s in target_skills 
        if s in cv_skills or any(s in skill for skill in cv_skills)
    }
    
    match_ratio = len(matched_skills) / len(target_skills)

    logging.info(
        f"Yetkinlik Eşleşmesi: {len(matched_skills)} / {len(target_skills)} "
        f"→ Oran: %{match_ratio*100:.1f}"
    )

    if match_ratio < MIN_MATCH_RATIO:
        logging.info(f"❌ Yetersiz Eşleşme (Eşik: %{MIN_MATCH_RATIO*100}, Aday: %{match_ratio*100:.1f}) → ELENDİ")
        return 0.0

    score_skills = match_ratio * 100

    # ---------------------------------------------------------
    # 4️⃣ DENEYİM SKORU (OVERQUALIFIED MANTIĞI EKLENDİ)
    # ---------------------------------------------------------
    cv_experience = extract_experience_years(clean_cv_text)
    required_experience = criteria_json.get("deneyim_yili", 0)
    
    score_experience = 100.0
    
    if required_experience > 0:
        # Üst sınır: İstenen deneyimin %40 fazlası
        over_limit = required_experience * 1.40
        
        if cv_experience < required_experience:
            # Durum A: Yetersiz Deneyim (Orantısal Azalma)
            score_experience = (cv_experience / required_experience) * 100
            
        elif cv_experience > over_limit:
            # Durum B: Aşırı Nitelikli (Overqualified - Puan Düşürme)
            # Formül: (Üst Sınır / Aday Deneyimi) * 100
            # Deneyim arttıkça puan 100'den aşağıya doğru iner.
            score_experience = (over_limit / cv_experience) * 100
            
        else:
            # Durum C: İdeal Aralık (İstenen ile %40 fazlası arası)
            score_experience = 100.0

    # 5️⃣ EĞİTİM SKORU
    score_education = 0.0
    education_criteria = criteria_json.get("egitim_durumu", [])
    
    if not education_criteria:
        score_education = 100.0 
    else:
        edu_text = " ".join(education_criteria)
        try:
            cv_vec = get_sentence_embedding(clean_cv_text[:1000])
            edu_vec = get_sentence_embedding(preprocess_text(edu_text))
            sim_score = calculate_similarity_score(cv_vec, edu_vec)
            score_education = min(100.0, sim_score + 10.0)
        except:
            score_education = 50.0

    # 6️⃣ FİNAL SKOR
    final_score = (
        score_skills * 0.60 +
        score_experience * 0.25 +
        score_education * 0.15
    )

    logging.info(
        f"SONUÇ → Yetkinlik: {score_skills:.1f}, Deneyim: {score_experience:.1f} (CV: {cv_experience}, Req: {required_experience}), "
        f"Eğitim: {score_education:.1f} | FİNAL: {final_score:.2f}"
    )

    return round(final_score, 2)