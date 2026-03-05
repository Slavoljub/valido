import pandas as pd


def import_kpr(file_path, engine):

    print("Učitavam Excel...")

    df = pd.read_excel(file_path, header=None)

    clean = pd.DataFrame()

    clean["broj_racuna"] = df.iloc[:,2].astype(str)
    clean["datum"] = pd.to_datetime(df.iloc[:,1], errors="coerce")
    clean["dobavljac"] = df.iloc[:,3].astype(str)
    clean["osnovica"] = pd.to_numeric(df.iloc[:,6], errors="coerce").fillna(0)
    clean["pdv"] = pd.to_numeric(df.iloc[:,10], errors="coerce").fillna(0)

    clean = clean.dropna(subset=["broj_racuna"])

    print("Pravim dobavljače...")

    dobavljaci = clean[["dobavljac"]].drop_duplicates()
    dobavljaci.columns = ["naziv"]

    dobavljaci.to_sql(
        "dobavljaci",
        engine,
        if_exists="append",
        index=False
    )

    print("Upisujem račune...")

    racuni = clean[["broj_racuna","datum"]].drop_duplicates()
    racuni.columns = ["broj_racuna","datum_izdavanja"]

    racuni.to_sql(
        "racuni",
        engine,
        if_exists="append",
        index=False
    )

    print("Upisujem stavke...")

    stavke = clean[["osnovica","pdv"]]

    stavke.to_sql(
        "stavke_racuna",
        engine,
        if_exists="append",
        index=False
    )

    print("KPR uspešno importovan.")