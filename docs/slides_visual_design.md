# EventGraph - Slide Görsel Tasarımları

## SLIDE 1 - Ana Başlık

### Görsel Düzen:

**Başlık (Üstte, Ortalı):**
* "EVENTGRAPH"
* Çok büyük, kalın, koyu mavi renk

**Alt Başlık (Başlığın altında):**
* "Cultural Event Discovery Platform"
* Orta boy, gri renk

**Ortada (Center):**
* Modern graf/ağ görseli veya
* Terminal screenshot (events being scraped) veya
* Soyut bağlantılı düğümler görseli

**Altta (3 kart yan yana):**

Sol Kart:
* "1,400+" (Çok büyük rakam)
* "Events Scraped" (Küçük yazı)
* İkon: 📊

Orta Kart:
* "Graph" (Büyük yazı)
* "Database" (Küçük yazı)
* İkon: 🗄️

Sağ Kart:
* "AI" (Büyük yazı)
* "Powered" (Küçük yazı)
* İkon: 🤖

**En alt (Footer):**
* "[İsmin] | [Ders Kodu] | Aralık 2024"
* Küçük, ortalı, gri

---

## SLIDE 2 - Mimari ve Teknoloji

### Görsel Düzen:

**Başlık (Üstte, Sol):**
* "Architecture & Technology Stack"
* Büyük, koyu mavi

**Alt Başlık:**
* "Data Flow Pipeline"
* Orta boy, gri

**Ortada (Yatay akış diyagramı - soldan sağa):**

Kutu 1 (Açık mavi):
* İkon: 🌐
* "Websites"
* Alt yazı: "Biletix, Biletinial"

Ok → (Üstünde: "Scrapy + Playwright")

Kutu 2 (Mor):
* İkon: 🕷️
* "Scrapy +"
* "Playwright"

Ok → (Üstünde: "Validation")

Kutu 3 (Turuncu):
* İkon: ⚙️
* "Data"
* "Pipelines"

Ok → (Üstünde: "Store")

Kutu 4 (Yeşil):
* İkon: 🗄️
* "FalkorDB"
* Alt yazı: "Graph DB"

