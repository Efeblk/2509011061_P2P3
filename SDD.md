# Software Design Document (SDD)

**Project Name:** EventGraph - AI Powered Event Discovery & Recommendation Engine  
**Version:** 1.0.0  
**Date:** December 2025  

---

## 1. Executive Summary (Yönetici Özeti)

**EventGraph**, İstanbul'daki kültür-sanat etkinliklerini (konser, tiyatro, stand-up) dağıtık kaynaklardan toplayan, anlamsal ilişkilerini **Knowledge Graph** (Bilgi Çizgesi) üzerinde modelleyen ve **Large Language Model (LLM)** destekli niteliksel analiz yapan bir karar destek sistemidir.

Bu proje, geleneksel bilet listeleme (aggregation) sistemlerinin aksine, sadece "ne var?" sorusuna değil; *"Bu fiyat bu etkinliğe değer mi?"* ve *"Hangi etkinlik aslında bir gizli cevher (hidden gem)?"* sorularına cevap vermek üzere tasarlanmıştır. Sistem, etkinliklerin popülaritesini, sanatçı repütasyonunu ve kullanıcı yorumlarını analiz ederek **"Value-Based Ranking"** (Değer Odaklı Sıralama) sunar.

---

## 2. System Architecture (Sistem Mimarisi)

Sistem, **Microservices** prensiplerinden esinlenen, gevşek bağlı (loosely coupled) 4 ana katmandan oluşur. Bu yapı, her bileşenin bağımsız olarak geliştirilmesine ve ölçeklenmesine olanak tanır.

### 2.1. Tech Stack & Grading Criteria Mapping

| Component | Technology | Rationale & Grading Criteria |
| :--- | :--- | :--- |
| **Data Collection** | **Scrapy + Playwright** | Dinamik (JS render) siteleri taramak ve asenkron I/O hızı avantajı için. *(Scraping: +10 pts)* |
| **Database** | **FalkorDB (Docker)** | Etkinlik verilerinin ilişkisel doğasını (Sanatçı-Mekan-Etkinlik) modellemek için düşük gecikmeli Graph DB. *(Database: +20 pts)* |
| **AI Analysis** | **Gemini 1.5 Flash API** | Etkinlik içeriklerini analiz etmek, bağlamsal çıkarım (Reasoning) ve duygu analizi yapmak için. |
| **Backend Logic** | **Python 3.10+** | `Dataclasses`, `Typing` ve `Abstract Base Classes` ile güçlü OOP yapısı. *(OOP: +15 pts)* |
| **Infrastructure**| **Docker** | Geliştirme ortamının izolasyonu ve taşınabilirliği için. |

---

## 3. Object-Oriented Design (OOP Mimarisi)

Sistem, **SOLID** prensiplerine ve **Design Patterns** (Tasarım Kalıpları) kurallarına sıkı sıkıya bağlıdır.

### 3.1. The OGM Layer (Object Graph Mapper)
Veritabanı soyutlaması için **Active Record** benzeri bir yapı kurulmuştur.

* **`Protocol: GraphModel`**: Tüm veritabanı modellerinin uyması gereken "Interface" (Arayüz).
* **`Abstract Class: Node`**: Ortak özellikleri (`uuid`, `created_at`) kapsar.
* **`Dataclass: EventNode`**: Etkinlik verilerini tip güvenli (Type-Safe) bir şekilde tutar ve `save()` metodu ile Graph sorgularını yönetir.

### 3.2. The Scraper Layer (Template Method Pattern)
Kod tekrarını önlemek için **Inheritance** (Kalıtım) kullanılmıştır.

* **`Abstract Class: BaseEventSpider`**:
    * `Scrapy.Spider` sınıfından türetilir.
    * Playwright konfigürasyonlarını ve hata yakalama bloklarını yönetir.
* **`Concrete Classes`**: `BubiletSpider`, `BiletinoSpider`. Sadece hedef siteye özgü CSS/XPath seçicilerini barındırır.

### 3.3. The AI Layer (Strategy Pattern)
Sistemin farklı AI modellerine kolayca geçebilmesi için **Strategy Pattern** kullanılmıştır.

* **`Protocol: AIAnalyzer`**: `analyze_event()` metodunu zorunlu kılar.
* **`Class: GeminiAnalyzer`**: Google Gemini API implementasyonudur.

---

## 4. Database Schema (Graph Model)

Veriler SQL tabloları yerine, **FalkorDB** üzerinde düğümler (Nodes) ve kenarlar (Edges) olarak saklanır. Bu yapı, karmaşık sorguların (Örn: *"X sanatçısının daha önce sahne aldığı mekanlardaki Y türündeki etkinlikler"*) performanslı çalışmasını sağlar.

### Nodes (Düğümler)
* `(:Event {title, date, price, ai_score, ai_verdict})`
* `(:Venue {name, city, address, capacity})`
* `(:Artist {name, genre, reputation_score})`
* `(:Tag {name})` *(Örn: "Dram", "Must-See", "Award-Winning")*

### Relationships (İlişkiler)
* `(:Artist)-[:PERFORMS_AT]->(:Event)`
* `(:Event)-[:LOCATED_AT]->(:Venue)`
* `(:Event)-[:HAS_TAG]->(:Tag)`

---

## 5. Implementation Plan (Uygulama Adımları)

### Phase 1: Core Infrastructure
1.  FalkorDB Docker container'ının başlatılması (`docker run -p 6379:6379 falkordb/falkordb`).
2.  Python sanal ortamının kurulması ve `requirements.txt` (scrapy, playwright, redis, google-generativeai) yüklenmesi.

### Phase 2: Domain Modeling (OGM)
1.  `models.py` dosyasında `GraphModel` protokolünün ve `EventNode` dataclass'ının yazılması.
2.  Redis bağlantısının Singleton Pattern ile `database.py` üzerinde kurgulanması.

### Phase 3: AI Intelligence
1.  `ai_agent.py` modülünün yazılması.
2.  Gemini API için Prompt Engineering yapılması (JSON formatında çıktı garantilenmesi).
    * *Prompt Hedefi:* Etkinliğin "Fiyat/Performans" ve "Kültürel Değer" analizini yapıp 0-100 arası puanlamak.

### Phase 4: Data Pipeline
1.  `BaseEventSpider` soyut sınıfının oluşturulması.
2.  `pipelines.py` içerisinde veri akışının sağlanması: `Scraper -> AI Enrichment -> Graph DB Save`.

---

## 6. Sample Data Output

Sistemin analiz sonrası üreteceği zenginleştirilmiş veri örneği:

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Kel Diva - Haluk Bilginer",
  "price": 1200.0,
  "venue": "Zorlu PSM",
  "ai_analysis": {
    "score": 92,
    "verdict": "MUST_GO",
    "reasoning": "Haluk Bilginer ve Zuhal Olcay gibi usta oyuncuları bir araya getiren, absürd tiyatronun kült eseri. Yüksek fiyatına rağmen prodüksiyon kalitesi ve oyunculuk şöleni için değer.",
    "tags": ["Tiyatro", "Absürd", "Yıldız Kadro", "Kült Eser"]
  }
}