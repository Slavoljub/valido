from __future__ import annotations

import os
import re
import json
from pathlib import Path
from typing import Literal

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy import create_engine, text

Mode = Literal["dobavljac", "mesec", "kombinovano"]


def get_engine():
    return create_engine("postgresql://postgres:postgres@localhost:5432/valido")


def get_openai_client(project_root: Path | None = None) -> OpenAI:
    root = project_root or Path.cwd()
    if root.name == "notebooks":
        root = root.parent

    load_dotenv(root / ".env", override=True)

    # notebook workaround
    os.environ.pop("SSL_CERT_FILE", None)
    os.environ.pop("SSL_CERT_DIR", None)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY nije učitan iz .env.")

    return OpenAI(api_key=api_key)


def promet_po_dobavljacu(engine, limit: int = 20) -> pd.DataFrame:
    q = text("""
        SELECT
            d.naziv AS dobavljac,
            d.pib,
            COUNT(*) AS broj_stavki,
            SUM(k.osnovica) AS suma_osnovica,
            SUM(k.iznos_pdv) AS suma_pdv,
            SUM(k.ukupan_iznos) AS ukupan_promet
        FROM kpr_transakcije k
        JOIN racuni r ON r.id = k.racun_id
        JOIN dobavljaci d ON d.id = r.dobavljac_id
        GROUP BY d.naziv, d.pib
        ORDER BY ukupan_promet DESC
        LIMIT :limit
    """)
    with engine.begin() as conn:
        return pd.DataFrame(conn.execute(q, {"limit": limit}).mappings().all())


def promet_po_mesecima(engine) -> pd.DataFrame:
    q = text("""
        SELECT
            DATE_TRUNC('month', k.datum_knjizenja)::date AS mesec,
            COUNT(*) AS broj_stavki,
            SUM(k.osnovica) AS suma_osnovica,
            SUM(k.iznos_pdv) AS suma_pdv,
            SUM(k.ukupan_iznos) AS ukupan_promet
        FROM kpr_transakcije k
        GROUP BY DATE_TRUNC('month', k.datum_knjizenja)::date
        ORDER BY mesec
    """)
    with engine.begin() as conn:
        return pd.DataFrame(conn.execute(q).mappings().all())


def _normalizuj_tekst_odgovora(text: str) -> str:
    if not text:
        return "Poštovani,\n\nNema dostupnog sadržaja za prikaz."

    # ukloni markdown znakove
    text = text.replace("**", "").replace("__", "").replace("##", "").replace("`", "")

    # očisti linije
    lines = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            lines.append("")
            continue

        # ukloni bullet prefikse
        line = re.sub(r"^[\-\*\•\–\—\·\▪\◦]+\s*", "", line)

        # ukloni višak specijalnih znakova
        line = re.sub(r"[#*_~<>|\\]+", "", line)

        # sredi razmake
        line = re.sub(r"\s+", " ", line).strip()
        lines.append(line)

    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    # formalni početak
    if not text.lower().startswith("poštovani"):
        text = f"Poštovani,\n\n{text}"

    # svaka sadržajna linija završava interpunkcijom (osim numerisanih naslova)
    final_lines = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            final_lines.append("")
            continue

        if re.match(r"^\d+\)\s+[A-Za-zČĆŽŠĐčćžšđ]", s):
            final_lines.append(s)
            continue

        if s[-1] not in ".!?":
            s += "."

        final_lines.append(s)

    text = "\n".join(final_lines).strip()
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    return text


def build_prompt(mod: Mode, korisnicko_pitanje: str, dob_df: pd.DataFrame, mes_df: pd.DataFrame):

    system = """
Ti si senior finansijski analitičar i revizor specijalizovan za analizu KPR evidencija
(knjiga primljenih računa) u sistemu PDV.

Tvoj zadatak je da na osnovu agregiranih podataka identifikuješ finansijske obrasce,
potencijalne poreske rizike i operativne anomalije.

Analizu radi kao profesionalni finansijski konsultant.

Pravila:

1. Odgovaraj isključivo na srpskom jeziku.
2. Odgovor mora da počne sa 'Poštovani,'.
3. Ne koristi markdown formatiranje niti specijalne oznake kao što su ** ili #.
4. Piši jasne, formalne i potpune rečenice.
5. Ne izmišljaj podatke koji nisu u ulaznim agregatima.

Posebno obrati pažnju na:

- koncentraciju troškova kod malog broja dobavljača
- odnos osnovice i PDV
- nagle promene prometa po mesecima
- zavisnost od pojedinačnih dobavljača
- potencijalne poreske rizike
- sezonske obrasce u prometu

Analiza treba da ima karakter profesionalnog finansijskog izveštaja.
"""

    if mod == "dobavljac":

        data_block = dob_df.to_dict(orient="records")

        user = f"""
Kontekst: analiza po dobavljačima.

Pitanje korisnika:
{korisnicko_pitanje or "Koji dobavljači nose najveći finansijski i poreski rizik?"}

Ulazni podaci:
{json.dumps(data_block, ensure_ascii=False, default=str)}

Na osnovu podataka napiši analizu u sledećoj strukturi:

1) Opšti pregled finansijske strukture dobavljača
2) Ključni finansijski uvidi
3) Potencijalni finansijski i poreski rizici
4) Operativne anomalije
5) Preporučeni naredni koraci
"""

    elif mod == "mesec":

        data_block = mes_df.to_dict(orient="records")

        user = f"""
Kontekst: analiza po mesecima.

Pitanje korisnika:
{korisnicko_pitanje or "Koji meseci odstupaju i šta to može značiti?"}

Ulazni podaci:
{json.dumps(data_block, ensure_ascii=False, default=str)}

Na osnovu podataka napiši analizu u sledećoj strukturi:

1) Opšti pregled finansijskog kretanja
2) Trendovi prometa kroz mesece
3) Potencijalne anomalije ili odstupanja
4) Potencijalni finansijski i poreski rizici
5) Preporučeni naredni koraci
"""

    else:

        data_block = {
            "promet_po_dobavljacu": dob_df.head(15).to_dict(orient="records"),
            "promet_po_mesecima": mes_df.to_dict(orient="records"),
        }

        user = f"""
Kontekst: kombinovana finansijska analiza KPR evidencije.

Pitanje korisnika:
{korisnicko_pitanje or "Daj integrisanu procenu finansijskih i poreskih rizika."}

Ulazni podaci:
{json.dumps(data_block, ensure_ascii=False, default=str)}

Na osnovu dostupnih agregata napiši profesionalni finansijski izveštaj u sledećoj strukturi:

1) Opšti pregled finansijske situacije
2) Ključni finansijski uvidi
3) Identifikovani finansijski i poreski rizici
4) Operativne anomalije i odstupanja
5) Preporučeni naredni koraci za menadžment
"""

    return system, user


def pozovi_kpr_gpt_analizu(mod: Mode = "kombinovano", pitanje: str = "") -> dict:
    engine = get_engine()
    client = get_openai_client()

    dob_df = promet_po_dobavljacu(engine, limit=20)
    mes_df = promet_po_mesecima(engine)
    system_msg, user_msg = build_prompt(mod, pitanje, dob_df, mes_df)

    resp = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.1,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
    )

    raw_answer = resp.choices[0].message.content or ""
    clean_answer = _normalizuj_tekst_odgovora(raw_answer)

    return {
        "mod": mod,
        "pitanje": pitanje,
        "answer": clean_answer,
        "meta": {
            "dobavljaci_rows": len(dob_df),
            "meseci_rows": len(mes_df),
        },
    }