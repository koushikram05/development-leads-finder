import pandas as pd

def enrich_with_gis(listings_csv="data/raw_listings.csv", gis_csv="data/gis_data.csv", output_csv="data/enriched_listings.csv"):
    try:
        df_listings = pd.read_csv(listings_csv)
        df_gis = pd.read_csv(gis_csv)  # Newton parcel data
        df = pd.merge(df_listings, df_gis, how="left", left_on="address", right_on="Address")
        df.to_csv(output_csv, index=False)
        print(f"✅ GIS enriched CSV saved to {output_csv}")
        return df
    except Exception as e:
        print("⚠️ GIS enrichment failed:", e)
        return pd.DataFrame()
