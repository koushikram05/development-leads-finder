# app/core/data_merger.py

import pandas as pd
from typing import List

class DataMerger:
    """
    Merges multiple property data sources into a single DataFrame.
    """

    def merge(self, dataframes: List[pd.DataFrame]) -> pd.DataFrame:
        """
        Merge a list of pandas DataFrames.
        """
        if not dataframes:
            return pd.DataFrame()
        merged_df = pd.concat(dataframes, ignore_index=True)
        return merged_df


# Example usage
if __name__ == "__main__":
    df1 = pd.DataFrame({"id": [1, 2], "price": [500000, 600000]})
    df2 = pd.DataFrame({"id": [3], "price": [550000]})
    merger = DataMerger()
    merged = merger.merge([df1, df2])
    print(merged)
