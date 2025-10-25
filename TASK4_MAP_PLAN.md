# Task 4: Map Visualization - Complete Implementation Plan

## Overview

Create interactive maps showing development opportunities with heatmaps, filters, and detailed property information.

---

## Technology Stack Decision

### Option A: Folium (Python-based) ✅ **RECOMMENDED**
- **Pros:**
  - Pure Python (no JavaScript needed)
  - Integrates directly with our pipeline
  - Easy to export as HTML files
  - Great for static/exploratory maps
  - Works with Leaflet.js under the hood
  - Heatmap layers supported
  
- **Cons:**
  - Limited interactivity compared to pure web maps
  - Generates HTML files (not real-time)

### Option B: Google Maps API
- **Pros:**
  - Real-time updates
  - Excellent UI
  
- **Cons:**
  - Requires API key + billing
  - JavaScript heavy
  - Different from Python pipeline

### Option C: Leaflet.js (JavaScript)
- **Pros:**
  - Highly interactive
  - Open-source
  
- **Cons:**
  - Requires JavaScript knowledge
  - Separate from Python pipeline

**→ We'll use FOLIUM** (Easiest integration with our Python pipeline)

---

## Implementation Plan

### Phase 1: Basic Map (Hour 1)

**File:** `app/integrations/map_generator.py`

```python
class MapGenerator:
    def __init__(self, center_lat, center_lon, zoom=12):
        """Initialize map at Newton, MA center"""
        
    def add_properties(self, listings):
        """Add property markers to map"""
        
    def add_heatmap(self, listings):
        """Add development score heatmap layer"""
        
    def save_map(self, filename):
        """Export to HTML file"""
```

**Features:**
- Center map on Newton, MA (42.3314, -71.2045)
- Add property markers with color coding:
  - 🔴 **Red (Excellent):** Score 80-100
  - 🟠 **Orange (Good):** Score 70-79
  - 🟡 **Yellow (Fair):** Score 60-69
  - 🟢 **Green (Low):** Score 0-59
- Heatmap showing development opportunity density
- Zoom level 12 (neighborhood view)

### Phase 2: Interactivity (Hour 2)

**Features:**
- **Popup on Click:** Show property details
  - Address
  - Score: XX/100
  - Price: $XXX,XXX
  - Lot Size: X,XXX sqft
  - Year Built
  - Reasoning
  
- **Layer Control:**
  - Toggle "Markers" on/off
  - Toggle "Heatmap" on/off
  - Toggle "Development Opportunities" (score >= 70)
  
- **Search/Filter:**
  - Filter by score threshold (slider)
  - Filter by price range
  - Show only high-value properties

### Phase 3: Integration (Hour 3)

**Integration Points:**

1. **Pipeline Integration (Stage 7 - Optional)**
```
Stage 6: Database
    ↓
Stage 7: Generate Map (New) ← Optional
    - Generate HTML map file
    - Save to data/maps/
    - Link in summary email
```

2. **API Endpoint (Optional, for web dashboard)**
```python
@app.get("/map")
def get_map():
    """Return interactive map as HTML"""
    return FileResponse("data/maps/latest_map.html")
```

3. **Standalone Script**
```bash
python -c "from app.integrations.map_generator import MapGenerator; \
           db.get_recent_opportunities(); \
           map_gen.generate_and_save()"
```

---

## Detailed Implementation

### File Structure

```
app/
├── integrations/
│   ├── map_generator.py (NEW - 300 lines)
│   └── ...
└── ...

data/
├── maps/ (NEW directory)
│   ├── latest_map.html
│   ├── opportunities_map.html
│   └── archive/
└── ...

docs/
├── TASK4_MAP_SETUP.md (NEW - 200 lines)
└── ...
```

### Code Architecture

#### 1. MapGenerator Class

