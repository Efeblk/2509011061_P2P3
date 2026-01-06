# EventGraph 🎭

**Student ID**: 2509011061  
**Project**: P2 (Web Scraping) + P3 (Data Analysis & Visualization)

AI-powered event discovery engine for Istanbul. Scrapes real-world messy web data, cleans it, analyzes it with statistical methods, and visualizes everything in a modern React dashboard.

![React Dashboard](https://img.shields.io/badge/React-Dashboard-61DAFB?style=for-the-badge&logo=react)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python)
![FalkorDB](https://img.shields.io/badge/FalkorDB-Graph_DB-red?style=for-the-badge)

---

## 🎯 Bonus Points Summary

| Category | Implementation | Points |
|----------|----------------|--------|
| **Visualization** | React.js + Recharts + Framer Motion | **+15** |
| **Dataset** | Scraped messy web data from Biletinial | **+10** |
| **Analysis** | Statistical analysis with scipy (ANOVA, normality tests, anomaly detection) | **+15** |
| **TOTAL** | | **+40** |

---

## 🚀 Quick Start

```bash
# 1. Create virtual environment
python3 -m venv venv && source venv/bin/activate

# 2. Install & setup
make setup

# 3. Scrape events
make scrape

# 4. Launch web dashboard
make web
# → Dashboard: http://localhost:5173
# → API: http://localhost:8000
```

---

## 📊 Visualization: React.js Dashboard (+15 points)

Modern web-based visualization with **React.js**, **Recharts**, and **Framer Motion**.

### Features:
- 📈 **Category Price Analysis** - Bar charts comparing mean vs median prices
- 🥧 **Event Distribution** - Interactive pie chart with hover effects
- 📉 **Data Quality Gauge** - Semi-circle gauge showing data completeness
- 📊 **Statistical Report** - Live stats: mean, median, σ, skewness, kurtosis, IQR
- 🧪 **Normality Test Results** - Kolmogorov-Smirnov test visualization
- 🔍 **Anomaly Detection** - IQR/Z-score outlier summary
- 🔄 **Live Progress Monitor** - Real-time scraping progress at `/progress`

### Launch:
```bash
make web  # Starts both backend (FastAPI) and frontend (Vite + React)
```

**Technologies**: React 18, Recharts, Framer Motion, Tailwind CSS, FastAPI

---

## 📦 Dataset: Scraped Messy Web Data (+10 points)

Data scraped from [Biletinial](https://www.biletinial.com) using **Scrapy + Playwright**.

### Raw Data Challenges:
| Issue | Example |
|-------|---------|
| Turkish dates | `"20 Ocak 2025"`, `"Bugün"`, `"Yarın"` |
| HTML entities | `&nbsp;`, `&#39;`, `&quot;` |
| Price formats | `"1.500,00 TL"`, `"ÜCRETSİZ"`, null |
| Duplicates | Same event with different IDs |
| Missing fields | ~30% missing descriptions |

### Data Cleaning Process:

#### 1. Date Normalization
```python
# Turkish months → ISO 8601
MONTH_MAP = {"ocak": 1, "şubat": 2, "mart": 3, ...}
# "20 Ocak 2025" → "2025-01-20T00:00:00"
```

#### 2. Price Extraction
```python
# Handle Turkish format and free events
"1.500,00 TL" → 1500.0
"ÜCRETSİZ" → 0.0
"150 - 250 TL" → 150.0 (minimum)
```

#### 3. Text Cleaning
```python
text = html.unescape(text)  # Remove entities
text = ' '.join(text.split())  # Normalize whitespace
```

#### 4. Deduplication
```python
# Fingerprint: (title, date, venue)
# Result: ~25,000 raw → ~18,000 unique events
```

#### 5. Category Normalization
```python
# 47 raw categories → 14 normalized categories
"Konser", "Canlı Müzik" → "Concert"
"Tiyatro", "Oyun" → "Theater"
```

**Files**: `src/scrapers/spiders/biletinial_spider.py`, `src/scrapers/pipelines.py`

---

## 📈 Analysis: Advanced Statistical Analysis (+15 points)

Comprehensive statistical analysis using **scipy**, **numpy**, and **pandas**.

### Methods Implemented:

| Method | Description | Result |
|--------|-------------|--------|
| **Descriptive Stats** | n, μ, M, σ, range | n=18,003, μ=981 TL, M=950 TL |
| **Quartile Analysis** | Q1, Q2, Q3, IQR | Q1=400, Q3=1250, IQR=850 |
| **Skewness** | Distribution asymmetry | γ₁ = 19.11 (right-skewed) |
| **Kurtosis** | Tail heaviness | γ₂ = 563.04 (leptokurtic) |
| **Normality Test** | Kolmogorov-Smirnov | p < 0.001 (non-normal) |
| **Anomaly Detection** | IQR + Z-score methods | ~8% anomaly rate |

### Run Analysis:
```bash
make analyze  # Prints statistical report to terminal
make web      # Shows analysis in dashboard (live)
```

**Files**: `src/analysis/statistics.py`, `src/analysis/anomaly_detector.py`

---

## 🧹 Data Cleaning Summary

| Metric | Before | After |
|--------|--------|-------|
| Events scraped | ~25,000 | 18,003 unique |
| Date format | Inconsistent Turkish | ISO 8601 |
| HTML entities | 35% with entities | 0% |
| Duplicates | ~7,000 | 0 |
| Categories | 47 variations | 14 normalized |

---

## 📁 Project Structure

```
├── frontend/              # React.js dashboard
│   ├── src/
│   │   ├── App.jsx        # Main dashboard
│   │   └── ProgressPage.jsx # Live progress monitor
├── src/
│   ├── scrapers/          # Scrapy spiders
│   │   ├── spiders/       # biletinial_spider.py
│   │   └── pipelines.py   # Data cleaning
│   ├── analysis/          # Statistical analysis
│   │   ├── statistics.py  # scipy analysis
│   │   └── anomaly_detector.py
│   ├── api/               # FastAPI backend
│   │   └── main.py
│   ├── ai/                # AI enrichment (Ollama)
│   └── models/            # Graph DB models
├── Makefile               # All commands
└── README.md
```

---

## 🔧 Commands

| Command | Description |
|---------|-------------|
| `make setup` | Install dependencies + start DB |
| `make scrape` | Scrape events from Biletinial |
| `make web` | Launch React dashboard |
| `make analyze` | Run statistical analysis |
| `make ai-enrich` | Generate AI summaries |
| `make view` | View database stats |
| `make fclean` | Full reset |

---

## 🛠️ Tech Stack

- **Scraping**: Scrapy + Playwright
- **Database**: FalkorDB (Redis-based graph DB)
- **Backend**: FastAPI + Uvicorn
- **Frontend**: React 18 + Vite + Recharts + Framer Motion
- **Analysis**: scipy, numpy, pandas
- **AI**: Ollama (Llama 3.2, mxbai-embed-large)

---

**Fall 2024**
