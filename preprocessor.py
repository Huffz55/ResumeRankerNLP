import docx  # En üste ekle
from zemberek import TurkishMorphology
import re
import logging

logger = logging.getLogger(__name__)

# --- ZEMBEREK (SADECE TÜRKÇE CÜMLELER İÇİN) ---
try:
    logger.info("Zemberek başlatılıyor...")
    MORPHOLOGY = TurkishMorphology.create_with_defaults()
    logger.info("✅ Zemberek yüklendi.")
except Exception as e:
    logger.warning(f"Zemberek yüklenemedi: {e}")
    MORPHOLOGY = None


def preprocess_text(text):
    """
    Skill'leri bozmadan temizleme yapar.
    """
    if not text:
        return ""

    text = text.lower()

    # 🔒 c#, .net, ci/cd korunur
    text = re.sub(r'[^\w\s\.\#\/\-]', ' ', text)

    text = re.sub(r'\s+', ' ', text).strip()
    return text


def get_stems(text):
    """
    ⚠️ SADECE TÜRKÇE kelimeler için kullan.
    Skill çıkarımı için KULLANMA.
    """
    if not MORPHOLOGY:
        return text.split()

    stems = []
    for word in text.split():
        if not word.isalpha():  # python, c#, .net vs geç
            stems.append(word)
            continue

        try:
            analysis = MORPHOLOGY.analyze_and_disambiguate(word)
            lemma = analysis.best_analysis().get_lemma()
            stems.append(lemma)
        except Exception:
            stems.append(word)

    return stems




