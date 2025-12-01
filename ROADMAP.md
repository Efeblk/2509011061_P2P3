# EventGraph - Project Roadmap

**Version:** 1.0.0
**Last Updated:** December 2025
**Project Duration:** 8-10 Weeks

---

## Overview

This roadmap outlines the development timeline for EventGraph, an AI-powered event discovery and recommendation engine. The project is divided into 4 major phases with clear milestones and deliverables.

---

## Phase 1: Foundation & Infrastructure Setup
**Duration:** Week 1-2
**Status:** Not Started

### Objectives
Set up the development environment and core infrastructure components.

### Tasks

#### Week 1: Environment Setup
- [ ] **1.1** Initialize Git repository and project structure
  - Create directory structure (`src/`, `tests/`, `docs/`, `config/`)
  - Set up `.gitignore` for Python projects
  - Create initial `README.md`

- [ ] **1.2** Docker Infrastructure
  - Write `docker-compose.yml` for FalkorDB
  - Configure FalkorDB container (port 6379)
  - Test connection to FalkorDB instance
  - Create Docker network for services

- [ ] **1.3** Python Environment
  - Set up virtual environment (Python 3.10+)
  - Create `requirements.txt` with core dependencies:
    - `scrapy>=2.11.0`
    - `playwright>=1.40.0`
    - `redis>=5.0.0`
    - `google-generativeai>=0.3.0`
    - `pydantic>=2.0.0`
    - `python-dotenv>=1.0.0`
  - Install Playwright browsers (`playwright install`)

#### Week 2: Configuration & Database Setup
- [ ] **1.4** Configuration Management
  - Create `.env.example` template
  - Implement config loader using `python-dotenv`
  - Set up logging configuration
  - Create settings module for environment variables

- [ ] **1.5** Database Connection Layer
  - Implement Singleton pattern for Redis/FalkorDB connection
  - Create `database.py` with connection pooling
  - Write connection health check utilities
  - Implement error handling and retry logic

- [ ] **1.6** Testing Infrastructure
  - Set up `pytest` framework
  - Create test database configuration
  - Write initial connection tests
  - Set up CI/CD pipeline basics (GitHub Actions)

### Deliverables
- ✅ Fully configured development environment
- ✅ Working FalkorDB instance accessible via Docker
- ✅ Database connection layer with tests
- ✅ Project documentation structure

---

## Phase 2: Domain Modeling & OOP Architecture
**Duration:** Week 3-4
**Status:** Not Started

### Objectives
Build the core object-oriented architecture and graph database models.

### Tasks

#### Week 3: OGM Layer (Object Graph Mapper)
- [ ] **2.1** Protocol Definitions
  - Create `protocols.py` with `GraphModel` protocol
  - Define required methods: `save()`, `delete()`, `find()`
  - Add type hints and documentation

- [ ] **2.2** Base Node Class
  - Implement abstract `Node` class
  - Add common fields: `uuid`, `created_at`, `updated_at`
  - Implement UUID generation logic
  - Add serialization methods (`to_dict()`, `from_dict()`)

- [ ] **2.3** Domain Models
  - Create `EventNode` dataclass with fields:
    - title, date, price, description, url
    - ai_score, ai_verdict, ai_reasoning
  - Create `VenueNode` dataclass (name, city, address, capacity)
  - Create `ArtistNode` dataclass (name, genre, reputation_score)
  - Create `TagNode` dataclass (name, category)

- [ ] **2.4** Relationship Modeling
  - Define edge types in `relationships.py`
  - Implement `PERFORMS_AT`, `LOCATED_AT`, `HAS_TAG` relationships
  - Create helper methods for relationship creation

#### Week 4: Graph Query Layer
- [ ] **2.5** Query Builder
  - Create Cypher query builder class
  - Implement CRUD operations for each node type
  - Add pagination support
  - Implement complex query methods (find events by artist, venue, etc.)

- [ ] **2.6** Graph Traversal Methods
  - Implement graph navigation utilities
  - Create methods for finding related entities
  - Add filtering and sorting capabilities
  - Optimize query performance

