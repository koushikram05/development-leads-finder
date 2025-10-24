# app/geo/lot_analysis.py

class LotAnalysis:
    """
    Performs basic lot analysis for properties.
    """
    def __init__(self, lot_size: float, zoning_type: str):
        self.lot_size = lot_size  # in square feet
        self.zoning_type = zoning_type

    def is_buildable(self) -> bool:
        """
        Determines if the lot is suitable for building based on zoning.
        """
        min_lot_sizes = {
            "residential": 5000,
            "commercial": 10000,
            "industrial": 20000
        }
        required_size = min_lot_sizes.get(self.zoning_type.lower(), 0)
        return self.lot_size >= required_size

    def lot_value_score(self) -> float:
        """
        Calculates a simple score based on lot size and zoning.
        """
        score = self.lot_size / 1000
        if self.zoning_type.lower() == "residential":
            score *= 1.2
        elif self.zoning_type.lower() == "commercial":
            score *= 1.5
        return score

# Example usage
if __name__ == "__main__":
    lot = LotAnalysis(6000, "residential")
    print("Buildable:", lot.is_buildable())
    print("Lot score:", lot.lot_value_score())
