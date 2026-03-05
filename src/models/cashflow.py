import pandas as pd
import openai
import re

# 🔐 OpenAI API ključ
openai.api_key = "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"

# ✅ Nova, robusna funkcija za konverziju srpskih brojeva
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
        return float(s)
    except ValueError:
        return None

def obradi_fakture_2024() -> dict:
    csv_path = "/media/malac/homeMX/malac/projekat/validoAI/data/mom21/specifikacija_dobavljaca/mom_ulazne_2024_dublja_analiza_sredjene_kolone.csv"
    df = pd.read_csv(csv_path)

    # 🧼 Konverzija svih numeričkih kolona
    for col in ["iznos_sa_pdv", "iznos_bez_pdv", "pdv_iznos"]:
        df[col] = df[col].apply(parse_serbian_number)

    df["datum_prometa"] = pd.to_datetime(df["datum_prometa"], errors="coerce", infer_datetime_format=True)
    df["dobavljac"] = df["dobavljac"].astype(str).str.strip()
    df = df.dropna(subset=["datum_prometa", "iznos_sa_pdv", "dobavljac"])

    # 🎯 Top 10 najvećih faktura
    df = df.sort_values(by="iznos_sa_pdv", ascending=False).head(10)

    fakture_json = df[["datum_prometa", "dobavljac", "iznos_bez_pdv", "iznos_sa_pdv"]] \
        .rename(columns={"datum_prometa": "datum"}) \
        .to_dict(orient="records")

    # 🧠 Priprema za GPT
    tekst_za_gpt = "\n".join([
        f"{f['datum'].date()} - {f['dobavljac']} - {f['iznos_sa_pdv']:.2f} RSD"
        for f in fakture_json
    ])

    prompt = (
        "Na osnovu sledećih 10 najvećih faktura u godini, analiziraj:\n"
        "- Ko su ključni dobavljači\n"
        "- Kada su bile najveće transakcije\n"
        "- Postoje li obrasci u vremenu ili partnerima\n\n"
        f"{tekst_za_gpt}"
    )

    try:
        odgovor = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Ti si AI finansijski analitičar."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )

        tekst = odgovor["choices"][0]["message"]["content"]
        tekst = re.sub(r"\*\*|__|\*", "", tekst)
        tekst = re.sub(r"^\s*\d+\.\s*", "", tekst, flags=re.MULTILINE)
        tekst = re.sub(r"^#+\s*", "", tekst, flags=re.MULTILINE)
        if not tekst.strip().endswith("."):
            tekst = tekst.rsplit(".", 1)[0] + "."

        komentar = tekst

    except Exception as e:
        komentar = f"GPT analiza nije uspela: {str(e)}"

    return {
        "fakture": fakture_json,
        "komentar": komentar
    }
