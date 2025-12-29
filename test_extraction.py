import os
import docx
from utils import extract_text_from_cv  # Fonksiyonun burada olduğundan emin ol

# --- Manuel Metin Hazırlığı ---
# Buraya Word içinden kopyaladığın metni yapıştır
manuel_metin = """BEDİRHAN CAN
BİLGİSAYAR MÜHENDİSLİĞİ ÖĞRENCİSİ
  +90 553 211 9405	  bedirhancan2004@gmail.com linkedin/bedirhancan		github/bedirhancan

Sakarya Üniversitesi Bilgisayar Mühendisliği 4. sınıf öğrencisiyim. Kariyer yolumu şekillendirme sürecindeyim; veri bilimi, veri analizi, iş analistliği ve proje yönetimi alanlarında deneyim kazanarak ilerlemeyi hedeﬂiyorum. Python ve SQL üzerine çalışıyor, NumPy, Pandas ve Scikit-Learn gibi kütüphanelerle veri analizi ve makine öğrenmesi projeleri geliştiriyorum. TÜBİTAK 2209-B destekli süreç madenciliği araştırma projesinde görev alıyorum. Öğrenmeye açık, takım çalışmasına yatkın ve analitik düşünceye önem veren bir mühendis adayıyım.

Programlama Dilleri: Java, Python , C#
Veri Tabanı Yönetimi: MSSQL , PostgreSQL , Oracle SQL
Veri Analizi & Görselleştirme: Pandas, NumPy, Matplotlib, Scikit-Learn, Power BI Yabancı Dil: İngilizce (B1)


 
Yazılım Stajyeri
İskenderun Demir ve Çelik A.Ş
  Oracle 21c veri tabanı kurulumu, tablo tasarımı ve veri bütünlüğü kontrolleri.
 
08.2025 - 09.2025
 
Java JDBC ile CRUD işlemleri ve SOLID prensiplerine uygun katmanlı mimari uygulamaları. Spring Boot ile REST API geliştirme, Postman testleri ve JWT tabanlı yetkilendirme.
Apache POI ile Oracle verilerinden Excel raporlama uygulaması geliştirme.
 
Sponsorluk Sorumlusu
Sakarya Üniversitesi Veri Bilimi Topluluğu
  Sponsorluk görüşmeleri gerçekleştirdim ve bir etkinlik için konuşmacı ayarladım.   Topluluk faaliyetlerinin desteklenmesi için iş birliği fırsatları geliştirdim.
Donanım Stajyeri
ESBİ Bilişim & Telekomünikasyon
  Donanım bileşenlerinin kurulumu, bakımı ve arıza giderme süreçlerinde görev aldım.   Ekip çalışmasıyla sistem kurulum süreçlerine katkı sağladım.
  Temel teknik servis deneyimi edindim.
 
10.2024 - 06.2025




07.2024 - 08.2024
 

 
 
Sakarya Üniversitesi
Bilgisayar Mühendisliği (Lisans) GNO: 2.94 / 4.0
 
08.2022 - Devam Ediyor
 

 
TÜBİTAK 2209-B Araştırma Projesi (Devam Ediyor) :
“Süreç Madenciliği Yöntemleriyle Üretim Süreçlerinde İş Akışı Analizi: Performans ve Etkinlik Değerlendirmesi”
  Üretim süreçlerine dair verilerin analiz edilerek iş akışlarının modellenmesi ve darboğazların tespit edilmesi hedeﬂenmektedir.
  Süreç madenciliği tekniklerinin kullanıldığı proje şu an geliştirme aşamasındadır.
"""

# --- Güvenli Yol Tanımlama ---
# r harfi (raw string) OneDrive gibi boşluklu/özel karakterli yollarda hayat kurtarır
cv_yolu = r"CV_Klasoru/deneme_cv.docx"

print(f"Sistem şu an bu dosyayı arıyor: {os.path.abspath(cv_yolu)}")

if os.path.exists(cv_yolu):
    print("✅ Dosya fiziksel olarak bulundu!")
    cikartilan_metin = extract_text_from_cv(cv_yolu)
    
    if cikartilan_metin:
        print(f"✅ Metin başarıyla okundu. Karakter sayısı: {len(cikartilan_metin)}")
        
        # Karşılaştırma yap
        from difflib import SequenceMatcher
        def calculate_accuracy(a, b):
            return SequenceMatcher(None, " ".join(a.split()), " ".join(b.split())).ratio() * 100
        
        oran = calculate_accuracy(manuel_metin, cikartilan_metin)
        print(f"--- SONUÇ ---")
        print(f"Doğruluk Oranı: %{oran:.2f}")
    else:
        print("❌ Fonksiyon None veya boş metin döndürdü!")
else:
    print("❌ HATA: Python dosyayı hala göremiyor. Lütfen dosya ismindeki boşlukları veya karakterleri kontrol edin.")