```python
class MapGenerator:
    """Generate interactive maps from property data"""
    
    def __init__(self, center_lat=42.3314, center_lon=-71.2045, zoom=12):
        """Initialize folium map"""
        self.map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom,
            tiles='OpenStreetMap'
        )
        self.properties = []
        self.heatmap_data = []
    
    def add_properties(self, listings, show_all=True, min_score=0):
        """Add markers for each property
        
        Args:
            listings: List of property dicts with lat/lon/score
            show_all: Include all properties or only high-value
            min_score: Minimum score to display (default 0)
        """
        for prop in listings:
            if float(prop.get('development_score', 0)) >= min_score:
                self._add_marker(prop)
    
    def add_heatmap(self, listings, intensity_field='development_score'):
        """Add heatmap layer showing opportunity density"""
        
    def add_layer_control(self):
        """Add toggle controls for different layers"""
        
    def save_map(self, filepath):
        """Export map to HTML file"""
    
    def _add_marker(self, property_dict):
        """Add single property marker with color based on score"""
        
    def _get_color(self, score):
        """Get color based on development score
        - Red: 80-100
        - Orange: 70-79
        - Yellow: 60-69
        - Green: 0-59
        """
```

#### 2. Color Coding System

```python
def get_color(score):
    """Color by development score"""
    if score >= 80:
        return '#d62728'      # Red - Excellent
    elif score >= 70:
        return '#ff7f0e'      # Orange - Good
    elif score >= 60:
        return '#ffdd00'      # Yellow - Fair
    else:
        return '#2ca02c'      # Green - Low
```

#### 3. Map Popup Template

```html
<div style="font-family: Arial; width: 200px;">
    <h4 style="margin: 0 0 10px 0;">ADDRESS</h4>
    
    <table style="width: 100%; font-size: 12px;">
        <tr>
            <td><strong>Score:</strong></td>
            <td>XX/100</td>
        </tr>
        <tr style="background: #f0f0f0;">
            <td><strong>Price:</strong></td>
            <td>$XXX,XXX</td>
        </tr>
        <tr>
            <td><strong>Lot Size:</strong></td>
            <td>X,XXX sqft</td>
        </tr>
        <tr style="background: #f0f0f0;">
            <td><strong>Year Built:</strong></td>
            <td>XXXX</td>
        </tr>
        <tr>
            <td colspan="2"><strong>Reason:</strong></td>
        </tr>
        <tr>
            <td colspan="2"><small>REASONING TEXT</small></td>
        </tr>
    </table>
    
    <div style="margin-top: 10px;">
        <a href="SHEET_URL" target="_blank" style="color: #0066cc;">
            View in Google Sheets
        </a>
    </div>
</div>
```

#### 4. Heatmap Layer

```python
def add_heatmap(self, listings):
    """Add density heatmap
    
    Creates heatmap showing concentration of opportunities
    Using development_score as intensity
    """
    heatmap_data = []
    for prop in listings:
        if prop.get('latitude') and prop.get('longitude'):
            heatmap_data.append([
                prop['latitude'],
                prop['longitude'],
                float(prop.get('development_score', 0)) / 100  # Normalize 0-1
            ])
    
    HeatMap(heatmap_data, 
            name='Development Score Heatmap',
            min_opacity=0.2,
            radius=25,
            blur=15).add_to(self.map)
    
    folium.LayerControl().add_to(self.map)
```

---

## Usage Examples

### Example 1: Basic Map Generation

```python
from app.integrations.map_generator import MapGenerator
from app.integrations.database_manager import HistoricalDatabaseManager

# Get recent properties
db = HistoricalDatabaseManager()
properties = db.get_recent_opportunities(days=30, min_score=0)

# Create map
map_gen = MapGenerator(center_lat=42.3314, center_lon=-71.2045)
map_gen.add_properties(properties)
map_gen.add_heatmap(properties)
map_gen.add_layer_control()

# Save
map_gen.save_map('data/maps/latest_map.html')
print("✓ Map saved to data/maps/latest_map.html")
```

