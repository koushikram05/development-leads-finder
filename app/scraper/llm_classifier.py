import os, openai
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def classify_listings(input_csv="data/enriched_listings.csv", output_csv="data/development_leads.csv"):
    df = pd.read_csv(input_csv)
    labels = []
    for _, row in df.iterrows():
        snippet = f"{row.get('address')} {row.get('lot_size')} {row.get('year_built')} {row.get('price')}"
        resp = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role":"user","content":f"Classify if this property is a development/teardown opportunity: {snippet}"}],
            temperature=0.0,
            max_tokens=200
        )
        text = resp.choices[0].message.content
        # crude JSON parse
        import json
        try: js = json.loads(text)
        except: js={"label":"unknown","confidence":0.0,"explanation":text}
        labels.append(js)
    df_labels = pd.DataFrame(labels)
    df_final = pd.concat([df, df_labels], axis=1)
    df_final.to_csv(output_csv, index=False)
    print(f"✅ LLM classified CSV saved to {output_csv}")
    return df_final
