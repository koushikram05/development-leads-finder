# app/geo/zoning_loader.py

import geopandas as gpd

class ZoningLoader:
    """
    Loads and provides zoning information from shapefiles.
    """

    def __init__(self, shapefile_path: str):
        self.shapefile_path = shapefile_path
        self.zoning_gdf = None
        self._load_shapefile()

    def _load_shapefile(self):
        """
        Load zoning shapefile into a GeoDataFrame.
        """
        try:
            self.zoning_gdf = gpd.read_file(self.shapefile_path)
        except Exception as e:
            raise FileNotFoundError(f"Error loading shapefile: {self.shapefile_path}") from e

    def get_zone(self, latitude: float, longitude: float):
        """
        Returns zoning information for a given coordinate.
        """
        if self.zoning_gdf is None:
            raise ValueError("Zoning shapefile not loaded yet.")
        
        point_gdf = gpd.GeoDataFrame(
            geometry=gpd.points_from_xy([longitude], [latitude]),
            crs=self.zoning_gdf.crs
        )
        result = gpd.sjoin(point_gdf, self.zoning_gdf, how="left", predicate="intersects")
        return result
