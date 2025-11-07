import logging
import re
from zemberek.morphology import TurkishMorphology

# --- Zemberek'i Global Olarak Yükle ---
# Bu, program başladığında SADECE BİR KEZ çalışır.
# Her CV için tekrar tekrar model yüklenmez.
try:
    logger = logging.getLogger(__name__)
    logger.info("Zemberek (preprocessor) başlatılıyor...")
    MORPHOLOGY = TurkishMorphology.create_with_defaults()
    logger.info("✅ Zemberek (preprocessor) başarıyla yüklendi.")
except Exception as e:
    logging.critical(f"KRİTİK HATA: Zemberek 'preprocessor' yüklenemedi! {e}")
    MORPHOLOGY = None

# --- Fonksiyonlar ---

def preprocess_text(text):
    """Metni küçük harfe çevirir ve noktalama işaretlerini kaldırır."""
    if not text:
        return ""
    text = text.lower() # 1. Tüm harfleri küçük harfe çevir
    text = re.sub(r'[^\w\s]', '', text) # 2. Noktalama ve özel karakterleri kaldır
    text = re.sub(r'\s+', ' ', text).strip() # 3. Ekstra boşlukları kaldır
    return text

def get_stems(text):
    """
    Ön işlenmiş (preprocess_text) bir metni alır, 
    kelimelere ayırır ve her kelimenin kökünü döndürür.
    """
    if not MORPHOLOGY:
        logging.error("Zemberek yüklü olmadığı için kök bulma işlemi atlanıyor.")
        return text.split() # Zemberek yoksa kelimeleri olduğu gibi döndür

    stems = []
    words = text.split()
    
    for word in words:
        if not word:
            continue
            
        analyses = MORPHOLOGY.analyze(word)
        analysis_list = list(analyses) 
        
        if analysis_list:
            stem = analysis_list[0].get_stem()
            stems.append(stem)
        else:
            stems.append(word)
            
    return stems