import torch
from transformers import AutoTokenizer, AutoModel
import logging

# --- Modelleri Global'de Yükle ---
# Bu, sunucu her başladığında SADECE BİR KEZ çalışır.
# Her API isteğinde model yüklenmez, bu da sistemi çok hızlandırır.
MODEL_NAME = "dbmdz/bert-base-turkish-cased" # 

try:
    TOKENIZER = AutoTokenizer.from_pretrained(MODEL_NAME)
    MODEL = AutoModel.from_pretrained(MODEL_NAME)
    # Varsa GPU'ya taşı (daha hızlı çalışır)
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    MODEL.to(DEVICE)
    MODEL.eval() # Modeli "değerlendirme" moduna al (eğitim yapmayacağız)
    logging.info(f"'{MODEL_NAME}' modeli başarıyla yüklendi ve '{DEVICE}' cihazına taşındı.")
except Exception as e:
    logging.critical(f"KRİTİK HATA: BERT modeli yüklenemedi! {e}")
    TOKENIZER = None
    MODEL = None
# --- ---

def get_sentence_embedding(text):
    """
    Verilen metni BERT kullanarak anlamsal bir vektöre dönüştürür.
    """
    if not TOKENIZER or not MODEL:
        raise Exception("NLP modeli düzgün yüklenemedi.")
        
    # Metni BERT'in anlayacağı token ID'lerine çevir
    inputs = TOKENIZER(
        text, 
        return_tensors='pt', 
        truncation=True, 
        padding=True, 
        max_length=512
    ).to(DEVICE) # Tokenları da modele (GPU/CPU) gönder
    
    # Modeli çalıştır
    with torch.no_grad(): # Gradient hesaplamayı kapat (performans)
        outputs = MODEL(**inputs)
        
    # "Mean Pooling" stratejisi ile tüm token'ların ortalamasını alarak
    # cümlenin/paragrafın genel bir temsilini (vektörünü) elde et.
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze()
    
    # Vektörü CPU'ya geri taşı (sonraki hesaplamalar için)
    return embedding.cpu().numpy()