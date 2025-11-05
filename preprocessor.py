import re
import logging

logging.info("Zemberek'SİZ ön işleme modu aktif.")

def preprocess_text(raw_text):
    """
    Zemberek OLMADAN metni ön işler.
    Sadece küçük harf, noktalama/sayı temizliği yapar.
    """
    if not raw_text:
        return ""
        
    # 1. Küçük harf
    text = raw_text.lower()
    
    # 2. Noktalamaları, sayıları ve gereksiz karakterleri kaldır
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip() # Fazla boşlukları temizle
            
    return text