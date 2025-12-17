
import asyncio
from src.services.venue_enricher import VenueEnricher
from src.models.venue import VenueNode

async def verify_enrichment():
    enricher = VenueEnricher()
    
    test_venues = [
        "Harbiye Cemil Topuzlu Açıkhava Tiyatrosu",
        "Zorlu PSM - Turkcell Sahnesi",
        "Maximum Uniq Açıkhava",
        "Kadıköy Sahne"
    ]
    
    print("--- Testing Venue Enrichment ---")
    
    for name in test_venues:
        print(f"\nProcessing: {name}")
        # Create a dummy node (don't save to DB to avoid pollution during test)
        venue = VenueNode(name=name, city="İstanbul")
        
        await enricher.enrich_venue(venue)
        
        print(f"  Is Outdoors: {venue.is_outdoors}")
        print(f"  Vibe: {venue.vibe}")
        print(f"  Capacity: {venue.capacity}")
        
        # Simple assertion logic
        if "Açıkhava" in name and not venue.is_outdoors:
            print("  ❌ ERROR: Should be outdoors!")
        elif "Zorlu" in name and venue.is_outdoors:
            print("  ❌ ERROR: Should be indoors!")
        else:
            print("  ✅ Logic seems correct.")

if __name__ == "__main__":
    asyncio.run(verify_enrichment())
