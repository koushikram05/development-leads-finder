"""
Map Generator for Development Opportunities
Creates interactive Folium maps with OpenStreetMap, heatmaps, and layer controls
"""

import folium
from folium.plugins import HeatMap, MarkerCluster
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class MapGenerator:
    """
    Generate interactive maps for development opportunities using Folium + OpenStreetMap
    
    Features:
    - Color-coded markers by development score
    - Heatmap showing opportunity density
    - Layer controls (toggle markers, heatmap)
    - Popups with property details
    - Multiple basemap options
    """
    
    # Color scheme by development score (hex colors for popups)
    COLOR_SCHEME = {
        'excellent': '#d62728',    # Red: 80-100
        'good': '#ff7f0e',         # Orange: 70-79
        'fair': '#ffdd00',         # Yellow: 60-69
        'low': '#2ca02c'           # Green: 0-59
    }
    
    # Icon colors for Folium (use only valid Folium colors)
    ICON_COLOR_MAP = {
        'excellent': 'red',
        'good': 'orange',
        'fair': 'yellow',
        'low': 'green'
    }
    
    def __init__(self, center_lat: float = 42.3314, center_lon: float = -71.2045, zoom_start: int = 12):
        """
        Initialize map generator
        
        Args:
            center_lat: Center latitude (default: Newton, MA)
            center_lon: Center longitude (default: Newton, MA)
            zoom_start: Initial zoom level (default: 12 - neighborhood view)
        """
        self.center_lat = center_lat
        self.center_lon = center_lon
        self.zoom_start = zoom_start
        
        # Initialize map with OpenStreetMap
        self.map = folium.Map(
            location=[self.center_lat, self.center_lon],
            zoom_start=self.zoom_start,
            tiles='OpenStreetMap'  # Use OpenStreetMap (free, open-source)
        )
        
        self.properties = []
        self.heatmap_data = []
        self.marker_groups = {
            'all': folium.FeatureGroup(name='All Markers (29 properties)', show=True),
            'high_value': folium.FeatureGroup(name='High-Value Only (≥70)', show=True),
            'excellent': folium.FeatureGroup(name='Excellent (≥80)', show=True)
        }
        
        logger.info(f"Map initialized at ({center_lat}, {center_lon}) with zoom {zoom_start}")
    
    def add_properties(self, listings: List[Dict[str, Any]], show_all: bool = True):
        """
        Add property markers to map
        
        Args:
            listings: List of property dictionaries with:
                - address: Property address
                - latitude: Lat coordinate
                - longitude: Lon coordinate
                - development_score: Score 0-100
                - price: Property price
                - lot_size: Lot size in sqft
                - year_built: Construction year
                - explanation: Why this score
            show_all: Whether to show all properties (default: True)
        """
        self.properties = listings
        
        logger.info(f"Adding {len(listings)} properties to map")
        
        # Count by category
        excellent = good = fair = low = 0
        
        for prop in listings:
            score = float(prop.get('development_score', 0))
            
            # Determine category
            if score >= 80:
                category = 'excellent'
                excellent += 1
            elif score >= 70:
                category = 'good'
                good += 1
            elif score >= 60:
                category = 'fair'
                fair += 1
            else:
                category = 'low'
                low += 1
            
            # Add marker to "all" group
            self._add_marker(prop, category, self.marker_groups['all'])
            
            # Add to filtered groups
            if score >= 70:
                self._add_marker(prop, category, self.marker_groups['high_value'])
            
            if score >= 80:
                self._add_marker(prop, category, self.marker_groups['excellent'])
            
            # Collect heatmap data
            if prop.get('latitude') and prop.get('longitude'):
                self.heatmap_data.append([
                    float(prop['latitude']),
                    float(prop['longitude']),
                    float(score) / 100  # Normalize to 0-1
                ])
        
        # Add marker groups to map
        for group in self.marker_groups.values():
            group.add_to(self.map)
        
        logger.info(f"Properties added: {excellent} excellent, {good} good, {fair} fair, {low} low")
        return {
            'excellent': excellent,
            'good': good,
            'fair': fair,
            'low': low,
            'total': len(listings)
        }
    
    def _add_marker(self, prop: Dict[str, Any], category: str, feature_group: folium.FeatureGroup):
        """
        Add single property marker to feature group
        
        Args:
            prop: Property dictionary
            category: 'excellent', 'good', 'fair', or 'low'
            feature_group: FeatureGroup to add marker to
        """
        try:
            lat = float(prop.get('latitude'))
            lon = float(prop.get('longitude'))
            
            # Get icon color
            icon_color = self.ICON_COLOR_MAP.get(category, 'gray')
            
            # Create popup HTML
            popup_html = self._create_popup_html(prop)
            
            # Create popup
            popup = folium.Popup(popup_html, max_width=300)
            
            # Add marker with category-based color
            folium.Marker(
                location=[lat, lon],
                popup=popup,
                icon=folium.Icon(color=icon_color, icon='info-sign'),
                tooltip=f"{prop.get('address', 'Unknown')} - Score: {prop.get('development_score', 'N/A')}"
            ).add_to(feature_group)
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Could not add marker for {prop.get('address', 'Unknown')}: {e}")
    
    def _create_popup_html(self, prop: Dict[str, Any]) -> str:
        """
        Create HTML content for popup
        
        Args:
            prop: Property dictionary
            
        Returns:
            HTML string for popup
        """
        score = float(prop.get('development_score', 0))
        
        # Determine score category
        if score >= 80:
            score_label = "🔴 EXCELLENT"
            score_class = "excellent"
        elif score >= 70:
            score_label = "🟠 GOOD"
            score_class = "good"
        elif score >= 60:
            score_label = "🟡 FAIR"
            score_class = "fair"
        else:
            score_label = "🟢 LOW"
            score_class = "low"
        
        # Format price
        price = prop.get('price', 0)
        try:
            price_str = f"${int(float(price)):,}"
        except (ValueError, TypeError):
            price_str = "N/A"
        
        # Format lot size
        lot_size = prop.get('lot_size', 0)
        try:
            lot_str = f"{int(float(lot_size)):,} sqft"
        except (ValueError, TypeError):
            lot_str = "N/A"
        
        # Format year built
        year = prop.get('year_built', 'N/A')
        
        # Get explanation
        explanation = prop.get('explanation', 'No explanation provided')
        
        # Create HTML
        html = f"""
        <div style="font-family: Arial, sans-serif; width: 280px; font-size: 13px;">
            <h4 style="margin: 0 0 10px 0; color: #333; border-bottom: 2px solid #ddd; padding-bottom: 8px;">
                {prop.get('address', 'Unknown Address')}
            </h4>
            
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 10px;">
                <tr style="background: #f9f9f9;">
                    <td style="padding: 6px; border-bottom: 1px solid #eee;"><strong>Score:</strong></td>
                    <td style="padding: 6px; border-bottom: 1px solid #eee; text-align: right;">
                        <strong>{score:.1f}/100</strong> {score_label}
                    </td>
                </tr>
                <tr>
                    <td style="padding: 6px; border-bottom: 1px solid #eee;"><strong>Price:</strong></td>
                    <td style="padding: 6px; border-bottom: 1px solid #eee; text-align: right;">{price_str}</td>
                </tr>
                <tr style="background: #f9f9f9;">
                    <td style="padding: 6px; border-bottom: 1px solid #eee;"><strong>Lot Size:</strong></td>
                    <td style="padding: 6px; border-bottom: 1px solid #eee; text-align: right;">{lot_str}</td>
                </tr>
                <tr>
                    <td style="padding: 6px; border-bottom: 1px solid #eee;"><strong>Year Built:</strong></td>
                    <td style="padding: 6px; border-bottom: 1px solid #eee; text-align: right;">{year}</td>
                </tr>
            </table>
            
            <div style="background: #f0f0f0; padding: 8px; border-radius: 4px; margin-bottom: 10px;">
                <strong style="color: #333;">Why This Score?</strong>
                <p style="margin: 5px 0 0 0; font-size: 12px; color: #555; line-height: 1.4;">
                    {explanation}
                </p>
            </div>
            
            <div style="text-align: center; padding-top: 8px; border-top: 1px solid #eee;">
                <small style="color: #666;">Click address for more details</small>
            </div>
        </div>
        """
        
        return html
    
    def add_heatmap(self, intensity_field: str = 'development_score'):
        """
        Add heatmap layer showing opportunity density
        
        Args:
            intensity_field: Field to use for heat intensity (default: development_score)
        """
        if not self.heatmap_data:
            logger.warning("No heatmap data available. Add properties first.")
            return
        
        logger.info(f"Adding heatmap layer with {len(self.heatmap_data)} points")
        
        # Create heatmap layer
        heatmap_layer = folium.FeatureGroup(name='Development Score Heatmap', show=True)
        
        HeatMap(
            self.heatmap_data,
            name='Heatmap',
            min_opacity=0.2,
            radius=25,
            blur=15,
            max_zoom=1
        ).add_to(heatmap_layer)
        
        heatmap_layer.add_to(self.map)
    
    def add_layer_control(self):
        """Add layer control panel for toggling layers"""
        logger.info("Adding layer controls")
        
        # Add layer control
        folium.LayerControl(
            position='topleft',
            collapsed=False
        ).add_to(self.map)
    
    def save_map(self, filepath: str) -> str:
        """
        Save map to HTML file
        
        Args:
            filepath: Path to save HTML file
            
        Returns:
            Path to saved file
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Add title to map
        title_html = '''
        <div style="position: fixed; 
                    top: 10px; left: 50px; width: 300px; height: auto;
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:16px; font-weight: bold; padding: 10px;
                    border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.2);">
            📍 Development Opportunities - Newton, MA
            <br><small style="font-weight: normal; font-size: 12px; color: #666;">
                {count} properties | Updated: {timestamp}
            </small>
        </div>
        '''.format(
            count=len(self.properties),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M")
        )
        
        self.map.get_root().html.add_child(folium.Element(title_html))
        
        # Save map
        self.map.save(str(filepath))
        logger.info(f"✓ Map saved to {filepath}")
        
        return str(filepath)
    
    def generate_stats(self) -> Dict[str, Any]:
        """
        Generate statistics about the map
        
        Returns:
            Dictionary with statistics
        """
        if not self.properties:
            return {
                'total_properties': 0,
                'average_score': 0,
                'by_category': {}
            }
        
        scores = [float(p.get('development_score', 0)) for p in self.properties if p.get('development_score') is not None]
        
        excellent = sum(1 for p in self.properties if float(p.get('development_score', 0)) >= 80)
        good = sum(1 for p in self.properties if 70 <= float(p.get('development_score', 0)) < 80)
        fair = sum(1 for p in self.properties if 60 <= float(p.get('development_score', 0)) < 70)
        low = sum(1 for p in self.properties if float(p.get('development_score', 0)) < 60)
        
        # Calculate geographic coverage (only for properties with valid coordinates)
        valid_properties = [p for p in self.properties if p.get('latitude') and p.get('longitude')]
        
        north_count = sum(1 for p in valid_properties if float(p.get('latitude', 0)) > self.center_lat)
        south_count = sum(1 for p in valid_properties if float(p.get('latitude', 0)) < self.center_lat)
        east_count = sum(1 for p in valid_properties if float(p.get('longitude', 0)) > self.center_lon)
        west_count = sum(1 for p in valid_properties if float(p.get('longitude', 0)) < self.center_lon)
        
        stats = {
            'total_properties': len(self.properties),
            'properties_with_coordinates': len(valid_properties),
            'average_score': sum(scores) / len(scores) if scores else 0,
            'max_score': max(scores) if scores else 0,
            'min_score': min(scores) if scores else 0,
            'by_category': {
                'excellent': excellent,
                'good': good,
                'fair': fair,
                'low': low
            },
            'coverage': {
                'north': north_count,
                'south': south_count,
                'east': east_count,
                'west': west_count
            }
        }
        
        return stats
    
    def generate_and_save(self, output_dir: str = 'data/maps') -> str:
        """
        Complete workflow: generate map with all features and save
        
        Args:
            output_dir: Directory to save maps
            
        Returns:
            Path to main map file
        """
        from app.integrations.database_manager import HistoricalDatabaseManager
        
        logger.info("=" * 60)
        logger.info("MAP GENERATION STARTED")
        logger.info("=" * 60)
        
        try:
            # Get data from database
            db = HistoricalDatabaseManager()
            properties = db.get_recent_opportunities(days=30, min_score=0)
            
            logger.info(f"Retrieved {len(properties)} properties from database")
            
            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize map generator
            map_gen = MapGenerator()
            
            # Add properties with color coding
            logger.info("Adding properties with color-coding...")
            stats = map_gen.add_properties(properties)
            logger.info(f"  ✓ {stats['excellent']} excellent (🔴)")
            logger.info(f"  ✓ {stats['good']} good (🟠)")
            logger.info(f"  ✓ {stats['fair']} fair (🟡)")
            logger.info(f"  ✓ {stats['low']} low (🟢)")
            
            # Add heatmap
            logger.info("Adding development opportunity heatmap...")
            map_gen.add_heatmap()
            logger.info("  ✓ Heatmap added")
            
            # Add layer controls
            logger.info("Adding layer controls...")
            map_gen.add_layer_control()
            logger.info("  ✓ Layer controls added")
            
            # Save main map
            main_map = output_path / "latest_map.html"
            map_gen.save_map(str(main_map))
            
            # Generate stats
            map_stats = map_gen.generate_stats()
            logger.info("\nMap Statistics:")
            logger.info(f"  Total properties: {map_stats['total_properties']}")
            logger.info(f"  Average score: {map_stats['average_score']:.1f}/100")
            logger.info(f"  Score range: {map_stats['min_score']:.1f} - {map_stats['max_score']:.1f}")
            
            logger.info("\n" + "=" * 60)
            logger.info("✓ MAP GENERATION COMPLETE")
            logger.info("=" * 60)
            logger.info(f"Map saved to: {main_map}")
            logger.info(f"Open in browser: file://{main_map.absolute()}")
            
            return str(main_map)
            
        except Exception as e:
            logger.error(f"Map generation failed: {e}", exc_info=True)
            raise


# Convenience functions

def create_opportunity_map(listings: List[Dict[str, Any]], output_file: str = 'data/maps/latest_map.html') -> str:
    """
    Quick function to create and save a map
    
    Args:
        listings: List of property dictionaries
        output_file: Where to save the map
        
    Returns:
        Path to saved map file
    """
    map_gen = MapGenerator()
    map_gen.add_properties(listings)
    map_gen.add_heatmap()
    map_gen.add_layer_control()
    return map_gen.save_map(output_file)


def create_high_value_map(listings: List[Dict[str, Any]], min_score: int = 70, output_file: str = 'data/maps/high_value_map.html') -> str:
    """
    Create map with only high-value properties
    
    Args:
        listings: List of property dictionaries
        min_score: Minimum score to include
        output_file: Where to save the map
        
    Returns:
        Path to saved map file
    """
    filtered = [p for p in listings if float(p.get('development_score', 0)) >= min_score]
    map_gen = MapGenerator()
    map_gen.add_properties(filtered)
    map_gen.add_heatmap()
    map_gen.add_layer_control()
    return map_gen.save_map(output_file)
