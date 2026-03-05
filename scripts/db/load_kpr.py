import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine("postgresql://postgres:postgres@localhost:5432/valido")

# učitaj stvarne podatke (npr. iz Excel-a koji si već generisao)
df = pd.read_excel("uploads/KPR_2025_LOOPING.xlsx")

with engine.begin() as conn:

    for _, row in df.iterrows():

        pib = str(row["pib"]).strip()
        naziv = str(row["dobavljac"]).strip()

        # 1 dobavljac
        dobavljac_id = conn.execute(
            text("SELECT id FROM dobavljaci WHERE pib=:pib"),
            {"pib": pib}
        ).scalar()

        if not dobavljac_id:
            dobavljac_id = conn.execute(
                text("""
                INSERT INTO dobavljaci (naziv, pib)
                VALUES (:naziv, :pib)
                RETURNING id
                """),
                {"naziv": naziv, "pib": pib}
            ).scalar()

        # 2 racun
        broj = str(row["broj_racuna"])

        racun_id = conn.execute(
            text("SELECT id FROM racuni WHERE broj_racuna=:broj"),
            {"broj": broj}
        ).scalar()

        if not racun_id:
            racun_id = conn.execute(
                text("""
                INSERT INTO racuni
                (broj_racuna, datum_izdavanja, dobavljac_id)
                VALUES (:broj, :datum, :dobavljac_id)
                RETURNING id
                """),
                {
                    "broj": broj,
                    "datum": row["datum_izdavanja"],
                    "dobavljac_id": dobavljac_id
                }
            ).scalar()

        # 3 transakcija
        conn.execute(
            text("""
            INSERT INTO kpr_transakcije
            (redni_broj, datum_knjizenja, racun_id,
             osnovica, iznos_pdv, ukupan_iznos,
             pretporez_odbitni, pretporez_neodbitni,
             uvoz, naknada_poljoprivreda)
            VALUES
            (:redni_broj, :datum_knjizenja, :racun_id,
             :osnovica, :iznos_pdv, :ukupan_iznos,
             :pretporez_odbitni, :pretporez_neodbitni,
             :uvoz, :naknada_poljoprivreda)
            """),
            {
                "redni_broj": row["redni_broj"],
                "datum_knjizenja": row["datum_knjizenja"],
                "racun_id": racun_id,
                "osnovica": row["osnovica"],
                "iznos_pdv": row["iznos_pdv"],
                "ukupan_iznos": row["ukupan_iznos"],
                "pretporez_odbitni": row["pretporez_odbitni"],
                "pretporez_neodbitni": row["pretporez_neodbitni"],
                "uvoz": row["uvoz"],
                "naknada_poljoprivreda": row["naknada_poljoprivreda"]
            }
        )

print("Svi KPR podaci ubaceni u bazu") 
