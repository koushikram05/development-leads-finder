"""
Main development opportunity pipeline
Orchestrates scraping, enrichment, and classification
"""

import sys
import argparse
from datetime import datetime
from typing import List, Dict, Any

from app.utils import (
    setup_logging, 
    save_to_csv, 
    save_to_json,
    deduplicate_listings,
    get_timestamp
)
from app.scraper import LLMSearch, RedfinScraper, RealtorScraper, ZillowScraper
from app.enrichment import GISEnrichment
from app.classifier import LLMClassifier


class DevelopmentPipeline:
    """
    Main pipeline for finding development opportunities
    """
    
    def __init__(self):
        self.logger = setup_logging('dev_pipeline')
        self.logger.info("=" * 60)
        self.logger.info("Development Opportunity Pipeline Initialized")
        self.logger.info("=" * 60)
        
        # Initialize components
        self.llm_search = LLMSearch()
        self.redfin_scraper = RedfinScraper()
        self.realtor_scraper = RealtorScraper()
        self.zillow_scraper = ZillowScraper()
        self.enricher = GISEnrichment()
        self.classifier = LLMClassifier()
        
    def run(
        self,
        search_query: str = "Newton MA teardown single family home large lot",
        location: str = "Newton, MA",
        use_scrapers: bool = False,
        max_pages: int = 3,
        enrich_data: bool = True,
        classify_data: bool = True,
        min_dev_score: float = 50.0
    ) -> Dict[str, Any]:
        """
        Run the complete pipeline
        
        Args:
            search_query: Search query for properties
            location: Location to search
            use_scrapers: Whether to use direct scrapers (in addition to search)
            max_pages: Max pages per scraper
            enrich_data: Whether to enrich with GIS data
            classify_data: Whether to classify opportunities
            min_dev_score: Minimum development score for filtering
            
        Returns:
            Dictionary with pipeline results and statistics
        """
        start_time = datetime.now()
        self.logger.info(f"Starting pipeline: {search_query}")
        
        # Send notification that scan has started
        try:
            from app.integrations.alert_manager import AlertManager
            alert_manager = AlertManager(email_enabled=True, slack_enabled=True)
            alert_manager.notify_scan_started(run_type="manual")
        except Exception as e:
            self.logger.debug(f"Could not send scan started notification: {e}")
        
        # Stage 1: Data Collection
        self.logger.info("\n" + "=" * 60)
        self.logger.info("STAGE 1: DATA COLLECTION")
        self.logger.info("=" * 60)
        
        all_listings = []
        
        # Use LLM Search (primary method - fast and reliable)
        self.logger.info("Searching via SerpAPI...")
        search_queries = [
            search_query,
            f"{location} teardown opportunity",
            f"{location} builder special large lot",
            f"{location} development opportunity single family"
        ]
        search_listings = self.llm_search.search_multiple_queries(search_queries, location)
        all_listings.extend(search_listings)
        self.logger.info(f"SerpAPI: Found {len(search_listings)} listings")
        
        # Optionally use direct scrapers
        if use_scrapers:
            city, state = self._parse_location(location)
            
            # Redfin
            try:
                self.logger.info("Scraping Redfin...")
                redfin_listings = self.redfin_scraper.search_location(
                    city, state, max_pages=max_pages
                )
                all_listings.extend(redfin_listings)
                self.logger.info(f"Redfin: Found {len(redfin_listings)} listings")
            except Exception as e:
                self.logger.error(f"Redfin scraping failed: {e}")
            
            # Realtor.com
            try:
                self.logger.info("Scraping Realtor.com...")
                realtor_listings = self.realtor_scraper.search_location(
                    city, state, max_pages=max_pages
                )
                all_listings.extend(realtor_listings)
                self.logger.info(f"Realtor.com: Found {len(realtor_listings)} listings")
            except Exception as e:
                self.logger.error(f"Realtor.com scraping failed: {e}")
            
            # Zillow (note: may be blocked)
            try:
                self.logger.info("Scraping Zillow...")
                zillow_listings = self.zillow_scraper.search_location(
                    city, state, max_pages=max_pages
                )
                all_listings.extend(zillow_listings)
                self.logger.info(f"Zillow: Found {len(zillow_listings)} listings")
            except Exception as e:
                self.logger.error(f"Zillow scraping failed: {e}")
        
        # Deduplicate
        all_listings = deduplicate_listings(all_listings, key='address')
        self.logger.info(f"\nTotal unique listings collected: {len(all_listings)}")
        
        # Save raw listings
        if all_listings:
            save_to_csv(all_listings, 'raw_listings.csv')
        
        # Stage 2: Data Enrichment
        if enrich_data and all_listings:
            self.logger.info("\n" + "=" * 60)
            self.logger.info("STAGE 2: DATA ENRICHMENT")
            self.logger.info("=" * 60)
            
            all_listings = self.enricher.enrich_listings_batch(all_listings)
            self.logger.info(f"Enriched {len(all_listings)} listings with GIS data")
        
        # Stage 3: Classification
        classified_listings = []
        development_opportunities = []
        
        if classify_data and all_listings:
            self.logger.info("\n" + "=" * 60)
            self.logger.info("STAGE 3: CLASSIFICATION")
            self.logger.info("=" * 60)
            
            classified_listings = self.classifier.classify_listings_batch(all_listings)
            self.logger.info(f"Classified {len(classified_listings)} listings")
            
            # Filter for development opportunities
            development_opportunities = self.classifier.filter_development_opportunities(
                classified_listings,
                min_score=min_dev_score,
                include_potential=True
            )
            self.logger.info(f"Found {len(development_opportunities)} development opportunities")
        
        # Stage 4: Save Results & Upload to Google Sheets
        self.logger.info("\n" + "=" * 60)
        self.logger.info("STAGE 4: SAVING RESULTS & UPLOADING TO SHEETS")
        self.logger.info("=" * 60)
        
        if classified_listings:
            save_to_csv(classified_listings, 'classified_listings.csv')
            save_to_json(classified_listings, 'classified_listings.json')
            
            # Upload to Google Sheets
            try:
                from app.integrations.google_sheets_uploader import GoogleSheetsUploader
                
                self.logger.info(f"Initializing Google Sheets uploader...")
                sheets_uploader = GoogleSheetsUploader()
                self.logger.info(f"✓ Uploader ready, uploading {len(classified_listings)} listings...")
                
                # Upload to Google Sheet with location filtering
                success = sheets_uploader.upload_listings(
                    listings=classified_listings,
                    sheet_name='DevelopmentLeads',
                    location_filter=location,
                    sort_by='development_score'
                )
                
                if success:
                    self.logger.info(f"✓ Google Sheets upload successful ({len(classified_listings)} listings)")
                else:
                    self.logger.warning(f"Google Sheets upload returned False")
                
            except FileNotFoundError as e:
                self.logger.warning(f"Google Sheets not configured: {e}")
                self.logger.info("→ To enable: Download google_credentials.json (see TASK1_GOOGLE_SHEETS_SETUP.md)")
            except Exception as e:
                self.logger.error(f"Google Sheets upload failed: {e}")
                import traceback
                self.logger.error(traceback.format_exc())
            
            # Stage 5: Send Alerts for High-Value Opportunities
            self.logger.info("\n" + "=" * 60)
            self.logger.info("STAGE 5: SENDING ALERTS")
            self.logger.info("=" * 60)
            
            try:
                from app.integrations.alert_manager import AlertManager
                
                alert_manager = AlertManager(email_enabled=True, slack_enabled=True)
                
                # Filter high-value opportunities (score >= 70)
                high_value = [l for l in classified_listings if float(l.get('development_score', 0)) >= 70.0]
                
                if high_value:
                    self.logger.info(f"Found {len(high_value)} high-value opportunities (score >= 70)")
                    
                    alert_results = alert_manager.alert_on_opportunities(
                        opportunities=high_value,
                        recipient_email=None,  # Uses SENDER_EMAIL from env
                        run_type="manual"
                    )
                    
                    if alert_results.get('email'):
                        self.logger.info(f"✓ Email alert sent for {len(high_value)} opportunities")
                    if alert_results.get('slack'):
                        self.logger.info(f"✓ Slack alert sent for {len(high_value)} opportunities")
                    
                    if not alert_results.get('email') and not alert_results.get('slack'):
                        self.logger.warning("Alerts not configured - skipped email/Slack")
                else:
                    self.logger.info("No high-value opportunities found - sending scan completion summary")
                    
                    # Send scan completed notification (summary with no new values found)
                    summary_results = alert_manager.notify_scan_completed(
                        total_found=len(all_listings),
                        opportunities_found=len(development_opportunities),
                        high_value_found=0,
                        run_type="manual"
                    )
                    
                    if summary_results.get('email'):
                        self.logger.info(f"✓ Scan completion email sent")
                    if summary_results.get('slack'):
                        self.logger.info(f"✓ Scan completion Slack notification sent")
                    
            except Exception as e:
                self.logger.warning(f"Alert sending failed (non-critical): {e}")
        
        # Stage 6: Save to Historical Database
        self.logger.info("\n" + "=" * 60)
        self.logger.info("STAGE 6: SAVING TO HISTORICAL DATABASE")
        self.logger.info("=" * 60)
        
        try:
            from app.integrations.database_manager import HistoricalDatabaseManager
            
            db = HistoricalDatabaseManager()
            
            # Record this scan run
            run_id = db.record_scan_run(
                search_query=search_query,
                location=location,
                run_type="manual",
                total_found=len(all_listings),
                opportunities_found=len(development_opportunities),
                high_value_found=len(high_value) if classified_listings else 0,
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )
            
            # Save all classified listings to database
            if classified_listings:
                db_stats = db.save_listings(classified_listings, run_id, auto_classify=True)
                self.logger.info(f"✓ Database saved: {db_stats['new_listings']} new, "
                               f"{db_stats['updated_listings']} updated, "
                               f"{db_stats['classifications_added']} classifications")
            
            # Show database statistics
            db_stats = db.get_statistics(days=30)
            self.logger.info(f"✓ Historical database now contains:")
            self.logger.info(f"  - {db_stats['total_listings']} total properties")
            self.logger.info(f"  - {db_stats['high_value_opportunities']} high-value opportunities (last 30 days)")
            self.logger.info(f"  - {db_stats['recent_runs']} scan runs (last 30 days)")
            
        except Exception as e:
            self.logger.warning(f"Database save failed (non-critical): {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
        
        if development_opportunities:
            save_to_csv(development_opportunities, 'development_opportunities.csv')
            save_to_json(development_opportunities, 'development_opportunities.json')
        
        # Pipeline statistics
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        stats = {
            'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration_seconds': duration,
            'total_listings': len(all_listings),
            'classified_listings': len(classified_listings),
            'development_opportunities': len(development_opportunities),
            'search_query': search_query,
            'location': location
        }
        
        # Classification breakdown
        if classified_listings:
            label_counts = {}
            for listing in classified_listings:
                label = listing.get('label', 'unknown')
                label_counts[label] = label_counts.get(label, 0) + 1
            stats['classification_breakdown'] = label_counts
        
        self._print_summary(stats, development_opportunities[:10])
        
        return stats
    
    def _parse_location(self, location: str) -> tuple:
        """Parse location string into city and state"""
        parts = location.split(',')
        if len(parts) >= 2:
            city = parts[0].strip()
            state = parts[1].strip().split()[0]  # Get state code
            return city, state
        return "Newton", "MA"
    
    def _print_summary(self, stats: Dict[str, Any], top_opportunities: List[Dict[str, Any]]):
        """Print pipeline summary"""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("PIPELINE SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Query: {stats['search_query']}")
        self.logger.info(f"Location: {stats['location']}")
        self.logger.info(f"Duration: {stats['duration_seconds']:.1f} seconds")
        self.logger.info(f"\nResults:")
        self.logger.info(f"  Total Listings: {stats['total_listings']}")
        self.logger.info(f"  Classified: {stats['classified_listings']}")
        self.logger.info(f"  Development Opportunities: {stats['development_opportunities']}")
        
        if 'classification_breakdown' in stats:
            self.logger.info(f"\nClassification Breakdown:")
            for label, count in stats['classification_breakdown'].items():
                self.logger.info(f"  {label}: {count}")
        
        if top_opportunities:
            self.logger.info(f"\nTop 10 Development Opportunities:")
            for i, opp in enumerate(top_opportunities, 1):
                self.logger.info(f"\n  {i}. {opp.get('address', 'Unknown')}")
                self.logger.info(f"     Score: {opp.get('development_score', 0):.1f}/100")
                self.logger.info(f"     Price: ${opp.get('price', 0):,.0f}" if opp.get('price') else "     Price: N/A")
                self.logger.info(f"     Lot: {opp.get('lot_size', 0):,.0f} sqft" if opp.get('lot_size') else "     Lot: N/A")
                self.logger.info(f"     Year: {opp.get('year_built', 'N/A')}")
                self.logger.info(f"     Reason: {opp.get('explanation', '')[:100]}")
        
        self.logger.info("\n" + "=" * 60)
        self.logger.info("Pipeline completed successfully!")
        self.logger.info("=" * 60)


def main():
    """
    Command-line interface for the pipeline
    """
    parser = argparse.ArgumentParser(
        description='Development Opportunity Lead Scraper'
    )
    
    parser.add_argument(
        'query',
        nargs='?',
        default='Newton MA teardown single family home large lot underbuilt',
        help='Search query for properties'
    )
    
    parser.add_argument(
        '--location',
        default='Newton, MA',
        help='Location to search (e.g., "Newton, MA")'
    )
    
    parser.add_argument(
        '--use-scrapers',
        action='store_true',
        help='Enable direct website scrapers (slower, may be blocked)'
    )
    
    parser.add_argument(
        '--max-pages',
        type=int,
        default=3,
        help='Maximum pages per scraper'
    )
    
    parser.add_argument(
        '--no-enrich',
        action='store_true',
        help='Skip GIS enrichment'
    )
    
    parser.add_argument(
        '--no-classify',
        action='store_true',
        help='Skip classification'
    )
    
    parser.add_argument(
        '--min-score',
        type=float,
        default=50.0,
        help='Minimum development score (0-100)'
    )
    
    args = parser.parse_args()
    
    # Run pipeline
    pipeline = DevelopmentPipeline()
    
    try:
        stats = pipeline.run(
            search_query=args.query,
            location=args.location,
            use_scrapers=args.use_scrapers,
            max_pages=args.max_pages,
            enrich_data=not args.no_enrich,
            classify_data=not args.no_classify,
            min_dev_score=args.min_score
        )
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nPipeline interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\nPipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

            