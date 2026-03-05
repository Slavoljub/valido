"""
KPR ETL Parser
--------------

Ova skripta pretvara KPR (Knjiga primljenih računa) Excel dokument
u čist dataframe finansijskih transakcija.

Pipeline:
Excel → Pandas → Čišćenje → Transformacija → Transakcioni model

Autor: ValidoAI ETL
"""

import re
import pandas as pd


# ------------------------------------------------------------
# CLEAN TEXT
# ------------------------------------------------------------
# Čisti tekstualna polja iz Excel/PDF konverzije
# uklanja newline, tabove i višestruke razmake
# takođe uklanja "//" koji se u KPR koristi kao separator
# ------------------------------------------------------------
def _clean_text(x):

    if pd.isna(x):
        return None

    s = str(x)

    # uklanjanje newline karaktera
    s = s.replace("\n", " ").replace("\t", " ")

    # uklanjanje duplih razmaka
    s = re.sub(r"\s+", " ", s).strip()

    # separator u knjizi
    if s in {"//", "/ /", "/"}:
        return None

    return s


# ------------------------------------------------------------
# SPLIT REDNI BROJ + DATUM KNJIŽENJA
# ------------------------------------------------------------
# Excel često ima spojeno polje:
# "00001 10/01/2025"
# Razdvajamo na:
# redni_broj
# datum_knjizenja
# ------------------------------------------------------------
def _split_redni_datum(s):

    if not s:
        return None, None

    m = re.match(r"^\s*(\d+)\s+(\d{2}/\d{2}/\d{4})\s*$", s)

    if m:
        return m.group(1), m.group(2)

    # fallback
    m2 = re.match(r"^\s*(\d+)\s*$", s)

    if m2:
        return m2.group(1), None

    return None, None


# ------------------------------------------------------------
# SPLIT BROJ RAČUNA + DATUM IZDAVANJA
# ------------------------------------------------------------
# polje može izgledati ovako:
# "DP5513878/25 10/01/2025"
# ili
# "F-6-2025 14/01/2025"
# ------------------------------------------------------------
def _split_racun_datum(s):

    if not s:
        return None, None

    m = re.match(r"^\s*(.+?)\s+(\d{2}/\d{2}/\d{4})\s*$", s)

    if m:
        return m.group(1).strip(), m.group(2)

    return s, None


# ------------------------------------------------------------
# PRETVARANJE BROJEVA
# ------------------------------------------------------------
# Excel može imati:
# 1234
# 1.234,56
# 1234.56
# Funkcija sve pretvara u float
# ------------------------------------------------------------
def _to_number(x):

    if x is None or (isinstance(x, float) and pd.isna(x)):
        return 0.0

    s = str(x).strip()

    if s == "" or s.lower() == "nan":
        return 0.0

    s = s.replace(" ", "")

    # evropski format
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(",", ".")

    try:
        return float(s)
    except ValueError:
        return 0.0


# ------------------------------------------------------------
# GLAVNA FUNKCIJA ETL-a
# ------------------------------------------------------------
def load_kpr(file_path: str) -> pd.DataFrame:

    # --------------------------------------------------------
    # 1. UČITAVANJE EXCEL-a
    # --------------------------------------------------------
    raw = pd.read_excel(file_path, header=None)

    # --------------------------------------------------------
    # 2. PRONALAŽENJE PRVOG REDA TRANSAKCIJE
    # --------------------------------------------------------
    start_row = raw[raw[0].astype(str).str.startswith("000", na=False)].index[0]

    raw = raw.iloc[start_row:].reset_index(drop=True)

    # --------------------------------------------------------
    # 3. UKLANJANJE PRAZNIH KOLONA
    # --------------------------------------------------------
    raw = raw.dropna(axis=1, how="all")

    # --------------------------------------------------------
    # 4. MAPIRANJE KPR STRUKTURE
    # --------------------------------------------------------
    raw.columns = [
        "redni_datum",
        "dokument",
        "racun_datum",
        "dobavljac",
        "pib",
        "ukupan_iznos",
        "osnovica",
        "oslobodjeno_pdv",
        "naknada_bez_pdv",
        "pdv",
        "pretporez_odbitni",
        "pretporez_neodbitni",
        "uvoz",
        "vrednost_bez_pdv",
        "iznos_pdv",
        "naknada_poljoprivreda",
    ]

    # --------------------------------------------------------
    # 5. ČIŠĆENJE TEKSTA
    # --------------------------------------------------------
    for c in ["redni_datum", "dokument", "racun_datum", "dobavljac", "pib"]:
        raw[c] = raw[c].map(_clean_text)

    # --------------------------------------------------------
    # 6. UKLANJANJE MEĐUZBIRA
    # --------------------------------------------------------
    raw = raw[
        ~raw["dobavljac"]
        .fillna("")
        .str.contains("MEĐUZBIR|MEDJUZBIR|UKUPNO", case=False, regex=True)
    ]

    # --------------------------------------------------------
    # 7. RAZDVAJANJE SPOJENIH POLJA
    # --------------------------------------------------------
    raw[["redni_broj", "datum_knjizenja"]] = raw["redni_datum"].apply(
        lambda x: pd.Series(_split_redni_datum(x))
    )

    raw[["broj_racuna", "datum_izdavanja"]] = raw["racun_datum"].apply(
        lambda x: pd.Series(_split_racun_datum(x))
    )

    # --------------------------------------------------------
    # 8. DATUMI
    # --------------------------------------------------------
    raw["datum_knjizenja"] = pd.to_datetime(raw["datum_knjizenja"], dayfirst=True, errors="coerce")

    raw["datum_izdavanja"] = pd.to_datetime(raw["datum_izdavanja"], dayfirst=True, errors="coerce")

    # --------------------------------------------------------
    # 9. NUMERIČKE KOLONE
    # --------------------------------------------------------
    numeric_cols = [
        "ukupan_iznos",
        "osnovica",
        "oslobodjeno_pdv",
        "naknada_bez_pdv",
        "pdv",
        "pretporez_odbitni",
        "pretporez_neodbitni",
        "uvoz",
        "vrednost_bez_pdv",
        "iznos_pdv",
        "naknada_poljoprivreda",
    ]

    for c in numeric_cols:
        raw[c] = raw[c].map(_to_number)

    # --------------------------------------------------------
    # 10. FINALNI TRANSAKCIONI MODEL
    # --------------------------------------------------------
    out = raw[
        [
            "redni_broj",
            "datum_knjizenja",
            "broj_racuna",
            "datum_izdavanja",
            "dobavljac",
            "pib",
            "osnovica",
            "iznos_pdv",
            "ukupan_iznos",
            "pretporez_odbitni",
            "pretporez_neodbitni",
            "uvoz",
            "naknada_poljoprivreda",
        ]
    ].copy()

    # --------------------------------------------------------
    # 11. ČIŠĆENJE PIB-a
    # --------------------------------------------------------
    out["pib"] = out["pib"].astype(str).str.replace(r"\D", "", regex=True)

    # --------------------------------------------------------
    # 12. UKLANJANJE PRAZNIH REDOVA
    # --------------------------------------------------------
    out = out[out["redni_broj"].notna()]

    out = out.reset_index(drop=True)

    return out


# ------------------------------------------------------------
# TEST BLOK
# ------------------------------------------------------------
if __name__ == "__main__":

    file_path = "uploads/KPR_2025_LOOPING.xlsx"

    df = load_kpr(file_path)

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)

    print(df.head(20))
    print("\nKolone:", df.columns.tolist())
    print("Shape:", df.shape)
