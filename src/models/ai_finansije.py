import pandas as pd
import openai
import matplotlib.pyplot as plt
import re

# OpenAI API ključ (privremeno direktno, kasnije može preko env var)
openai.api_key = "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"

# Učitaj CSV fajl sa podacima o dobavljačima
CSV_PATH = "/media/malac/homeMX/malac/projekat/validoAI/data/mom21/specifikacija_dobavljaca/specifikacija_dobavljaca_ai.csv"
df_2024 = pd.read_csv(CSV_PATH)


# postojeće funkcije
def ucitaj_dobavljace_putanja(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["promet"] = df["duguje"] + df["potrazuje"]
    return df

def ucitaj_plate_putanja(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Bruto 2"] = df["Bruto 2"].astype(str) \
        .str.replace(",", "", regex=False) \
        .str.replace(".", "", regex=False) \
        .astype(float)
    df["Bruto 2"] = df["Bruto 2"] / 100  # decimalni iznos
    return df

# dopunjena funkcija
def generisi_ai_svesku_sa_trendom(
    df_dobavljaci: pd.DataFrame,
    df_plate: pd.DataFrame,
    godina: str = "2024"
) -> dict:
    try:
        # Zbirni iznosi
        ukupno_duguje = df_dobavljaci["duguje"].sum()
        ukupno_bruto2 = df_plate["Bruto 2"].sum()
        ukupno_trosak = ukupno_duguje + ukupno_bruto2

        # Procenti
        procenat_dobavljaci = round((ukupno_duguje / ukupno_trosak) * 100, 2)
        procenat_plate = round((ukupno_bruto2 / ukupno_trosak) * 100, 2)

        # GPT prompt
        prompt = f"""
Analiziraj finansijsku sliku firme za {godina}. godinu na osnovu sledećih podataka:

- Ukupno plaćeno dobavljačima: {ukupno_duguje:.2f} RSD
- Ukupno isplaćeno zaposlenima (bruto 2): {ukupno_bruto2:.2f} RSD
- Ukupni trošak: {ukupno_trosak:.2f} RSD
- Procenat na dobavljače: {procenat_dobavljaci:.2f}%
- Procenat na zaposlene: {procenat_plate:.2f}%

Uporedi strukturu troškova. Da li firma više troši na radnu snagu ili na partnere? Da li postoji disbalans? Piši jasno i bez tehničkog jezika.
"""

        odgovor = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )

        tekst = odgovor["choices"][0]["message"]["content"]

        tekst = re.sub(r"\*\*|__|\*", "", tekst)
        tekst = re.sub(r"^\s*\d+\.\s*", "", tekst, flags=re.MULTILINE)
        tekst = re.sub(r"^#+\s*", "", tekst, flags=re.MULTILINE)
        if not tekst.strip().endswith("."):
            tekst = tekst.rsplit(".", 1)[0] + "."

        # Grafik trenda bruto zarada po mesecima
        plt.figure(figsize=(10, 5))
        df_trend = df_plate.groupby('Mesec')['Bruto 2'].sum().reset_index()
        plt.plot(df_trend['Mesec'], df_trend['Bruto 2'], marker='o', linestyle='-', linewidth=2)
        plt.title(f'Trend bruto zarada za {godina}. godinu', fontsize=14)
        plt.xlabel('Mesec', fontsize=12)
        plt.ylabel('Ukupno Bruto 2 (RSD)', fontsize=12)
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('trend_bruto_zarade.png')  # čuvamo grafik kao sliku
        plt.close()

        # JSON niz za frontend (Mesec + Bruto 2)
        trend_bruto2 = df_trend.to_dict(orient="records")

        return {
            "gpt_tekst": tekst.strip(),
            "ukupno_duguje": round(ukupno_duguje, 2),
            "ukupno_bruto2": round(ukupno_bruto2, 2),
            "ukupno_trosak": round(ukupno_trosak, 2),
            "procenat_dobavljaci": procenat_dobavljaci,
            "procenat_plate": procenat_plate,
            "grafik_putanja": "trend_bruto_zarade.png",
            "trend_bruto2": trend_bruto2
        }

    except Exception as e:
        return {"error": f"Greška pri AI analizi sveske: {str(e)}"}







if __name__ == "__main__":
    print("--- GPT analiza dobavljača: Top 5 po prometu ---\n")
    df_top5 = generisi_top_5_tabelu(df_2024)
    print(df_top5.to_string(index=False))
