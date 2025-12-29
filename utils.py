import fitz
import docx
import logging
import re
import datetime
from zemberek import TurkishMorphology

# -------------------------------------------------
# LOGGING
# -------------------------------------------------
logging.basicConfig(level=logging.INFO)

# -------------------------------------------------
# 1️⃣ YETKİNLİK BİLGİ BANKASI (EN ÜSTTE OLMALI)
# -------------------------------------------------
SKILLS_DATABASE = {
    'python', 'django', 'flask', 'api', 'rest api', 'postgresql', 'mysql', 'sql',
    'react', 'javascript', 'html', 'css', 'docker', 'git', 'ci/cd',
    'java', 'c#', '.net', 'kotlin', 'swift', 'php', 'laravel',
    'makine öğrenmesi', 'veri bilimi', 'tensorflow', 'pandas', 'numpy'
}

# -------------------------------------------------
# 2️⃣ ZEMBEREK (TEK SEFER YÜKLENİR)
# -------------------------------------------------
morphology = TurkishMorphology.create_with_defaults()

# -------------------------------------------------
# 3️⃣ STEM (LEMMA) ÇIKARIMI
# -------------------------------------------------
def get_stems(text):
    if not text:
        return set()

    stems = set()
    # Kelimeleri ayırırken küçük harfe çevir
    words = re.findall(r'\b\w+\b', text.lower())

    for word in words:
        # Teknik terimleri (Sayı içeren veya özel karakterli) korumak için basit bir kontrol
        # Ya da direkt Zemberek analizini yap, ama orijinal kelimeyi de sakla
        analysis = morphology.analyze(word)
        if analysis.analysis_results:
            # Zemberek bazen "python" gibi kelimeleri yanlış analiz eder.
            # Stems kümesine hem kökü hem de kelimenin kendisini eklemek en güvenlisidir.
            lemma = analysis.analysis_results[0].item.lemma
            stems.add(lemma)
            stems.add(word) # Orijinal halini de ekle (Örn: python)
        else:
            stems.add(word) # Analiz edilemiyorsa olduğu gibi ekle

    return stems

# -------------------------------------------------
# 4️⃣ STEM TABANLI YETKİNLİK ÇIKARIMI
# -------------------------------------------------
def extract_skills_from_stems(stems):
    found_skills = set()
    
    # stems artık hem kökleri hem orijinal kelimeleri içeriyor.
    for skill in SKILLS_DATABASE:
        skill_lower = skill.lower()
        skill_tokens = skill_lower.split()

        if len(skill_tokens) > 1:
            # "rest api" gibi çok kelimeliler için
            if all(token in stems for token in skill_tokens):
                found_skills.add(skill_lower)
        else:
            # "python" gibi tek kelimeliler için
            if skill_lower in stems:
                found_skills.add(skill_lower)

    return list(found_skills)

# -------------------------------------------------
# 5️⃣ CV METNİ ÇIKARMA (PDF / DOCX)
# -------------------------------------------------
def extract_text_from_cv(filepath):
    """
    PDF veya DOCX dosyasından metin çıkarır.
    """
    if not filepath:
        logging.error("Dosya yolu boş.")
        return None

    text = ""

    if filepath.endswith(".pdf"):
        try:
            with fitz.open(filepath) as doc:
                for page in doc:
                    page_text = page.get_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logging.error(f"PDF okuma hatası ({filepath}): {e}")
            return None

    elif filepath.endswith(".docx"):
        try:
            doc = docx.Document(filepath)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            logging.error(f"DOCX okuma hatası ({filepath}): {e}")
            return None

    else:
        logging.warning(f"Desteklenmeyen dosya formatı: {filepath}")
        return None

    logging.info(f"Metin başarıyla çıkarıldı: {filepath}")
    return text.strip()

# -------------------------------------------------
# 6️⃣ DENEYİM YILI ÇIKARIMI
# -------------------------------------------------
def extract_experience_years(clean_text):
    """
    Metinden deneyim yılını Regex ile tahmin eder.
    """
    if not clean_text:
        return 0

    experiences = []
    current_year = datetime.datetime.now().year

    # "5 yıl", "3 sene"
    explicit_matches = re.findall(r'(\d+)\s*(yıl|sene|year)', clean_text)
    for match in explicit_matches:
        experiences.append(int(match[0]))

    # "2019 - 2023"
    range_matches = re.findall(r'(20\d{2})\s*-\s*(20\d{2})', clean_text)
    for start, end in range_matches:
        start, end = int(start), int(end)
        if end > start:
            experiences.append(end - start)

    # "2020 - halen"
    current_matches = re.findall(
        r'(20\d{2})\s*-\s*(halen|günümüz|present|still)',
        clean_text
    )
    for start, _ in current_matches:
        start = int(start)
        if current_year > start:
            experiences.append(current_year - start)

    return max(experiences) if experiences else 0
