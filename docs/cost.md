# AI Enrichment Cost Analysis

**Date:** 2025-12-09

## Current Usage
- **Total Summaries Generated:** 108
- **Total Cost Incurred:** 16.2 TL
- **Cost per Summary:** ~0.15 TL

## Projection for All Events
- **Total Events in Database:** 4,415
- **Estimated Total Cost:** 4,415 * 0.15 TL ≈ **662.25 TL**

> [!NOTE]
> This is an estimate based on the current cost per event. Actual costs may vary slightly depending on token usage differences between events.

## Cost Optimization (Implemented)
To reduce the projected cost, we have implemented the following changes:

1.  **Skip Empty Events**: Events with no description and no reviews are now skipped automatically. This prevents paying for "0/10" quality summaries.
2.  **Disabled Embeddings**: Vector embedding generation (which doubles the API calls per event) has been disabled by default.

**New Projected Cost**:
- By disabling embeddings: **~50% savings** on API calls.
- By skipping empty events: Estimated **10-20%** additional savings depending on data quality.
- **Revised Estimate**: 662.25 TL -> **~300 TL** (or less) for the full database.

## AI Tournament Costs (Curated Collections)
Architecture: **Gemini 1.5 Flash** (Filtering) + **Gemini 3.0 Pro** (Reasoning).

### Per Tournament (e.g., "Best Value")
1.  **Stage 1: Filtering (Flash)**
    -   Input: ~4,000 events (~1.2M tokens)
    -   Price: ~$0.075 / 1M tokens
    -   Cost: **~$0.09** (3 TL)
2.  **Stage 2: Reasoning (Pro)**
    -   Input: ~200 finalists (~60k tokens)
    -   Price: ~$5.00 / 1M tokens
    -   Cost: **~$0.30** (10 TL)

**Total per Collection**: ~$0.39 (**13 TL**)
**Total Run (4 Collections)**: ~$1.56 (**53 TL**)
