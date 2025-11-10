import fitz 
import docx
import logging
import re 
import datetime # YENİ: Deneyim hesaplaması için eklendi

# Hataları loglamak için
logging.basicConfig(level=logging.INFO)

# --- 1. YETKİNLİK BİLGİ BANKASI (Aynı) ---
SKILLS_DATABASE = {
    'python', 'django', 'flask', 'api', 'rest api', 'postgresql', 'mysql', 'sql',
    'react', 'javascript', 'html', 'css', 'docker', 'git', 'ci/cd',
    'java', 'c#', '.net', 'kotlin', 'swift', 'php', 'laravel', 'makine öğrenmesi',
    'veri bilimi', 'tensorflow', 'pandas', 'numpy'
}

def extract_text_from_cv(filepath):
    """
    Verilen dosya yolundan (.pdf veya .docx) metin çıkarır.
    (Bu fonksiyonda değişiklik yapılmadı)
    """
    text = ""
    if not filepath:
        logging.error("Dosya yolu boş.")
        return None
    if filepath.endswith('.pdf'):
        try:
            with fitz.open(filepath) as doc:
                for page in doc:
                    page_text = page.get_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logging.error(f"PDF Okuma Hatası (PyMuPDF) ({filepath}): {e}")
            return None
    elif filepath.endswith('.docx'):
        try:
            doc = docx.Document(filepath)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            logging.error(f"DOCX Okuma Hatası ({filepath}): {e}")
            return None
    else:
        logging.warning(f"Desteklenmeyen dosya formatı: {filepath}")
        return None
    logging.info(f"Metin başarıyla çıkarıldı: {filepath}")
    return text.strip()


# --- 2. GÜNCELLENMİŞ FONKSİYON: Akıllı Yetkinlik Çıkarıcı ---
def extract_skills_from_text(clean_text):
    """
    Temizlenmiş CV metninden SKILLS_DATABASE'de bulunan
    yetkinlikleri çıkaran GÜNCELLENMİŞ fonksiyon.
    
    Bu yöntem artık "rest api", "c#", "ci/cd" gibi çoklu kelimeleri
    ve özel karakterli yetkinlikleri bulabilir.
    """
    found_skills = set()
    
    # Metni kelimelere ayırmıyoruz.
    # Bunun yerine, her bir yetkinliğin metinde geçip geçmediğine bakıyoruz.
    for skill in SKILLS_DATABASE:
        # re.escape(skill), 'c#' ve '.net' gibi özel karakterlerin
        # regex'te düzgün çalışmasını sağlar.
        # \b kelime sınırı demektir ('api' kelimesinin 'terapi' içinde bulunmasını engeller)
        pattern = r'\b' + re.escape(skill) + r'\b'
        
        # clean_text zaten küçük harf olduğu için IGNORECASE'e gerek yok
        if re.search(pattern, clean_text):
            found_skills.add(skill)
            
    return list(found_skills)


# --- 3. GÜNCELLENMİŞ FONKSİYON: Akıllı Deneyim Yılı Çıkarıcı ---
def extract_experience_years(clean_text):
    """
    Metinden deneyim yılını Regex ile bulmaya çalışır.
    
    GÜNCELLEME:
    1. "5 yıl", "3 sene" gibi net ifadeleri arar.
    2. "2019 - 2023" gibi tarih aralıklarını hesaplar.
    3. "2020 - Halen" (veya günümüz, present) gibi aralıkları hesaplar.
    
    Bulduğu tüm değerler arasından en yüksek olanı döndürür.
    """
    experiences = []
    current_year = datetime.datetime.now().year
    
    # 1. "X yıl/sene/year" gibi net ifadeleri bul
    # (clean_text küçük harf olduğu için 'year|yıl|sene' yeterli)
    explicit_matches = re.findall(r'(\d+)\s*(yıl|sene|year)', clean_text)
    for match in explicit_matches:
        experiences.append(int(match[0]))
        
    # 2. "2019-2023" gibi tarih aralıklarını bul
    # (20\d{2}) -> 2000-2099 arası yılları yakalar
    range_matches = re.findall(r'(20\d{2})\s*-\s*(20\d{2})', clean_text)
    for match in range_matches:
        try:
            start_year = int(match[0])
            end_year = int(match[1])
            if end_year > start_year:
                experiences.append(end_year - start_year)
        except Exception:
            pass # Hatalı tarih formatıysa es geç

    # 3. "2020 - Halen" gibi mevcut işleri bul
    # (halen|günümüz|present|still)
    current_matches = re.findall(r'(20\d{2})\s*-\s*(halen|günümüz|present|still)', clean_text)
    for match in current_matches:
        try:
            start_year = int(match[0])
            if current_year > start_year:
                experiences.append(current_year - start_year)
        except Exception:
            pass
            
    # Tüm bulunan deneyimler arasından en yükseğini döndür
    if experiences:
        return max(experiences)
        
    return 0 # Hiçbir şey bulamazsa 0 yıl döner