import pandas as pd
import openai
import re
import matplotlib.pyplot as plt

#Pretvara srpske brojeve (u hiljadama) u čiste float RSD vrednosti
def parse_serbian_number(s):
    if s is None:
        return None
    s = str(s).strip().replace(" ", "").replace(".", "")
    if s.count(",") > 1:
        parts = s.rsplit(",", 1)
        s = parts[0].replace(",", "") + "." + parts[1]
    else:
        s = s.replace(",", ".")
    try:
        return float(s) * 1000
    except ValueError:
        return None

#Priprema bilans stanja: čisti podatke, konvertuje brojeve i klasifikuje stavke
def prepare_bilans_stanja_pregled(csv_path):
    df = pd.read_csv(csv_path)
    df['0'] = df['0'].ffill()
    df['1'] = df['1'].ffill()
    df.columns = ['Red', 'Pozicija', 'RSD', 'EUR', 'Učešće', 'Nepoznato1', 'Nepoznato2']

    ignore_keywords = ['BILANS', 'AKTIVA', 'PASIVA', 'OBRTNA', 'STALNA', 'IMOVINA', 'KAPITAL', 'UKUPNA', 'POZICIJA', 'VALIDO']
    df = df[~df['Pozicija'].str.upper().str.contains('|'.join(ignore_keywords), na=False)]

    df['RSD'] = df['RSD'].apply(parse_serbian_number)
    df['EUR'] = df['EUR'].apply(parse_serbian_number)
    df['Učešće'] = df['Učešće'].apply(parse_serbian_number)

    df = df[df['RSD'].notna()]
    df = df.reset_index(drop=True)

    def map_kategorija(pozicija):
        pozicija = str(pozicija).lower()
        if any(x in pozicija for x in ['nekretnine', 'postrojenja', 'oprema', 'nematerijalna', 'goodwill', 'dugoročna']):
            return 'Stalna imovina'
        if any(x in pozicija for x in ['zalihe', 'kratkoročna', 'gotovinska', 'gotovina', 'potraživanja', 'plasmani', 'pdv', 'unapred', 'ekvivalenti']):
            return 'Obrtna imovina'
        if any(x in pozicija for x in ['kapital', 'dobitak', 'gubitak', 'rezerv']):
            return 'Kapital'
        if any(x in pozicija for x in ['obaveze', 'kredit', 'dugoroč', 'kratkoroč', 'porez']):
            return 'Obaveze'
        return 'Ostalo'

    df['Kategorija'] = df['Pozicija'].apply(map_kategorija)
    df['Grupa'] = df['Pozicija'].str.extract(r'([A-ZČŠĐŽĆ].*)')

    return df[['Pozicija', 'RSD', 'EUR', 'Učešće', 'Kategorija', 'Grupa']]

# Prikazuje Pie chart (grafički prikaz bilansa po kategorijama)
def plot_pie_bilans(df):
    grouped = df.groupby("Kategorija")["RSD"].sum()
    labels = grouped.index
    values = grouped.values

    plt.figure(figsize=(7, 7))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90,
            colors=plt.cm.Set3.colors, wedgeprops={'edgecolor': 'white'})
    plt.title("Struktura bilansa po kategorijama", fontsize=14)
    plt.axis('equal')
    plt.tight_layout()
    plt.show()

# Analizira bilans stanja i vraća GPT komentar — stručan, čist i bez simbola
def gpt_komentar_bilansa(df, api_key):
    openai.api_key = api_key
    suma = df.groupby("Kategorija")["RSD"].sum().to_dict()

    stalna = suma.get("Stalna imovina", 0)
    obrtna = suma.get("Obrtna imovina", 0)
    kapital = suma.get("Kapital", 0)
    obaveze = suma.get("Obaveze", 0)
    ukupna_imovina = stalna + obrtna
    ukupna_izvori = kapital + obaveze

    tekst = f"""
Bilans stanja na dan 31.12.2024. prikazuje:

Stalna imovina: {int(stalna):,} RSD  
Obrtna imovina: {int(obrtna):,} RSD  
Ukupna imovina: {int(ukupna_imovina):,} RSD  
Kapital: {int(kapital):,} RSD  
Obaveze: {int(obaveze):,} RSD  
Ukupni izvori finansiranja: {int(ukupna_izvori):,} RSD
""".replace(",", ".")

    prompt = f"""
Korisnik želi stručan i razumljiv komentar bilansa stanja firme na dan 31.12.2024.

{tekst}

Objasni:
- Šta prikazuje aktiva
- Kakva je struktura stalne i obrtne imovine
- Šta prikazuje pasiva
- Da li postoji finansijska ravnoteža
- Da li se poštuje zlatno pravilo finansiranja
- Šta vlasnik može da zaključi

Piši jasno, bez liste, simbola i prekidanja. Samo povezan tekst kao da savetnik objašnjava.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4-0125-preview",
        messages=[
            {"role": "system", "content": "Ti si iskusan finansijski savetnik."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=700
    )

    #Čišćenje odgovora
    tekst = response["choices"][0]["message"]["content"]
    tekst = re.sub(r"\*\*|__|\*", "", tekst)
    tekst = re.sub(r"^\s*\d+\.\s*", "", tekst, flags=re.MULTILINE)
    tekst = re.sub(r"^#+\s*", "", tekst, flags=re.MULTILINE)
    if not tekst.strip().endswith("."):
        tekst = tekst.rsplit(".", 1)[0] + "."

    return tekst.strip()
