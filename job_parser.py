import logging
import re
import json
from zemberek import TurkishMorphology

# -------------------------------------------------
# 1️⃣ BİLGİ BANKALARI
# -------------------------------------------------
SKILLS_DATABASE = {
    'python', 'django', 'flask', 'api', 'rest api', 'postgresql', 'mysql', 'sql',
    'react', 'javascript', 'html', 'css', 'docker', 'git', 'ci/cd',
    'java', 'c#', '.net', 'kotlin', 'swift', 'php', 'laravel',
    'makine öğrenmesi', 'veri bilimi', 'tensorflow', 'pandas', 'numpy',
    'aws', 'azure', 'cloud', 'linux', 'bash', 'agile', 'scrum', 'jira',
    'mongodb', 'redis', 'elasticsearch', 'fastapi', 'spring boot', 'hibernate',
    'vue', 'angular', 'node.js', 'express', 'typescript', 'go', 'golang',
    'ruby', 'rails', 'scala', 'hadoop', 'spark', 'kafka', 'airflow',
    'k8s', 'kubernetes', 'jenkins', 'ansible', 'terraform'
}

EDUCATION_DATABASE = [
    "Bilgisayar Mühendisliği", "Yazılım Mühendisliği", "Endüstri Mühendisliği",
    "Matematik Mühendisliği", "Elektrik Elektronik Mühendisliği",
    "Yönetim Bilişim Sistemleri"
]

# -------------------------------------------------
# 2️⃣ ZEMBEREK BAŞLATMA
# -------------------------------------------------
try:
    # logging seviyesini sadece hataları gösterecek şekilde ayarladım, çıktı temiz olsun
    logging.basicConfig(level=logging.ERROR) 
    morphology = TurkishMorphology.create_with_defaults()
except Exception as e:
    logging.error(f"Zemberek başlatılamadı: {e}")
    morphology = None

# -------------------------------------------------
# 3️⃣ SATIR BAZLI STEM (KÖK) ÇIKARIMI
# -------------------------------------------------
def get_stems_from_text(text):
    """
    Metindeki kelimelerin köklerini çıkarır.
    """
    if not text or not morphology:
        return set()

    stems = set()
    # Kelimeleri ayır
    words = re.findall(r'\b\w+\b', text.lower())

    for word in words:
        results = morphology.analyze(word)
        if results.analysis_results:
            lemma = results.analysis_results[0].item.lemma
            stems.add(lemma)
            stems.add(word) # Orijinal halini de ekle
        else:
            stems.add(word)

    return stems

# -------------------------------------------------
# 4️⃣ İŞ İLANI ANALİZ MOTORU (TEK LİSTE)
# -------------------------------------------------
def analyze_job_posting(text):
    
    sonuc = {
        "yetkinlikler": [],      # Artık tek bir liste var
        "egitim_durumu": [],
        "deneyim_yili": 0
    }

    text_lower = text.lower()

    # A. EĞİTİM DURUMU KONTROLÜ
    for bolum in EDUCATION_DATABASE:
        if bolum.lower() in text_lower:
            if bolum not in sonuc["egitim_durumu"]:
                sonuc["egitim_durumu"].append(bolum)

    # B. DENEYİM YILI (Regex)
    deneyim_match = re.search(r"en az (\d+)\s*(?:yıl|sene)", text_lower)
    if deneyim_match:
        sonuc["deneyim_yili"] = int(deneyim_match.group(1))
    else:
        alt_match = re.search(r"(\d+)\s*(?:yıl|sene)\s*deneyim", text_lower)
        if alt_match:
            sonuc["deneyim_yili"] = int(alt_match.group(1))

    # C. YETKİNLİK AYRIŞTIRMA (Tüm metin üzerinden)
    # Satır satır gezmeye gerek kalmadı, tüm metnin köklerini alıp bakabiliriz.
    all_stems = get_stems_from_text(text)
    
    found_skills = set() # Tekrarı önlemek için küme (set) kullanıyoruz
    
    for skill in SKILLS_DATABASE:
        skill_parts = skill.split()
        
        if len(skill_parts) > 1:
            # "rest api" gibi çok kelimeli yetkinlikler için hepsi var mı?
            if all(part in all_stems for part in skill_parts):
                found_skills.add(skill)
        else:
            # Tek kelimeli yetkinlikler
            if skill in all_stems:
                found_skills.add(skill)
    
    # Set'i listeye çevirip sonuca ekle
    sonuc["yetkinlikler"] = list(found_skills)
    
    return sonuc

# -------------------------------------------------
# 5️⃣ TEST
# -------------------------------------------------

ilan_metni = """
Ekibimize güç katacak, modern web teknolojilerine hakim bir Backend Geliştirici arıyoruz.

Sorumluluklar:

Ölçeklenebilir ve güvenli API mimarilerinin tasarlanması ve geliştirilmesi.

Mevcut Python ve Django tabanlı projelerin bakımının yapılması.

Veritabanı performans optimizasyonlarının (PostgreSQL, Redis) gerçekleştirilmesi.

Üçüncü parti servis entegrasyonlarının yapılması.

Aranan Nitelikler:

En az 2 yıl web geliştirme deneyimi.

Python programlama diline ve Django (veya FastAPI) framework'üne hakimiyet.

REST API tasarımı ve geliştirme konularında tecrübeli.

SQL bilgisine sahip, ilişkisel veritabanları ile çalışmış.

Git versiyon kontrol sistemini aktif kullanan.

Tercihen Docker ve Linux ortamlarına aşina.

Temel düzeyde HTML, CSS ve JavaScript bilgisi olan.

İletişim becerileri yüksek ve takım çalışmasına yatkın.

Analitik düşünen ve problem çözme yeteneğine sahip.

Sunduklarımız:

Uzaktan (Remote) çalışma imkanı.

Eğitim ve gelişim desteği.

Keyifli ve dinamik bir çalışma ortamı.
"""

# Analizi çalıştır
sonuc_json = analyze_job_posting(ilan_metni)

print(json.dumps(sonuc_json, indent=4, ensure_ascii=False))