- [ ] **2.7** Unit Testing
  - Write comprehensive tests for all models
  - Test CRUD operations
  - Test relationship creation and queries
  - Achieve >80% code coverage

### Deliverables
- ✅ Complete OGM layer with all domain models
- ✅ Graph query builder with CRUD operations
- ✅ Comprehensive unit test suite
- ✅ API documentation for models

---

## Phase 3: AI Intelligence Integration
**Duration:** Week 5-6
**Status:** Not Started

### Objectives
Integrate Google Gemini API and build AI-powered event analysis system.

### Tasks

#### Week 5: AI Architecture
- [ ] **3.1** AI Strategy Pattern
  - Create `AIAnalyzer` protocol in `protocols.py`
  - Define `analyze_event()` method signature
  - Add result validation schema

- [ ] **3.2** Gemini Integration
  - Create `ai_agent.py` module
  - Implement `GeminiAnalyzer` class
  - Set up API key management
  - Implement rate limiting and retry logic

- [ ] **3.3** Prompt Engineering
  - Design system prompt for event analysis
  - Create structured output format (JSON schema)
  - Define scoring criteria:
    - Price/Performance ratio (0-50 points)
    - Cultural value (0-50 points)
  - Add verdict categories: `MUST_GO`, `WORTH_IT`, `MAYBE`, `SKIP`

- [ ] **3.4** Response Parsing
  - Implement JSON response parser
  - Add validation using Pydantic models
  - Handle API errors and malformed responses
  - Create fallback scoring mechanism

#### Week 6: AI Enrichment Pipeline
- [ ] **3.5** Batch Processing
  - Implement batch analysis for multiple events
  - Add concurrent processing with rate limiting
  - Create progress tracking
  - Implement caching for analyzed events

- [ ] **3.6** Tag Extraction
  - Extract genre/category tags from AI analysis
  - Create tag normalization logic
  - Implement tag graph integration
  - Build tag suggestion system

- [ ] **3.7** Testing & Validation
  - Test AI responses with sample event data
  - Validate scoring consistency
  - Test error handling scenarios
  - Performance benchmarking

### Deliverables
- ✅ Fully functional Gemini API integration
- ✅ Event analysis pipeline with scoring
- ✅ Tag extraction and classification
- ✅ AI module tests and documentation

---

## Phase 4: Data Collection & Pipeline
**Duration:** Week 7-8
**Status:** Not Started

### Objectives
Build web scraping infrastructure and complete data processing pipeline.

### Tasks

#### Week 7: Scraper Architecture
- [ ] **4.1** Base Spider (Template Method Pattern)
  - Create `BaseEventSpider` abstract class
  - Implement Playwright middleware integration
  - Add common error handling
  - Create retry logic for failed requests

- [ ] **4.2** Site-Specific Spiders
  - Implement `BubiletSpider`:
    - Define CSS/XPath selectors
    - Parse event listings
    - Extract event details (title, date, price, venue)
  - Implement `BiletinoSpider`:
    - Define selectors for Biletino structure
    - Handle pagination
    - Extract artist information

- [ ] **4.3** Data Validation
  - Create `validators.py` module
  - Implement field validators (price, date format)
  - Add duplicate detection logic
  - Create data cleaning utilities

#### Week 8: Pipeline Integration
- [ ] **4.4** Scrapy Pipeline
  - Create `pipelines.py` with processing stages:
    1. Data validation
    2. AI enrichment
    3. Graph database persistence
  - Implement pipeline ordering
  - Add error handling and logging

- [ ] **4.5** Entity Resolution
  - Implement fuzzy matching for venues/artists
  - Create deduplication logic
  - Merge duplicate entities
  - Update relationships

- [ ] **4.6** Scheduling & Automation
  - Set up Scrapy crawl scheduler
  - Create cron jobs for regular updates
  - Implement incremental crawling
  - Add monitoring and alerting

- [ ] **4.7** End-to-End Testing
  - Test complete pipeline: Scrape → Analyze → Store
  - Validate data integrity in graph database
  - Performance testing with large datasets
  - Error recovery testing

### Deliverables
- ✅ Working web scrapers for 2+ ticket platforms
- ✅ Complete data processing pipeline
- ✅ Automated scheduling system
- ✅ Integration test suite

