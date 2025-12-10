# EventGraph 🎯

Your AI-powered event discovery engine for Istanbul.
Finds the best events from Biletix and Biletinial, filters out the noise, and curates collections like "Date Night" or "Best Value".

## 🚀 Quick Start (Fresh Install)

Since you just cleaned everything, here is how to get running in 3 steps:

### 1. Setup
Install dependencies and start the database.
```bash
make setup
```

### 2. Populate Data
Scrape events and run the AI tournament engine to rank them.
```bash
make scrape           # Fetch fresh data (takes ~5-10 mins)
make ai-collections   # AI ranks events into collections (takes ~2 mins)
```

### 3. Ask AI
Query the system for recommendations.
```bash
make ask
```
*Example: "Find me a cheap concert this weekend" or "Plan a date night"*

---

## 🛠️ Commands

| Command | Description |
|---------|-------------|
| `make setup` | Install deps & start DB (first run only) |
| `make scrape` | Scrape all events from web |
| `make ai-collections` | Run AI tournaments to categorize/rank events |
| `make ask` | Launch the search CLI |
| `make view` | See raw data statistics |
| `make fclean` | **Hard Reset**: Wipes DB, venv, and logs |

## 🧠 tech Stack
- **AI**: Gemini 2.5 Flash (Filtering) + Gemini 2.5 Pro (Reasoning)
- **DB**: FalkorDB (Graph Database)
- **Scraper**: Scrapy + Playwright
- **Language**: Python 3.11+