Aşağı ok ↓ (Kutu 3'ten, üstünde: "Enrich")

Kutu 5 (Kırmızı/Pembe - Kutu 3'ün altında):
* İkon: 🤖
* "Google"
* "Gemini"

**Altta (2 sütun madde işaretleri):**

Sol Sütun:
* ✓ Scrapy + Playwright
* ✓ Python 3.10+

Sağ Sütun:
* ✓ FalkorDB (Graph)
* ✓ Google Gemini AI

---

## SLIDE 3 - OOP Tasarımı (GÜNCELLENMIŞ - 4 Node)

### Görsel Düzen:

**Başlık (Üstte, Sol):**
* "Object-Oriented Architecture"
* Büyük, koyu mavi

**Alt Başlık:**
* "Clean Code with Type Safety"
* Orta boy, gri

**Ortada (Dikey ağaç diyagramı - yukarıdan aşağıya):**

Seviye 1 (En üst):
* Kesikli kenarlı kutu (Açık mor)
* "GraphModel"
* Alt etiket: "(Protocol - Interface)"
* İçinde: "save(), delete(), to_dict(), find_by_uuid()"

Aşağı ok ↓ (Etiket: "implements")

Seviye 2 (Orta):
* Kalın kenarlı kutu (Açık mavi)
* "Node"
* Köşede "ABC" rozeti
* Alt etiket: "(Abstract Base Class)"
* İçinde: "uuid, created_at, updated_at"

Aşağı ok ↓ DÖRDE ayrılıyor (Etiket: "inherits")

Seviye 3 (Alt - 4 kutu yan yana, eşit aralıklı):

Kutu 1 (Yeşil):
* "EventNode"
* İkon: 📅
* İçinde: "title, venue, date, price"

Kutu 2 (Yeşil):
* "EventContentNode"
* İkon: 💬
* İçinde: "text, rating, author"

Kutu 3 (Yeşil):
* "AISummaryNode"
* İkon: 🤖
* İçinde: "quality_score, sentiment"

Kutu 4 (Yeşil):
* "CollectionNode"
* İkon: 📚
* İçinde: "name, category"

**Altta (3x2 grid - özellikler):**

Satır 1:
* ✓ Protocols (Type Safety)
* ✓ Abstract Classes (ABC)

Satır 2:
* ✓ Dataclasses (@dataclass)
* ✓ Full Type Hints (Optional[str])

Satır 3:
* ✓ Custom ORM Methods
* ✓ 4 Node Types (Event, Content, AI, Collection)

---

## SLIDE 4 - Graph Relationships (YENİ - Relations Gösterimi)

### Görsel Düzen:

**Başlık (Üstte, Sol):**
* "Graph Database Relationships"
* Büyük, koyu mavi

**Alt Başlık:**
* "Connected Data Model"
* Orta boy, gri

**Ortada (Graph diyagramı - ilişkiler gösterimi):**

Merkez - Event Node (Büyük, yeşil kutu):
* 📅 **Event**
* "title, venue, date, price"

Event'ten çıkan 3 ilişki oku:

Sağ üst → EventContent Node (Mavi kutu):
* Relationship: **HAS_CONTENT** →
* 💬 **EventContent**
* "text, rating, author"

Sağ → AISummary Node (Turuncu kutu):
* Relationship: **HAS_AI_SUMMARY** →
* 🤖 **AISummary**
* "quality_score, sentiment"

Sağ alt → Collection Node (Mor kutu):
* Relationship: ← **CONTAINS** (ters yönlü!)
* 📚 **Collection**
* "name, category"

**Altta (2 sütun - relationship özellikleri):**

Sol Sütun - "Relationship Types":
* → HAS_CONTENT (1:many)
* → HAS_AI_SUMMARY (1:1)
* ← CONTAINS (many:many)

Sağ Sütun - "Graph Advantages":
* ✓ Fast traversal
* ✓ Complex queries
* ✓ Recommendation ready

### ASCII Görselleştirme - Slide 4:

```
┌─────────────────────────────────────────────────────────┐
│ Graph Database Relationships                            │
│ Connected Data Model                                    │
│                                                          │
│              ┌──────────────────┐                       │
│              │ 💬 EventContent  │                       │
│              │ text, rating     │                       │
│              └──────────────────┘                       │
│                       ▲                                  │
│                       │                                  │
│                 HAS_CONTENT                              │
│                       │                                  │
│         ┌─────────────┴─────────────┐                   │
│         │     📅 Event (Center)     │                   │
│         │  title, venue, date       │ ──HAS_AI──►      │
│         │  price, source            │   SUMMARY        │
│         └─────────────┬─────────────┘       │           │
│                       │                     ▼           │
│                  CONTAINS                ┌──────────┐   │
│                    (from)                │🤖 AISumm.│   │
│                       │                  │quality   │   │
│                       ▼                  └──────────┘   │
│              ┌──────────────────┐                       │
│              │ 📚 Collection    │                       │
│              │ name, category   │                       │
│              └──────────────────┘                       │
│                                                          │
│  Relationship Types:        Graph Advantages:           │
│  → HAS_CONTENT (1:many)     ✓ Fast traversal           │
│  → HAS_AI_SUMMARY (1:1)     ✓ Complex queries          │
│  ← CONTAINS (many:many)     ✓ Recommendation ready     │
└─────────────────────────────────────────────────────────┘
```

---

## SLIDE 5 - AI Integration (YENİ - AI Kullanımı)

### Görsel Düzen:

**Başlık (Üstte, Sol):**
* "AI-Powered Event Analysis"
* Büyük, koyu mavi

**Alt Başlık:**
* "Google Gemini Integration"
* Orta boy, gri

**Sol taraf (Input - Event Data):**

Kutu başlık: "Raw Event Data"
* 📅 Event: "Sezen Aksu Konseri"
* 📍 Venue: "Zorlu PSM"
* 💰 Price: 450 TL
* 📝 Description: "Türk pop müziğinin efsane ismi Sezen Aksu, unutulmaz şarkılarıyla Zorlu PSM'de..."

**Ortada (AI Process):**

Büyük ok → ile bağlı

Kutu (Turuncu/pembe arka plan):
* 🤖 **Google Gemini API**
* "gemini-1.5-flash"

İşlemler:
* ✓ Sentiment Analysis
* ✓ Quality Scoring
* ✓ Category Detection
* ✓ Summary Generation

**Sağ taraf (Output - AI Summary):**

Kutu başlık: "AI Summary Result"

AISummary Node içeriği:
* 🎯 **Quality Score:** 8.5/10
* 📊 **Importance:** "iconic"
* 💎 **Value Rating:** "good"
* ❤️ **Sentiment:** "Highly anticipated, emotional performance"
* 🎭 **Best For:** "Turkish pop fans, nostalgic audiences"
* ✨ **Uniqueness:** "Legendary artist, rare performance"

**Altta (Metrikler - 2 sütun):**

Sol Sütun - "AI Metrics":
* 📈 1,400+ events analyzed
* ⚡ ~2 sec per event
* 💰 $0.0004 per analysis

Sağ Sütun - "Use Cases":
* ✓ Auto-categorization
* ✓ Quality filtering
* ✓ Smart recommendations

### ASCII Görselleştirme - Slide 5:

```
┌─────────────────────────────────────────────────────────────┐
│ AI-Powered Event Analysis                                   │
│ Google Gemini Integration                                   │
│                                                              │
│  ┌──────────────┐       ┌──────────┐      ┌──────────────┐ │
│  │ Raw Event    │       │          │      │ AI Summary   │ │
│  │ Data         │  ───► │ 🤖 Gemini│ ───► │ Result       │ │
│  │              │       │          │      │              │ │
│  │ 📅 Sezen Aksu│       │ gemini-  │      │🎯 Score: 8.5 │ │
│  │ 📍 Zorlu PSM │       │ 1.5-flash│      │📊 iconic     │ │
│  │ 💰 450 TL    │       │          │      │❤️ Sentiment: │ │
│  │ 📝 Desc...   │       │ ✓ Sent.  │      │  "Highly..." │ │
│  │              │       │ ✓ Quality│      │🎭 Best for:  │ │
│  │              │       │ ✓ Categ. │      │  "Pop fans"  │ │
│  │              │       │ ✓ Summary│      │✨ Unique     │ │
│  └──────────────┘       └──────────┘      └──────────────┘ │
│                                                              │
│  AI Metrics:              Use Cases:                        │
│  📈 1,400+ analyzed       ✓ Auto-categorization            │
│  ⚡ ~2 sec per event      ✓ Quality filtering              │
│  💰 $0.0004 per analysis  ✓ Smart recommendations          │
└─────────────────────────────────────────────────────────────┘
```

---

## SLIDE 6 - Test ve Sonuçlar

### Görsel Düzen:

**Başlık (Üstte, Sol):**
* "Quality Assurance & Results"
* Büyük, koyu mavi

**Alt Başlık:**
* "Production-Ready System"
* Orta boy, gri

**Üstte (3 büyük metrik kartı yan yana):**

Kart 1 (Yeşil arka plan):
* İkon: ✓ (Çok büyük)
* Rakam: "43" (Çok büyük)
* Etiket: "Unit Tests"

Kart 2 (Yeşil arka plan):
* İkon: ✓ (Çok büyük)
* Rakam: "100%"
* Etiket: "Pass Rate"

Kart 3 (Mavi arka plan):
* İkon: ⚙️
* Yazı: "CI/CD"
* Etiket: "GitHub Actions"

**Ortada (Başlık + 2 sütun checklist):**

Başlık: "Production Ready Features"

Sol sütun:
* ✓ Type checking (mypy)
* ✓ Zero duplicate events
* ✓ Automated data pipeline

Sağ sütun:
* ✓ GitHub Actions CI/CD
* ✓ Multiple Python versions
* ✓ Real production data (1,400+ events)

**Altta (Açık mavi kutu):**

Başlık: "Future Roadmap"

Madde işaretleri (mavi oklar):
* → Add more event sources (Passo, Mobilet)
* → Build REST API for querying
* → Implement personalized recommendations
* → Mobile application

**En altta (Büyük, ortalı):**
* "Thank You!" (Çok büyük, kalın)
* "Questions?" (Orta boy, altında)

---

## ASCII Görselleştirme - Slide 3 (Güncellenmiş)

```
┌───────────────────────────────────────────────────────────┐
│ Object-Oriented Architecture                              │
│ Clean Code with Type Safety                               │
│                                                            │
│              ┌─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┐                  │
│              │   GraphModel         ABC│                  │
│              │   (Protocol)            │                  │
│              │   save(), delete()      │                  │
│              └─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┘                  │
│                        │                                   │
│                   implements                               │
│                        ▼                                   │
│              ┌──────────────────┐                         │
│              │      Node        │                         │
│              │  (Abstract Base) │  ABC                    │
│              │  uuid, created   │                         │
│              └──────────────────┘                         │
│                        │                                   │
│                   inherits                                 │
│         ┌──────┬───────┴────────┬──────┐                 │
│         ▼      ▼                ▼       ▼                 │
│    ┌───────┐ ┌──────┐  ┌─────────┐ ┌────────┐           │
│    │📅     │ │💬    │  │🤖       │ │📚      │           │
│    │Event  │ │Event │  │AI       │ │Collect-│           │
│    │Node   │ │Cont. │  │Summary  │ │ion     │           │
│    │       │ │Node  │  │Node     │ │Node    │           │
│    └───────┘ └──────┘  └─────────┘ └────────┘           │
│                                                            │
│ ✓ Protocols   ✓ ABC        ✓ Dataclasses                 │
│ ✓ Type Hints  ✓ ORM        ✓ 4 Node Types                │
└───────────────────────────────────────────────────────────┘
```

---

## Genel Notlar

**Tüm Slide'larda Tutarlı Olması Gerekenler:**

Renkler:
* Başlıklar: Koyu mavi (#1e3a8a)
* Arka plan: Beyaz
* Vurgular: Yeşil (#10b981)
* Kartlar: Açık gri (#f3f4f6)

Font:
* Başlık: 44-48pt, kalın
* Alt başlık: 24-28pt, normal
* Gövde: 16-20pt, normal
* Kod: Monospace, 14-16pt

Header (Her slide üstünde - isteğe bağlı):
* Sol: "EventGraph" (küçük)
* Sağ: "Slide X/6" (küçük)

Footer (Her slide altında):
* "[İsmin] | [Ders Kodu] | Aralık 2024"
* Küçük, ortalı, gri

---

## Slide 3 Önemli Değişiklikler

### Eski (2 Node):
- EventNode
- EventContentNode

### Yeni (4 Node) ✅:
1. **EventNode** - Temel event bilgileri (title, venue, date, price)
2. **EventContentNode** - Event içerikleri (text, rating, author)
3. **AISummaryNode** - AI analizleri (quality_score, sentiment)
4. **CollectionNode** - Küratörlü listeler (name, category)

### Neden Bu Değişiklik Önemli:
- Daha karmaşık OOP yapısı gösteriyor
- 4 farklı use case için özelleşmiş node'lar
- Gerçek production kodunu yansıtıyor
- Öğretmene "bu adam ciddi OOP yapmış" izlenimi veriyor

### Görsel Değişiklik:
- Ok 2'ye değil **4'e** ayrılıyor
- 4 yeşil kutu yan yana (eşit aralıklı)
- Her kutuda ikon farklı: 📅 💬 🤖 📚
- Alt özet: "4 Node Types" olarak güncellenmiş

Başarılar! 🚀
