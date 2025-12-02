# EventGraph - Quick Commands Cheat Sheet

## 🚀 First Time Setup

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
source venv/bin/activate     # Mac/Linux
# OR
venv\Scripts\activate        # Windows

# 3. Install dependencies
make install
# OR manually:
pip install -r requirements.txt
playwright install

# 4. Copy environment file
cp .env.example .env
```

---

## 🎯 Daily Workflow

### Start the System
```bash
make up
```
**What it does:**
- ✅ Starts FalkorDB in Docker
- ✅ Waits for database to be ready
- ✅ Initializes database (creates indexes)
- ✅ Shows you're ready to go!

### Scrape Events
```bash
make scrape
```
**What it does:**
- 🕷️ Runs Biletix spider
- 📄 Scrapes theater events
- ✅ Validates data
- 💾 Saves to FalkorDB

### View Results
```bash
make view
```
**What it does:**
- 📊 Shows database statistics
- 📋 Lists all scraped events
- 🎭 Displays event details

### Stop the System
```bash
make down
```
**What it does:**
- 🛑 Stops FalkorDB container
- 🧹 Cleans up Docker resources

---

## 📊 Complete Workflow Example

```bash
# Terminal session:
source venv/bin/activate     # Activate venv
make up                      # Start system
make scrape                  # Scrape events
make view                    # See results
make down                    # Stop when done
```

---

## 🔧 Additional Commands

### Database
```bash
make db-stats                # Show statistics
make db-shell                # Open Redis CLI
```

### Development
```bash
make format                  # Format code with black
make lint                    # Check code quality
make test                    # Run tests
make clean                   # Clean cache files
```

### Docker
```bash
make docker-up               # Start Docker services
make docker-down             # Stop Docker services
make docker-logs             # View Docker logs
```

### Help
```bash
make help                    # Show all commands
```

---

## 🐛 Troubleshooting

### "Command not found: make"
```bash
# Use commands directly:
docker-compose up -d falkordb
python src/main.py
scrapy crawl biletix
python test_scraper.py
```

### "Database connection failed"
```bash
# Check if Docker is running:
docker ps

# Restart database:
make down
make up
```

### "No module named 'src'"
```bash
# Make sure you're in project root:
pwd  # Should show: .../2509011061_P2P3

# Make sure venv is activated:
which python  # Should show path to venv
```

### "Playwright not installed"
```bash
playwright install chromium
```

---

## 🎓 What Each Command Really Does

| Command | Behind the Scenes |
|---------|-------------------|
| `make up` | `docker-compose up -d falkordb` → `sleep 5` → `python src/main.py` |
| `make scrape` | `scrapy crawl biletix` |
| `make view` | `python test_scraper.py` |
| `make down` | `docker-compose down` |

---

## 💡 Pro Tips

1. **Always activate venv first**: `source venv/bin/activate`
2. **Keep terminal open**: Don't close terminal with active venv
3. **Check status**: `docker-compose ps` to see if database is running
4. **View logs**: `docker-compose logs -f falkordb` to debug issues
5. **Clean start**: `make down && make up` for fresh start

---

## 🎯 Your First Run

```bash
# Complete first run:
python -m venv venv                    # Create venv (once)
source venv/bin/activate               # Activate
make install                           # Install packages (once)
cp .env.example .env                   # Create config (once)
make up                                # Start system
make scrape                            # Scrape events (takes ~30 sec)
make view                              # See results!
```

**Expected output:**
```
📊 Current Database Stats:
   Events: 10
   Total nodes: 10
   Memory: 2.5M

📋 Found 10 events:
1. Kel Diva
   Venue: Zorlu PSM
   Date: 2024-12-15
   Price: 850.0 TL
   ...
```

---

Ready to start? Run: `make up` 🚀
