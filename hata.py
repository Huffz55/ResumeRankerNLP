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
    "50328713_tr.pdf", 
    "27152464_tr.pdf", 
    "10624813_tr.pdf", 
    "12472574_tr.pdf", 
    "12011623_tr.pdf", 
    "32985311_tr.pdf", 
    "82246962_tr.pdf", 
    "20566550_tr.pdf"
]

test_scores = [71.20, 66.88, 66.03, 63.39, 62.64, 62.30, 59.55, 53.72]

# Senin "Olması Gereken" İdeal Sıralaman
# Diyelim ki Senior'ın 1. sırada olması gerektiğini düşünüyorsun:
test_ideal = [
    "50328713_tr.pdf",  # 1. Python, SQL, Git ve Linux yetkinliği tam. Kaggle projeleri var.
    "12011623_tr.pdf",  # 2. Bilgisayar Bilimleri mezunu. Web Scraping (API hazırlığı için temel) ve SQL tecrübesi güçlü.
    "32985311_tr.pdf",  # 3. Yazılım Analisti stajı, Python ve SQL sertifikaları ile tam bir "Junior" profili.
    "20566550_tr.pdf",  # 4. Mühendislik mezunu, Oracle SQL uzmanlığı ve Scrum bilgisiyle kurumsal yapıya uygun.
    "82246962_tr.pdf",  # 5. Python'u otomasyon için kullanıyor, Linux ve SQL Server bilgisi var.
    "27152464_tr.pdf",  # 6. 14+ yıl deneyimli QA Manager. Python biliyor ama pozisyon için çok kıdemli (Overqualified).
    "12472574_tr.pdf",  # 7. 8+ yıl test liderliği deneyimi. API ve HTML bilgisi var ancak geliştirici odaklı değil.
    "10624813_tr.pdf"   # 8. 25+ yıl deneyimli üst düzey yönetici. Modern Python/SQL ilanının çok uzağında bir profil.
]

ndcg_sonuc = calculate_with_real_scores(test_names, test_scores, test_ideal)
print(f"Gerçek Skorlarla NDCG Başarısı: {ndcg_sonuc:.4f}")