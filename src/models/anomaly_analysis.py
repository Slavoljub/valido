import os
import pandas as pd
import xml.etree.ElementTree as ET
import openai


openai.api_key = "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"
csv_path = "/media/malac/homeMX/malac/projekat/validoAI/data/mom21/plate/mom21_plate_2024.csv"
xml_folder_path = "/media/malac/homeMX/malac/projekat/validoAI/data/mom21/pppd/"


def safe_float(x):
    """Konvertuje vrednost u float, ako nije moguće, vraća 0.0."""
    try:
        return float(str(x).replace(",", "."))
    except:
        return 0.0

def ucitaj_csv_bruto(csv_path):
    try:
        # ✅ Provera da li fajl postoji
        if not os.path.exists(csv_path):
            raise ValueError(f"⚠️ CSV fajl ne postoji: {csv_path}")

        try:
            df = pd.read_csv(csv_path)
        except pd.errors.EmptyDataError:
            raise ValueError("⚠️ CSV fajl je prazan!")
        except Exception as e:
            raise ValueError(f"⚠️ Greška pri učitavanju CSV-a: {e}")

        print("✅ CSV fajl uspešno učitan! Prvih 5 redova:")
        print(df.head())

        # ✅ Provera dostupnih kolona
        print("📌 Kolone u učitanom CSV fajlu:", df.columns.tolist())

        if "Mesec" not in df.columns:
            raise ValueError("⚠️ CSV fajl ne sadrži kolonu 'Mesec'!")

        # ✅ Normalizacija naziva meseca (uklanja oznake tipa "deo 2")
        df["Mesec"] = df["Mesec"].str.split().str[0]

        # ✅ Kreiranje "MesecBroj" kolone
        meseci_map = {
            "Januar": "01", "Februar": "02", "Mart": "03", "April": "04",
            "Maj": "05", "Jun": "06", "Jul": "07", "Avgust": "08",
            "Septembar": "09", "Oktobar": "10", "Novembar": "11", "Decembar": "12"
        }

        df["MesecBroj"] = df["Mesec"].map(meseci_map)

        # ✅ Provera da li je "MesecBroj" pravilno generisan
        if df["MesecBroj"].isnull().any():
            print("❌ Greška: 'MesecBroj' nije pravilno generisan! Pogrešni podaci:")
            print(df[df["MesecBroj"].isnull()][["Mesec", "MesecBroj"]])
            raise ValueError("Neuspešna konverzija meseca u broj!")

        print("✅ Generisana 'MesecBroj' kolona:", df[["Mesec", "MesecBroj"]].head())

        # ✅ Provera potrebnih kolona
        potrebne_kolone = ["Mesec", "Prezime i Ime", "Časovi", "Zarada"]
        for kolona in potrebne_kolone:
            if kolona not in df.columns:
                raise ValueError(f"⚠️ Nedostaje kolona: {kolona}")

        # ✅ Dodavanje godine i formatiranje meseca
        df["Godina"] = "2024"
        df["MesecFormatiran"] = df["Mesec"] + " " + df["Godina"]

        # ✅ Provera numeričkih podataka i računanje satnice
        df["Radni sati"] = df["Časovi"].apply(safe_float)
        df["Satnica"] = df.apply(
            lambda row: safe_float(row["Zarada"]) / safe_float(row["Časovi"]) if safe_float(row["Časovi"]) > 0 else 0,
            axis=1
        )

        print("✅ CSV fajl uspešno obrađen! Spremno za analizu.")
        return df

    except Exception as e:
        print(f"❌ Greška prilikom učitavanja CSV-a: {e}")
        return None



# Funkcija za učitavanje XML bruto podataka (Bruto 2 + porezi i doprinosi)
def ucitaj_sve_xml(xml_folder_path):
    podaci = []
    ns = {'ns1': 'http://pid.purs.gov.rs'}

    for file in os.listdir(xml_folder_path):
        if file.endswith(".xml"):
            xml_path = os.path.join(xml_folder_path, file)
            tree = ET.parse(xml_path)
            root = tree.getroot()

            obracunski_period = root.find(".//ns1:ObracunskiPeriod", ns)
            mesec = obracunski_period.text if obracunski_period is not None else "Nepoznato"

            for z in root.findall(".//ns1:PodaciOPrihodima", ns):
                ime = z.find("ns1:Ime", ns)
                prezime = z.find("ns1:Prezime", ns)
                bruto = z.find("ns1:Bruto", ns)
                osnovica_porez = z.find("ns1:OsnovicaPorez", ns)
                porez = z.find("ns1:Porez", ns)
                pio = z.find("ns1:PIO", ns)
                zdr = z.find("ns1:ZDR", ns)
                nez = z.find("ns1:NEZ", ns)

                podaci.append({
                    "Prezime i Ime": f"{prezime.text.strip().upper() if prezime is not None else 'NEPOZNATO'} {ime.text.strip().upper() if ime is not None else 'NEPOZNATO'}",
                    "Bruto 2": safe_float(bruto.text.replace(",", ".")) if bruto is not None else 0,
                    "Mesec": mesec,
                    "Osnovica Porez": safe_float(osnovica_porez.text.replace(",", ".")) if osnovica_porez is not None else 0,
                    "Porez": safe_float(porez.text.replace(",", ".")) if porez is not None else 0,
                    "PIO": safe_float(pio.text.replace(",", ".")) if pio is not None else 0,
                    "Zdravstveno": safe_float(zdr.text.replace(",", ".")) if zdr is not None else 0,
                    "Nezaposlenost": safe_float(nez.text.replace(",", ".")) if nez is not None else 0
                })

    return pd.DataFrame(podaci)

def analiziraj_anomalije(csv_path: str, xml_folder_path: str) -> pd.DataFrame:
    df_bruto1 = ucitaj_csv_bruto(csv_path)
    df_bruto2 = ucitaj_sve_xml(xml_folder_path)
    df_merged = pd.merge(df_bruto1, df_bruto2, on=["Prezime i Ime", "Mesec"], how="outer").fillna(0)

    # 📌 Sada imamo sve ključne podatke
    df_merged["Regres"] = df_merged["Regres"].apply(safe_float)
    df_merged["Minuli Rad"] = df_merged["Minuli Rad"].apply(safe_float)

    df_merged["Bruto 1"] = df_merged["Ukupno"]  # Bruto 1 je ukupna zarada iz CSV-a
    df_merged["Bruto 2"] = df_merged["Bruto 2"].apply(safe_float)  # Bruto 2 dolazi iz XML-a

    # 📌 Nova formula za razliku: uzimamo u obzir Regres i Minuli Rad
    df_merged["Razlika"] = (df_merged["Bruto 1"] + df_merged["Regres"] + df_merged["Minuli Rad"]) - df_merged["Bruto 2"]
    df_merged["Razlika"] = df_merged["Razlika"].apply(lambda x: round(x, 2))  

    df_merged["Razlika (%)"] = df_merged.apply(
        lambda row: round(((row["Bruto 2"] - (row["Bruto 1"] + row["Regres"] + row["Minuli Rad"])) / row["Bruto 1"]) * 100, 2)
        if row["Bruto 1"] != 0 else 0.00,
        axis=1
    )

    return df_merged.sort_values(by=["Mesec", "Prezime i Ime"]).reset_index(drop=True)






#Ovako dobijaš:
# Brzu analizu anomalija (sekunde).
# GPT analizu pokrećeš samo kada je stvarno potrebna kroz API.
#Probaj ovo, pa možemo brzo srediti endpoint da koristi GPT samo pojedinačno na zahtev iz UI-ja. 🚀

