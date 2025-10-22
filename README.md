# Akbank GenAI Bootcamp Projesi: Python Öğrenme Chatbotu

## [span_0](start_span)🚀 Proje Amacı[span_0](end_span)
Bu proje, RAG (Retrieval Augmented Generation) mimarisini kullanarak Python programlama dili hakkında doğru ve bağlamsal yanıtlar verebilen bir chatbot geliştirmeyi amaçlamaktadır. Proje, yeni başlayanların sıkça sorduğu soruları, güvenilir dokümanlardan bilgi çekerek hızlıca yanıtlamayı hedefler.

## [span_1](start_span)💾 Veri Seti Hakkında Bilgi[span_1](end_span)
* *Kaynak:* [Python Dokümantasyonu / Seçtiğiniz Kaynak]
* *Metodoloji:* [Nasıl toplandığı/hazırlandığı]
* *İçerik Özeti:* [Neler içerdiği]

## [span_2](start_span)🛠 Kullanılan Yöntemler ve Teknoloji[span_2](end_span)
* *[span_3](start_span)RAG Framework:* LangChain / Haystack[span_3](end_span)
* *[span_4](start_span)Generation Model:* Gemini API[span_4](end_span)
* *[span_5](start_span)Vektör Veritabanı:* ChromaDB[span_5](end_span)

## [span_6](start_span)📊 Elde Edilen Sonuçlar[span_6](end_span)
(Bu bölümü testler sonrası dolduracağız)

## [span_7](start_span)🔗 Web Arayüzü (Deploy Link)[span_7](end_span)
(Deploy işleminden sonra buraya linki yapıştıracağız)
*https://your-chatbot-deploy-link.com* 

---

## 2. ADIM: Veri Seti Hazırlama

Şimdi, chatbot'umuzun bilgi kaynağını oluşturalım.

### 2.1. Veri Kaynağı Belirleme
Python öğrenme için, **"Python 3.12.x Resmi Dokümantasyonunun Öğretici (Tutorial) kısmı"**nı veri kaynağı olarak seçelim. Bu, güvenilir ve kapsamlı bir kaynaktır.

### 2.2. Veri Seti Anlatımı Taslağı
[span_8](start_span)Bu metin, `README.md`'nin **"Veri Seti Hakkında Bilgi"** bölümüne ve projenin sunumuna eklenecektir[span_8](end_span).

markdown
*Veri Seti Anlatımı:*
Bu proje için veri seti, Python programlama dilinin en güncel (3.x) *resmi dokümantasyonundan* derlenmiştir. Özellikle, yeni başlayanlar için temel sözdizimi, veri yapıları ve modüler programlama gibi konuları kapsayan *"Python Tutorial"* bölümü kullanılmıştır.

*Toplanış / Hazırlanış Metodolojisi:*
Veri setini hazırlarken, resmi Python dokümantasyonu web sayfaları HTML veya PDF formatında indirildi. Daha sonra, bu dokümanlar pypdf kütüphanesi (veya benzeri bir doküman yükleyici) kullanılarak okunabilir metin parçalarına (chunks) dönüştürülmeye hazır hale getirildi. Bu yaklaşım, chatbot'un karmaşık HTML yapıları yerine temiz metin üzerinde çalışmasını sağlamaktadır.