---

## Phase 5: API & User Interface (Optional Enhancement)
**Duration:** Week 9-10
**Status:** Future Work

### Objectives
Build REST API and simple web interface for querying recommendations.

### Tasks

#### Week 9: REST API
- [ ] **5.1** FastAPI Setup
  - Create API project structure
  - Implement endpoints:
    - `GET /events` - List events with filters
    - `GET /events/{id}` - Event details
    - `GET /recommendations` - Personalized suggestions
    - `GET /search` - Search events
  - Add request/response models
  - Implement pagination

- [ ] **5.2** Query Optimization
  - Add caching layer (Redis)
  - Implement database query optimization
  - Add search indexing
  - Performance tuning

#### Week 10: Simple Frontend
- [ ] **5.3** Web Interface
  - Create basic HTML/CSS/JS interface
  - Implement event listing page
  - Add filtering and sorting
  - Display AI verdicts and scores

- [ ] **5.4** Deployment
  - Containerize all services
  - Create production `docker-compose.yml`
  - Write deployment documentation
  - Set up basic monitoring

### Deliverables
- ✅ REST API with documentation
- ✅ Simple web interface
- ✅ Deployment-ready Docker setup

---

## Milestones & Checkpoints

### Milestone 1: Infrastructure Complete (End of Week 2)
- Database running and accessible
- Project structure established
- Development environment ready

### Milestone 2: Core Models Complete (End of Week 4)
- All domain models implemented
- Graph queries working
- Test coverage >80%

### Milestone 3: AI Integration Complete (End of Week 6)
- Gemini API functional
- Event scoring operational
- Tag extraction working

### Milestone 4: MVP Ready (End of Week 8)
- End-to-end pipeline functional
- Data collection automated
- System ready for demonstration

### Milestone 5: Production Ready (End of Week 10)
- API deployed
- User interface available
- Documentation complete

---

## Risk Management

### Technical Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| API rate limits (Gemini) | High | Implement caching, batch processing, fallback scoring |
| Website structure changes | Medium | Abstract selectors, regular monitoring, easy spider updates |
| Graph database performance | Medium | Query optimization, indexing, connection pooling |
| Scrapy blocking | High | Rotate user agents, add delays, use Playwright stealth mode |

### Timeline Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Scope creep | High | Strict adherence to MVP features, defer enhancements |
| Learning curve (FalkorDB) | Medium | Allocate extra time in Phase 2, use documentation |
| Third-party API changes | Medium | Version pinning, monitoring, quick response plan |

---

## Success Criteria

### Functional Requirements
- ✅ System successfully scrapes events from 2+ platforms
- ✅ AI analysis provides consistent scores (0-100)
- ✅ Graph database stores and queries relationships efficiently
- ✅ Pipeline processes 100+ events without failure

### Technical Requirements
- ✅ Code follows SOLID principles
- ✅ Test coverage >75%
- ✅ OOP design patterns properly implemented
- ✅ Docker containers run without configuration issues

### Grading Criteria Alignment
- ✅ **Scraping:** Advanced scraping with Playwright (+10 pts)
- ✅ **Database:** FalkorDB graph implementation (+20 pts)
- ✅ **OOP:** Strong class hierarchy, protocols, design patterns (+15 pts)
- ✅ **Integration:** All components working together seamlessly

---

## Next Steps

1. **Immediate Actions:**
   - Review and approve this roadmap
   - Set up development environment
   - Create project repository
   - Schedule Phase 1 kickoff

2. **Weekly Reviews:**
   - Monday: Sprint planning
   - Friday: Progress review and blocker resolution

3. **Documentation:**
   - Maintain development journal
   - Update roadmap status weekly
   - Document design decisions

---

## Resources & References

- [FalkorDB Documentation](https://docs.falkordb.com/)
- [Scrapy Documentation](https://docs.scrapy.org/)
- [Playwright Python](https://playwright.dev/python/)
- [Google Gemini API](https://ai.google.dev/docs)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)

---

**Note:** This roadmap is a living document and should be updated as the project progresses. Timeline estimates are based on full-time development; adjust accordingly for part-time work.
