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

#MIN_MANDATORY_SKILL_RATIO = 0.6  # %60 eşik


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

    # 1️⃣ CV METNİ
    raw_cv_text = extract_text_from_cv(cv_file_path)
    if not raw_cv_text:
        return 0.0

    clean_cv_text = preprocess_text(raw_cv_text)
    if not clean_cv_text:
        return 0.0

    # 2️⃣ YETKİNLİKLER
    cv_stems = get_stems(clean_cv_text)
    cv_skills = set(extract_skills_from_stems(cv_stems))

    mandatory_skills = set(criteria_json.get("zorunlu_yetkinlikler", []))
    optional_skills = set(criteria_json.get("istenen_yetkinlikler", []))

    # --- ZORUNLU YETKİNLİK EŞİĞİ ---
    if mandatory_skills:
        mandatory_matches = mandatory_skills & cv_skills
        mandatory_ratio = len(mandatory_matches) / len(mandatory_skills)

        logging.info(
            f"Zorunlu Yetkinlik: "
            f"{len(mandatory_matches)} / {len(mandatory_skills)}"
        )

        if mandatory_ratio < MIN_MANDATORY_SKILL_RATIO:
            logging.info("❌ Zorunlu yetkinlik eşiği geçilemedi → ELENDİ")
            return 0.0

    # --- SKILL SKORU (Zorunlu + İstenen) ---
    all_skill_set = mandatory_skills | optional_skills

    if all_skill_set:
        matched_skills = all_skill_set & cv_skills
        score_skills = (len(matched_skills) / len(all_skill_set)) * 100
    else:
        score_skills = 100.0

    # 3️⃣ DENEYİM
    cv_experience = extract_experience_years(clean_cv_text)
    required_experience = criteria_json.get("deneyim_yili", 0)

    if required_experience > 0:
        score_experience = min(
            100.0,
            (cv_experience / required_experience) * 100
        )
    else:
        score_experience = 100.0

    # 4️⃣ EĞİTİM (BERT)
    score_education = 0.0
    education_text = " ".join(criteria_json.get("egitim_durumu", []))

    if education_text:
        try:
            cv_vec = get_sentence_embedding(clean_cv_text)
            edu_vec = get_sentence_embedding(
                preprocess_text(education_text)
            )
            score_education = calculate_similarity_score(cv_vec, edu_vec)
        except Exception as e:
            logging.error(f"Eğitim vektörü hatası: {e}")

    # 5️⃣ FİNAL SKOR
    final_score = (
        score_skills * 0.5 +
        score_experience * 0.3 +
        score_education * 0.2
    )

    logging.info(
        f"TOPLAM SKOR → "
        f"Yetkinlik: {score_skills:.2f}, "
        f"Deneyim: {score_experience:.2f}, "
        f"Eğitim: {score_education:.2f} "
        f"| FİNAL: {final_score:.2f}"
    )

    return final_score