### Example 2: Filter by Score

```python
# Only show high-value properties
map_gen = MapGenerator()
high_value = db.get_recent_opportunities(days=30, min_score=70)
map_gen.add_properties(high_value)
map_gen.save_map('data/maps/high_value_map.html')
```

### Example 3: Custom Basemap

```python
# Different map style
map_gen = MapGenerator()
map_gen.map = folium.Map(
    location=[42.3314, -71.2045],
    zoom_start=12,
    tiles='CartoDB positron'  # Light theme
)
map_gen.add_properties(properties)
map_gen.save_map('data/maps/light_map.html')
```

---

## Pipeline Integration (Stage 7)

### Option A: As Optional Stage in Pipeline

Modify `app/dev_pipeline.py`:

```python
# Stage 7: Generate Maps (Optional)
if generate_maps:
    self.logger.info("\n" + "=" * 60)
    self.logger.info("STAGE 7: GENERATING MAPS")
    self.logger.info("=" * 60)
    
    try:
        from app.integrations.map_generator import MapGenerator
        
        # Create directory
        Path("data/maps").mkdir(exist_ok=True)
        
        # Get all properties from database
        db = HistoricalDatabaseManager()
        properties = db.get_recent_opportunities(days=30, min_score=0)
        
        # Generate maps
        map_gen = MapGenerator()
        map_gen.add_properties(properties)
        map_gen.add_heatmap(properties)
        map_gen.add_layer_control()
        map_gen.save_map('data/maps/latest_map.html')
        
        self.logger.info(f"✓ Map generated: data/maps/latest_map.html")
        
    except Exception as e:
        self.logger.warning(f"Map generation failed (non-critical): {e}")
```

### Option B: Standalone Script

```bash
# Generate map independently
python -m app.scripts.generate_maps

# Generate map for specific date range
python -m app.scripts.generate_maps --days 7 --min-score 70
```

---

## Output

### Map Features

1. **Markers**
   - Color-coded by development score
   - Clustered when zoomed out
   - Popup with property details on click

2. **Heatmap Layer**
   - Shows opportunity density
   - Toggleable with layer control
   - Intensity based on score

3. **Layers**
   - Markers layer (toggle on/off)
   - Heatmap layer (toggle on/off)
   - Basemap options

4. **Export**
   - Saved as `data/maps/latest_map.html`
   - ~500 KB file size (for 29 properties)
   - Can be opened in any browser
   - Can be embedded in email or dashboard

### Example Output Files

```
data/maps/
├── latest_map.html          (Current scan results)
├── high_value_map.html      (Score >= 70 only)
├── opportunities_map.html   (Development opportunities)
├── heatmap_only.html        (Heatmap layer only)
└── archive/
    ├── map_2025_10_24.html
    └── map_2025_10_23.html
```

---

## Dependencies

Add to `requirements.txt`:

```
folium==0.14.0          # Map generation
geopy==2.4.1           # Geocoding (if needed)
```

Install:

```bash
pip install folium geopy
```

---

## File Size Estimates

- **Single map (29 properties):** ~500 KB HTML
- **With heatmap + all layers:** ~600 KB
- **High-value only (0 properties):** ~300 KB

**Performance:** Maps open in browser instantly (<1 second)

---

## Testing Plan

### Test 1: Basic Map Generation

```python
def test_basic_map():
    """Test map creation with sample data"""
    sample_data = [
        {
            'address': '123 Main St',
            'latitude': 42.3314,
            'longitude': -71.2045,
            'development_score': 85,
            'price': 750000,
            'lot_size': 10000
        },
        # ... more properties
    ]
    
    map_gen = MapGenerator()
    map_gen.add_properties(sample_data)
    map_gen.save_map('test_map.html')
    
    assert Path('test_map.html').exists()
    print("✓ Basic map test passed")
```

### Test 2: Heatmap Layer

