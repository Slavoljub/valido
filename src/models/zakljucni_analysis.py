import pandas as pd
import openai
from typing import Dict
import os

# Postavljanje API ključa (možeš i iz okruženja ako ne želiš hardkod)
openai.api_key = "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"

def parse_zakljucni_list() -> Dict[str, float]:
    csv_path = "/media/malac/homeMX/malac/projekat/validoAI/data/mom21/rtg/zakljucni.csv"
    df = pd.read_csv(csv_path)

    # Grupisanje konta po poslovnim kategorijama
    konta_grupe = {
        "računi": [241, 244],
        "potraživanja": [204, 205],
        "zalihe": [100, 101, 150],
        "osnovna_sredstva": [23, 28],
        "obaveze": [435, 422, 470]
    }

    rezultati = {grupa: 0.0 for grupa in konta_grupe}

    for grupa, konta in konta_grupe.items():
        suma = df[df['konto'].isin(konta)]['neto_saldo'].sum()
        rezultati[grupa] = round(suma, 2)

    # ✅ Dodatno: likvidnost i status
    obrtna = rezultati["računi"] + rezultati["potraživanja"] + rezultati["zalihe"]
    obaveze = rezultati["obaveze"]
    likvidnost = round(obrtna / obaveze, 2) if obaveze else 0.0

    if likvidnost < 1.0:
        likvidnost_status = "Rizično"
        badge_klasa = "badge bg-danger"
    elif 1.0 <= likvidnost <= 1.5:
        likvidnost_status = "Upozorenje"
        badge_klasa = "badge bg-warning text-dark"
    else:
        likvidnost_status = "Stabilno"
        badge_klasa = "badge bg-success"

    # Dodajemo u rezultate
    rezultati["likvidnost"] = likvidnost
    rezultati["likvidnost_status"] = likvidnost_status
    rezultati["likvidnost_badge"] = badge_klasa

    return rezultati

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def generate_financial_commentary(data: Dict[str, float]) -> str:
    prompt = f"""
Na osnovu sledećih finansijskih podataka firme na kraju godine:

- Računi (gotovina): {data['računi']} RSD
- Potraživanja od kupaca: {data['potraživanja']} RSD
- Zalihe i avansi: {data['zalihe']} RSD
- Osnovna sredstva: {data['osnovna_sredstva']} RSD
- Obaveze (dobavljači, PDV, krediti): {data['obaveze']} RSD

Dodatni indikator:
- Koeficijent likvidnosti (obrtna sredstva / obaveze): {data['likvidnost']} → status: {data['likvidnost_status']}

Napiši jasan, stručan i direktan komentar o finansijskom zdravlju firme.
Komentar treba da bude u 3–5 rečenica, kao da ga knjigovođa piše vlasniku firme.

Uključi analizu:
- Da li firma može da pokrije obaveze
- Koliko su obrtna sredstva jaka
- Da li je stanje stabilno ili upozoravajuće
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-0125-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"[GPT GREŠKA] {e}")
        return "AI komentar nije dostupan u ovom trenutku."

