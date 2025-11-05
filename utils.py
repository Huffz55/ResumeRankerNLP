import fitz  # PyMuPDF
import docx
import logging
import re # Kural tabanlı arama için Regex modülü

# Hataları loglamak için
logging.basicConfig(level=logging.INFO)

# --- 1. YETKİNLİK BİLGİ BANKASI (Basit Hali) ---
# 'preprocess_text' ile temizlendikten sonraki halleriyle (küçük harf)
SKILLS_DATABASE = {
    'python', 'django', 'flask', 'api', 'rest api', 'postgresql', 'mysql', 'sql',
    'react', 'javascript', 'html', 'css', 'docker', 'git', 'ci/cd',
    'java', 'c#', '.net', 'kotlin', 'swift', 'php', 'laravel', 'makine öğrenmesi',
    'veri bilimi', 'tensorflow', 'pandas', 'numpy'
    # Bu listeyi binlerce kelimeyle zenginleştirebilirsiniz
}

def extract_text_from_cv(filepath):
    """
    Verilen dosya yolundan (.pdf veya .docx) metin çıkarır.
    """
    text = ""
    # ... (Bu fonksiyonun içi aynı kalıyor, PDF/DOCX okuma) ...
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


# --- 2. YENİ FONKSİYON: Yetkinlik Çıkarıcı ---
def extract_skills_from_text(clean_text):
    """
    Temizlenmiş CV metninden SKILLS_DATABASE'de bulunan
    yetkinlikleri çıkaran basit bir fonksiyon.
    """
    found_skills = set()
    # Metni kelimelere ayır (daha akıllı bir tokenizer kullanılabilir ama bu basit)
    words_in_cv = set(clean_text.split())
    
    # Bilgi bankamızdaki hangi kelimeler CV'de var?
    found_skills = SKILLS_DATABASE.intersection(words_in_cv)
    
    # Not: Bu çok basit bir yöntem. "react native" gibi 2 kelimelikleri kaçırır.
    # Daha akıllı yöntem, n-gram veya regex kullanmaktır.
    # Ama "python", "react", "django" gibi tekil kelimeleri yakalar.
    
    return list(found_skills)


# --- 3. YENİ FONKSİYON: Deneyim Yılı Çıkarıcı ---
def extract_experience_years(clean_text):
    """
    Metinden deneyim yılını Regex ile bulmaya çalışır.
    Çok basit bir tahmindir, geliştirilmesi gerekir.
    """
    # (\d+) bir veya daha fazla sayıyı yakala
    # \s* arada boşluk olabilir
    # (yıl|sene|year) "yıl", "sene" veya "year" kelimelerinden biri
    # re.IGNORECASE büyük/küçük harf duyarsız
    match = re.search(r'(\d+)\s*(yıl|sene|year)', clean_text, re.IGNORECASE)
    
    if match:
        # Yakalanan ilk grup (sayı)
        return int(match.group(1))
        
    # TODO: Tarih aralıklarını (örn: 2019-2023) da hesaplayabiliriz.
    # Şimdilik basit tutuyoruz.
    
    return 0 # Hiç bulamazsa 0 yıl döner