```python
def test_heatmap():
    """Test heatmap generation"""
    map_gen = MapGenerator()
    map_gen.add_properties(properties)
    map_gen.add_heatmap(properties)
    map_gen.save_map('test_heatmap.html')
    
    assert 'HeatMap' in Path('test_heatmap.html').read_text()
    print("✓ Heatmap test passed")
```

### Test 3: Color Coding

```python
def test_color_coding():
    """Test score-based color assignment"""
    test_cases = [
        (95, '#d62728'),  # Red
        (75, '#ff7f0e'),  # Orange
        (65, '#ffdd00'),  # Yellow
        (25, '#2ca02c'),  # Green
    ]
    
    for score, expected_color in test_cases:
        assert get_color(score) == expected_color
    
    print("✓ Color coding test passed")
```

---

## Documentation

### File: `TASK4_MAP_SETUP.md`

```markdown
# Task 4: Map Visualization Setup Guide

## Quick Start
python -c "from app.integrations.map_generator import MapGenerator; ..."

## Features
- Color-coded markers by development score
- Heatmap showing opportunity density
- Layer control (toggle markers/heatmap)
- Property details popups
- Multiple basemaps

## Output
- HTML file saved to `data/maps/latest_map.html`
- Open in any web browser
- Fully interactive

## API Reference
...
```

---

## Advantages of This Approach

✅ **Pure Python** - No JavaScript needed
✅ **Integrates with existing pipeline** - Works with database
✅ **Easy to use** - One line: `map_gen.save_map(filename)`
✅ **Portable** - HTML files can be shared/embedded
✅ **Real data** - Uses actual property coordinates from database
✅ **Professional** - Beautiful, polished maps
✅ **Extensible** - Easy to add features later
✅ **No external services** - Works offline (except basemap tiles)

---

## Timeline

| Phase | Time | Deliverables |
|-------|------|--------------|
| 1: Basic Map | 30 min | Color-coded markers, heatmap |
| 2: Interactivity | 30 min | Popups, layer control, filters |
| 3: Integration | 30 min | Pipeline integration + testing |
| **Total** | **~1.5 hours** | Production-ready map system |

---

## Next Steps After Task 4

1. ✅ Task 4 Complete: Maps with visualization
2. ⏭️ Task 5: ROI Scoring (30-40 min)
3. ⏭️ Fine-tune ML Model (1-2 hours)

**All Tasks Completion:** ~3-4 hours remaining

---

## Example Map Usage in Email

Could embed map link in email alerts:

```html
<div style="margin-top: 20px;">
    <h3>📍 View on Interactive Map</h3>
    <p>
        <a href="https://yourserver.com/maps/latest_map.html" 
           style="background: #667eea; color: white; padding: 10px 20px; 
                  border-radius: 5px; text-decoration: none;">
            Open Interactive Map
        </a>
    </p>
</div>
```

---

## Questions Answered

**Q: Can I update the map in real-time?**
A: Yes - regenerate the HTML after each pipeline run (Stage 7)

**Q: Can I embed the map on a website?**
A: Yes - iFrame the HTML file: `<iframe src="maps/latest_map.html"></iframe>`

**Q: How many properties can the map handle?**
A: 1000+ properties work fine (tested with Folium)

**Q: Can users interact with the map?**
A: Yes - zoom, pan, click for details, toggle layers

**Q: Does it work offline?**
A: Mostly yes (except basemap tiles require internet)

---

## Summary

**Task 4 will deliver:**
- ✅ Interactive map with property markers
- ✅ Heatmap showing development opportunity density
- ✅ Color-coding by score (Red/Orange/Yellow/Green)
- ✅ Popups with property details
- ✅ Layer controls (toggle markers/heatmap)
- ✅ Integration with database
- ✅ HTML export for sharing/embedding
- ✅ Production-ready code

**Ready to implement?** Say "Go" and we'll start! 🚀
