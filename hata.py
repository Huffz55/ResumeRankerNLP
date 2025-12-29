import numpy as np
from sklearn.metrics import ndcg_score

def calculate_with_real_scores(predicted_names, predicted_scores, ideal_names):
    """
    Sistemden gelen gerçek puanları (91.07 vb.) kullanarak NDCG hesaplar.
    """
    # 1. Temizlik
    preds = [p.strip().lower() for p in predicted_names]
    ideals = [i.strip().lower() for i in ideal_names]
    
    # 2. İdeal dünyaya göre "Gerçek Değer" (Relevance) atama
    # İdeal listendeki 1. adaya 5, sonuncuya 1 puan veriyoruz.
    relevance_map = {name: len(ideals) - i for i, name in enumerate(ideals)}
    
    # İdeal sıralama skoru (Mükemmel durumda olması gereken)
    # [5, 4, 3, 2, 1] gibi bir dizi oluşur
    true_relevance = np.array([[relevance_map.get(name, 0) for name in ideals]])
    
    # 3. Sistem puanlarını "İdeal Sıralama" düzenine göre dizme
    # NDCG fonksiyonu, senin puanlarını ideal listedeki aday sırasıyla karşılaştırır
    system_scores = []
    for target_name in ideals:
        if target_name in preds:
            idx = preds.index(target_name)
            system_scores.append(predicted_scores[idx])
        else:
            system_scores.append(0) # Eğer ideal listedeki aday sistemde yoksa
            
    system_scores = np.array([system_scores])

    # 4. NDCG Hesabı
    # true_relevance: Hedef puanlar (5, 4, 3...)
    # system_scores: Senin sisteminin o adaylara verdiği gerçek puanlar (91.07, 77.33...)
    ndcg = ndcg_score(true_relevance, system_scores)
    
    return ndcg

# --- SENARYO VERİLERİ (Senin Tablundan) ---
test_names = [
    "ŞevvalBuğdaCV - Şevval Buğda.pdf", "BedirhanCan_CvTur (4) - Bedirhan Can.pdf", 
    "cv (20) - Atilla Erdinç.pdf", "cvseyma - Şeyma K.pdf", 
    "Özgeçmiş (Rumeysa Akar)  - rumeysa akar.pdf"
]
test_scores = [77.33, 67.99, 63.91, 62.03, 55.89]

# Senin "Olması Gereken" İdeal Sıralaman
# Diyelim ki Senior'ın 1. sırada olması gerektiğini düşünüyorsun:
test_ideal = [
    "cv (20) - Atilla Erdinç.pdf", 
    "ŞevvalBuğdaCV - Şevval Buğda.pdf", 
    "BedirhanCan_CvTur (4) - Bedirhan Can.pdf", 
    "cvseyma - Şeyma K.pdf",
    "Özgeçmiş (Rumeysa Akar)  - rumeysa akar.pdf"
]

ndcg_sonuc = calculate_with_real_scores(test_names, test_scores, test_ideal)
print(f"Gerçek Skorlarla NDCG Başarısı: {ndcg_sonuc:.4f}")