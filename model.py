import torch
from sentence_transformers import SentenceTransformer
import logging
import numpy as np

# DÜZELTME 1: MODEL_NAME, modelin kendisi DEĞİL, adını içeren bir string (metin) olmalıdır.
MODEL_NAME = "emrecan/bert-base-turkish-cased-mean-nli-stsb-tr" 

# Modelin asıl yükleneceği değişkeni en başta 'None' olarak tanımlayalım
MODEL = None 

try:
    # Varsa GPU'ya taşı (daha hızlı çalışır)
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # YENİ MODEL YÜKLEME:
    # Model burada, 'MODEL_NAME' string'i kullanılarak SADECE BİR KEZ yüklenir.
    MODEL = SentenceTransformer(MODEL_NAME, device=DEVICE)
    
    MODEL.eval() # Modeli "değerlendirme" moduna al (eğitim yapmayacağız)
    logging.info(f"'{MODEL_NAME}' SBERT modeli başarıyla yüklendi ve '{DEVICE}' cihazına taşındı.")

except Exception as e:
    logging.critical(f"KRİTİK HATA: SBERT modeli yüklenemedi! {e}")
    MODEL = None # Hata olursa 'None' olarak kalır (Bu satır zaten vardı, doğru)

def get_sentence_embedding(text):
    """
    Verilen metni SBERT kullanarak anlamsal bir vektöre dönüştürür.
    (Eski BERT koduna göre çok daha basitleştirildi ve daha etkilidir)
    """
    if not MODEL:
        # Model yüklenememişse (örn. internet hatası veya yukarıdaki hata)
        # programın çökmesini engellemek için uyarı verip boş bir vektör döndürebiliriz
        # VEYA hatayı fırlatabiliriz (mevcut kodunuz gibi).
        raise Exception("NLP modeli (SBERT) düzgün yüklenemedi.")
        
    # SBERT (SentenceTransformer) kütüphanesi, tokenizasyon, padding,
    # modeli çalıştırma ve "pooling" (ortalama alma) işlemlerinin
    # tamamını 'encode' metodu ile tek başına yapar.
    
    embedding = MODEL.encode(
        text, 
        convert_to_numpy=True,  # Sonucu doğrudan numpy array'e çevir
        show_progress_bar=False # Logları temiz tutmak için (çoklu CV'de)
    )
    
    return embedding