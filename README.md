# EventGraph 🎯

Your AI-powered event discovery engine for Istanbul.
Finds the best events from Biletix and Biletinial, filters out the noise using LLMs, and curates collections like "Date Night" or "Best Value".

## ✨ Features

- **Multi-Source Scraping**: Unified data from Biletix & Biletinial.
- **AI Filtering**: Uses fast models (Gemini Flash / Llama 3.2) to categorize intent.
- **Reasoning Engine**: Uses smart models (Gemini Pro) to rank events and generate summaries.
- **Graph Database**: Powered by FalkorDB for relationship mapping (Event -> Venue -> Category).
- **Natural Language Search**: Ask "Where should I go for a cheap date?" and get curated answers.

> [!WARNING]
> **Service Status Notice**: 
> - **Biletix**: Currently **disabled** due to poor data context quality.
> - **Google Gemini**: Currently **disabled** due to high operational costs.
> *These services may be restored in future updates.*

---

## 🛠️ Prerequisites

- **Python 3.11+**
- **Docker** (for the database)
- **Ollama** (Required for local inference)
- *(Optional)* **Google Gemini API Key** (for cloud reasoning)

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

### 3. Configure AI (Default: Local Privacy)
The project is configured to use **Ollama** by default for 100% local, private processing.

1.  **Install & Serve Ollama**:
    ```bash
    # Install from ollama.com, then run:
    ollama serve
    ```

2.  **Pull Required Models**:
    ```bash
    ollama pull llama3.2
    ollama pull mxbai-embed-large
    ollama pull mistral-nemo
    ```

3.  **Check `.env`**:
    Ensure `AI_LOCAL=ollama` is set (this is the default).

*(Optional)* To use Google Gemini instead:
1.  Get an API Key from [Google AI Studio](https://makersuite.google.com/app/apikey).
2.  Set `GEMINI_API_KEY=your_key` and `AI_LOCAL=gemini` in `.env`.

**Hardware Recommendations for Local AI (Ollama):**
- **Minimum**: 4GB RAM, 2 CPU cores → Set `AI_CONCURRENCY=2`
- **Recommended**: 8GB RAM, 4 CPU cores → Set `AI_CONCURRENCY=4`
- **Optimal**: 16GB+ RAM, 8+ CPU cores → Set `AI_CONCURRENCY=8`

*Higher concurrency = faster processing but more memory usage.*

### 4. Configure Scraping
Adjust scraping performance in the `.env` file.

```env
# .env
SCRAPY_CONCURRENT_REQUESTS=16  # Number of concurrent HTTP requests
SCRAPY_DOWNLOAD_DELAY=1        # Delay between requests (in seconds)
PLAYWRIGHT_HEADLESS=true       # Run browser in headless mode
```

**Scraping Performance Recommendations:**
- **Conservative**: `SCRAPY_CONCURRENT_REQUESTS=8`, `SCRAPY_DOWNLOAD_DELAY=2` → Slower but gentler on servers
- **Balanced**: `SCRAPY_CONCURRENT_REQUESTS=16`, `SCRAPY_DOWNLOAD_DELAY=1` → Good balance of speed and stability
- **Aggressive**: `SCRAPY_CONCURRENT_REQUESTS=32`, `SCRAPY_DOWNLOAD_DELAY=0.5` → Fastest but may trigger rate limits

*Higher concurrent requests = faster scraping but more network/CPU usage and higher chance of being blocked.*

---

## 🚀 Usage Workflow

### 1. Scrape Events 🕷️
Fetch the latest data from web sources.
```bash
make scrape
```
*Tip: This runs both Biletix and Biletinial scrapers.*

### 2. Enrich Events with AI 🧠
Generate intelligent summaries for all events using AI.
```bash
make ai-enrich
```
*This analyzes event descriptions, Biletinial AI summaries, and top 5 user reviews to generate:*
- Quality scores (0-10)
- Importance level (must-see, iconic, popular, niche)
- Sentiment analysis
- Key highlights and concerns
- Best audience fit

**What gets analyzed:**
- Event description (up to 1000 chars)
- Biletinial's AI summary (if available)
- Top 5 user reviews (up to 500 chars each)

**Performance:**
- With Ollama (llama3.2): ~2-3 events/second (depends on hardware)
- With Gemini API: ~5-10 events/second (depends on rate limits)

### 3. Run AI Collections 🏆
Curate special collections using AI tournaments.
```bash
make ai-collections
```
*This runs the "Tournament" system where AI picks the best events for different categories like "Date Night" or "Best Value".*

### 4. Ask for Recommendations 💬
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
| `make ai-enrich` | Generate AI summaries for events without summaries |
| `make ai-enrich LIMIT=100` | Process only first 100 events (for testing) |
| `make ai-enrich FORCE=--force` | Process even low-quality events (no description/reviews) |
| `make ai-enrich-all` | Regenerate ALL summaries (overwrites existing) |
| `make ai-view` | View quality audit of AI-generated summaries |
| `make clean-ai` | Delete all AI summaries from database |
| `make clean-data` | Wipe database contents (keeps table structure) |
| `make fclean` | **Hard Reset**: Deletes venv, DB volumes, and logs |

## 🧠 AI Enrichment Details

### Summary Generation Process

Each event is analyzed using:
1. **Event Description** (up to 1000 characters)
2. **Biletinial AI Summary** (professional curated description)
3. **Top 5 User Reviews** (up to 500 characters each)

The AI generates:
- **Quality Score**: 0-10 rating based on content quality
- **Importance Level**: must-see, iconic, popular, niche, seasonal, emerging
- **Value Rating**: excellent, good, fair, expensive
- **Sentiment Summary**: One-sentence review sentiment
- **Key Highlights**: Array of 3 main positives
- **Concerns**: Potential issues or criticisms
- **Best For**: Target audience types
- **Vibe**: 2-3 words describing atmosphere
- **Uniqueness**: What makes this event special
- **Flags**: Educational value, tourist attraction, bucket list worthy


**Performance Tips:**
- Lower `AI_CONCURRENCY` if you get memory errors
- Increase `AI_CONCURRENCY` if CPU usage is low (<50%)
- Use `LIMIT=100` to test settings before full run
- Monitor system resources: `htop` or `top`

## 📚 Documentation
- [**Scraped Websites**](docs/scraped_websites.md): Details on supported sources and categories.

## 📁 Project Structure

- `src/scrapers/`: Spiders for Biletix/Biletinial (Scrapy)
- `src/ai/`: Clients for Gemini and Ollama
- `src/models/`: Data classes for Graph Nodes (Event, Venue)
- `src/scripts/`: Utilities for running tournaments and enrichment
- `docs/`: Documentation and guides
- `ask.py`: The CLI entry point
