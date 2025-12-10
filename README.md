# EventGraph 🎯

Your AI-powered event discovery engine for Istanbul.
Finds the best events from Biletix and Biletinial, filters out the noise using LLMs, and curates collections like "Date Night" or "Best Value".

## ✨ Features

- **Multi-Source Scraping**: Unified data from Biletix & Biletinial.
- **AI Filtering**: Uses fast models (Gemini Flash / Llama 3.2) to categorize intent.
- **Reasoning Engine**: Uses smart models (Gemini Pro) to rank events and generate summaries.
- **Graph Database**: Powered by FalkorDB for relationship mapping (Event -> Venue -> Category).
- **Natural Language Search**: Ask "Where should I go for a cheap date?" and get curated answers.

---

## 🛠️ Prerequisites

- **Python 3.11+**
- **Docker** (for the database)
- **Google Gemini API Key** (for reliable reasoning)
- *(Optional)* **Ollama** (for local/free inference)

---

## 📦 Installation

### 1. Create Virtual Environment
Isolate dependencies to keep your system clean.
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies & Database
Use the `make` shortcut to handle everything.
```bash
make setup
```
*This installs python packages, Playwright browsers, and starts the FalkorDB container.*

### 3. Configure AI
Edit the `.env` file created during setup.

**Option A: Cloud (Recommended)**
```env
# .env
AI_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here
```

**Option B: Local (Free)**
If you have [Ollama](https://ollama.com) installed:
```bash
ollama pull llama3.2
```
```env
# .env
AI_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
```

---

## 🚀 Usage Workflow

### 1. Scrape Events 🕷️
Fetch the latest data from web sources.
```bash
make scrape
```
*Tip: This runs both Biletix and Biletinial scrapers.*

### 2. Run AI Analysis 🧠
Process the raw events to categorize, rank, and summarize them.
```bash
make ai-collections
```
*This runs the "Tournament" system where AI picks the best events for different categories.*

### 3. Ask for Recommendations 💬
Launch the CLI to interact with your data.
```bash
make ask
```
*Example queries:*
> "Find me a jazz concert this weekend."
> "I want a cheap stand-up show on the Asian side."

---

## 🔧 Advanced Commands

| Command | Description |
|---------|-------------|
| `make view` | View stats about scraped events in the database |
| `make verify` | Run data quality checks (missing prices, dates, etc.) |
| `make ai-enrich` | Generate summaries for all events (slow) |
| `make ai-audit` | Audit the quality of AI outputs |
| `make clean-data` | Wipe database contents (keeps table structure) |
| `make fclean` | **Hard Reset**: Deletes venv, DB volumes, and logs |

## 📁 Project Structure

- `src/scrapers/`: Spiders for Biletix/Biletinial (Scrapy)
- `src/ai/`: Clients for Gemini and Ollama
- `src/models/`: Data classes for Graph Nodes (Event, Venue)
- `src/scripts/`: Utilities for running tournaments and enrichment
- `ask.py`: The CLI entry point
