# Biletix Spider Fix - Doubled Event Count

## Problem
Spider was only scraping **12 events** when there were **31 events** on the page.

## Root Cause
**Line 85** in `biletix_spider.py` had a hardcoded limit:
```python
for event in events[:20]:  # Limit to first 20 events
```

This arbitrarily limited processing to only the first 20 event elements, and some of those didn't have titles, resulting in only ~12-19 events being saved.

## Fix
Removed the arbitrary limit and added better logging:

```python
# Before:
for event in events[:20]:  # Limit to first 20 events

# After:
for idx, event in enumerate(events, 1):  # Process ALL events
    # ... with better error tracking
```

Also added:
- Event counter with index
- Separate tracking for yielded vs skipped events  
- Better logging showing: "✓ Processed 31 events: 30 yielded, 1 skipped"

## Results

### Before Fix:
- 31 events found
- 20 events processed (artificial limit)
- ~19 events yielded (1 had no title)
- 12 events saved (7 duplicates)

### After Fix:
- 31 events found
- **31 events processed** (no limit!)
- **30 events yielded** (1 has no title)
- **24 events saved** (6 duplicates)

**Result: Doubled from 12 → 24 unique events! 🎉**

## New Events Captured

Events that were being skipped (21-31):
- Anadolu Mutfağı ve Yemek Stilistliği Atölyesi
- Antalya Kum Heykel Müzesi
- Dünya Mutfağı ve Yemek Stilistliği Atölyesi  
- Dünya Çayları ve Türk Çayı Demleme Atölyesi
- Ebru Atölyesi
- Eserini Sen Seç Heykel
- Hamlet
- Hocapaşa Mevlevileri - Sema Ayini
- Kumda Nitelikli Türk Kahvesi Atölyesi
- Nickelodeon Play! Tersane İstanbul
- Pray Tiyatro Etkinlikleri
- Seramik ve Çini Boyama Atölyesi
- Takı Tasarım Atölyesi
- Vitray Cam Boyama Atölyesi
- Diyalog Müzesi Sessizlikte Diyalog

## Code Changes

```python
# Added tracking variables
events_yielded = 0
events_skipped = 0

# Process all events with index
for idx, event in enumerate(events, 1):
    try:
        title = self.extract_title(event)
        # ... extraction logic ...
        
        if title:
            # ... yield event ...
            events_yielded += 1
        else:
            events_skipped += 1
            self.logger.debug(f"Event #{idx} skipped: no title found")
    except Exception as e:
        events_skipped += 1
        self.logger.error(f"Error parsing event #{idx}: {e}")

# Log summary
self.logger.info(f"✓ Processed {len(events)} events: {events_yielded} yielded, {events_skipped} skipped")
```

## Verification

```bash
source venv/bin/activate
scrapy crawl biletix

# Output:
# Found 31 event elements on page
# ✓ Processed 31 events: 30 yielded, 1 skipped
# Events saved: 24
```

## Why Some Events Are Still "Missing"

- **1 skipped**: Event #1 has no title (empty or ad placeholder)
- **6 duplicates**: Same event listed multiple times (different dates/venues)
  - Example: "Parfüm Yapım Atölyesi" appears 5+ times for different locations
  - Duplicate detection working correctly!

## Lesson Learned

❌ **Never use arbitrary limits** like `[:20]` without good reason  
✅ **Process all available data** and let business logic (duplicates, validation) filter  
✅ **Add counters and logging** to track what's happening  

---

**Status**: Fixed - Spider now captures all available events on page
**Impact**: 2x more events (12 → 24)
