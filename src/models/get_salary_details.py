from unidecode import unidecode
import pdfplumber
import pandas as pd
import re
import os
import openai
import textwrap
import matplotlib.pyplot as plt

openai.api_key = "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"
csv_path = "/media/malac/homeMX/malac/projekat/validoAI/data/mom21/plate/mom21_plate_2024_bruto2_sorted.csv"

def extract_salary_details(pdf_path):
    """
    Ekstrahuje Neto zaradu, Na teret zaposlenog, Na teret poslodavca i Bruto 2 iz PDF-a.
    """
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                neto = re.search(r'Iznos Neto Zarade\s*([\d]{1,3}(?:[.,]\d{3})*[.,]\d{2})', text)
                zaposlenog = re.search(r'I Na teret Zaposlenog.*?Ukupno:\s*([\d]{1,3}(?:[.,]\d{3})*[.,]\d{2})', text, re.DOTALL)
                poslodavca = re.search(r'II Na teret Poslodavca.*?Ukupno:\s*([\d]{1,3}(?:[.,]\d{3})*[.,]\d{2})', text, re.DOTALL)
                bruto2 = re.search(r'Ukupni troskovi isplatioca\s*([\d]{1,3}(?:[.,]\d{3})*[.,]\d{2})', text)

                return (
                    neto.group(1) if neto else "N/A",
                    zaposlenog.group(1) if zaposlenog else "N/A",
                    poslodavca.group(1) if poslodavca else "N/A",
                    bruto2.group(1) if bruto2 else "N/A"
                )
    return "N/A", "N/A", "N/A", "N/A"


def analyze_with_gpt(data, uloga):
    if uloga == "vlasnik":
        prompt = f"""
        Poštovani,  

        Ovde sam da vam pomognem da bolje razumete kako se troškovi plata i doprinosa odražavaju na vaše poslovanje.  

        ------
        {data}
        ------

        Ova analiza će vam pružiti ključne uvide u:  

        - Udeo plata u prihodima – Koliki procenat prihoda vaša firma izdvaja za zarade i kako to utiče na profitabilnost?  
        - Održivost troškova rada – Da li su trenutni troškovi plata održivi i kako se mogu optimizovati?  
        - Poređenje sa konkurencijom – Kako vaša firma stoji u odnosu na industrijske proseke kada je reč o prihodima po zaposlenom i EBITDA marži?  
        - Preporuke za optimizaciju – Na osnovu podataka, predložite strategije za poboljšanje efikasnosti i dugoročnu održivost poslovanja.  

        Izveštaj treba da bude jasan, pregledan i koncizan, bez specijalnih znakova ili formatiranja.  
        Svaka rečenica treba biti smisleno završena i analiza treba da bude poslovno upotrebljiva.  

        Srdačan pozdrav,  
        Vaš finansijski analitičar.
        """

    elif uloga == "hr":
        prompt = f"""
        Poštovani,  

        Ovde sam da vam pomognem da bolje razumete strukturu zarada zaposlenih i identifikujete ključne trendove u vašoj firmi.  

        ------
        {data}
        ------

        Ova analiza će vam pružiti uvide u:  

        - Trendove u platama – Kako su se zarade menjale tokom godine i postoje li značajna odstupanja?  
        - Konkurentnost zarada – Da li su plate u vašoj firmi u skladu sa tržišnim standardima?  
        - Strukturu zarada – Postoje li neobične razlike među sektorima i kako ih optimizovati?  
        - Preporuke za HR strategiju – Kako unaprediti sistem plata i zadržati ključne zaposlene?  

        Izveštaj treba da bude konkretan, merljiv i jasan, bez specijalnih znakova ili formatiranja.  
        Svaka rečenica treba biti potpuno završena i analiza mora sadržavati korisne uvide za HR menadžment.  

        Srdačan pozdrav,  
        Vaš finansijski analitičar.
        """

    else:
        return "Nepoznata uloga, ne mogu generisati analizu."

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "Ti si finansijski analitičar. Piši jasno, poslovnim tonom i sa logičkim pasusima. Ne koristi specijalne znakove ili podebljanja. Osiguraj da odgovor uvek završava smislenu misao."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,  # Smanjeno sa 500 na 400 tokena za precizniji odgovor
        temperature=0.1
    )

    clean_response = response["choices"][0]["message"]["content"].strip()

    # Uklanjamo specijalne znakove kao što su ** i ##
    clean_response = re.sub(r"[\*\#]", "", clean_response)

    # Osiguravamo da se odgovor završava na tačku, upitnik ili uzvičnik
    if clean_response[-1] not in ".!?":
        last_period = clean_response.rfind(".")
        if last_period != -1:
            clean_response = clean_response[:last_period + 1]

    # Formatiranje pasusa sa lepšim razmakom
    formatted_response = "\n\n".join(clean_response.split("\n"))

    return formatted_response



#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def process_salary_for_year(pdf_folder, output_csv_path, uloga, use_gpt=False):
    """
    Ekstrahuje podatke iz CSV-a i vraća ceo DataFrame, bez filtriranja kolona po ulozi.
    """
    df = pd.read_csv(output_csv_path)

    print("🛠 DEBUG: Kolone u CSV-u:", df.columns)

    if "Bruto 2" not in df.columns:
        return {"error": "Kolona 'Bruto 2' ne postoji u CSV-u."}, 500

    # Više ne filtriramo po ulozi ovde – to se radi u view funkciji
    return df

#-------------------------------------------------------------------------------------------------------------------------

mesec_map = {
    "Januar": "01", "Februar": "02", "Mart": "03", "April": "04", "Maj": "05", "Jun": "06",
    "Jul": "07", "Avgust": "08", "Septembar": "09", "Oktobar": "10", "Novembar": "11", "Decembar": "12"
}

def clean_month_column(df):
    df["Mesec"] = df["Mesec"].str.replace(r'[^a-zA-Z]', '', regex=True)
    df["Mesec"] = df["Mesec"].map(mesec_map)
    return df



def analyze_bruto2_trends(csv_path, firma_tip="mala firma"):
    """
    Analizira trendove bruto 2 kroz mesece, generiše vremensku seriju i AI uvid sa dodatnim kontekstom.
    """

    if not os.path.exists(csv_path):
        return {"error": f"❌ Fajl ne postoji na putanji: {csv_path}"}

    try:
        df = pd.read_csv(csv_path)

        if "Mesec" not in df.columns:
            return {"error": "Kolona 'Mesec' ne postoji u CSV fajlu."}

        df["Mesec"] = df["Mesec"].astype(str).str.replace(r' \d+$', '', regex=True)

        numeric_columns = ["Neto Zarada", "Na Teret Zaposlenog", "Na Teret Poslodavca", "Bruto 2"]
        for col in numeric_columns:
            df[col] = df[col].astype(str).str.replace(',', '').astype(float)

        df = df.groupby("Mesec").sum().reset_index()

        mesec_map = {
            "Januar": "01", "Februar": "02", "Mart": "03", "April": "04", "Maj": "05", "Jun": "06",
            "Jul": "07", "Avgust": "08", "Septembar": "09", "Oktobar": "10", "Novembar": "11", "Decembar": "12"
        }
        df["Mesec"] = pd.Categorical(df["Mesec"], categories=mesec_map.keys(), ordered=True)
        df = df.sort_values("Mesec")

        meseci = df["Mesec"].tolist()
        neto_values = df["Neto Zarada"].tolist()
        zaposlenog_values = df["Na Teret Zaposlenog"].tolist()
        poslodavca_values = df["Na Teret Poslodavca"].tolist()
        bruto2_values = df["Bruto 2"].tolist()

        graph_path = os.path.join("static", "bruto2_trend.png")

        plt.figure(figsize=(10, 5))
        plt.plot(meseci, neto_values, marker='o', linestyle='-', label="Neto Zarada", color="green")
        plt.plot(meseci, zaposlenog_values, marker='s', linestyle='--', label="Na Teret Zaposlenog", color="orange")
        plt.plot(meseci, poslodavca_values, marker='^', linestyle='-.', label="Na Teret Poslodavca", color="blue")
        plt.plot(meseci, bruto2_values, marker='d', linestyle='-', label="Bruto 2", color="red")

        plt.xlabel("Mesec")
        plt.ylabel("Iznos (RSD)")
        plt.title("Trendovi plata kroz mesece")
        plt.legend()
        plt.grid()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(graph_path)
        plt.close()

        if not os.path.exists(graph_path):
            return {"error": "❌ Grafikon nije sačuvan!"}

        chart_data = {
            "labels": meseci,
            "bruto1": neto_values,
            "bruto2": bruto2_values,
            "na_teret_poslodavca": poslodavca_values
        }

        # 📌 Analiza trenda
        if bruto2_values[-1] > bruto2_values[0] * 1.3:
            saveti = "Uočava se značajan rast bruto troškova krajem godine. Preporučujemo analizu strukture zarada, mogućnost optimizacije doprinosa i konsultaciju sa knjigovođom."
        else:
            saveti = "Troškovi su relativno stabilni tokom godine. Ipak, preporučuje se redovno praćenje i poređenje sa prihodima."

        # 📌 GPT prompt sa valutom i dodatnim kontekstom
        prompt = f"""
Poštovani,

Analiziramo mesečne podatke o zaradama za {firma_tip}. Svi iznosi su u dinarima (RSD).

Meseci: {meseci}
Neto zarada: {neto_values}
Na teret zaposlenog: {zaposlenog_values}
Na teret poslodavca: {poslodavca_values}
Bruto 2: {bruto2_values}

Zasnovano na ovim podacima, generiši jasnu, kulturnu i korisnu analizu kretanja bruto troškova zarada tokom godine.

Posebno obuhvati sledeće:
1. Da li postoji rast/brži pad bruto troškova?
2. Kako to može uticati na poslovanje firme?
3. {saveti}
        """

        odgovor = openai.ChatCompletion.create(
            model="gpt-4-0125-preview",
            messages=[
                {"role": "system", "content": "Ti si AI finansijski savetnik za mala i srednja preduzeća u Srbiji. Daj jasan i smiren uvid u trendove zarada."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.2
        )

        tekst = odgovor["choices"][0]["message"]["content"]
        tekst = re.sub(r"\*\*|__|\*", "", tekst)
        tekst = re.sub(r"^\s*\d+\.\s*", "", tekst, flags=re.MULTILINE)
        tekst = re.sub(r"^#+\s*", "", tekst, flags=re.MULTILINE)
        if not tekst.strip().endswith("."):
            tekst = tekst.rsplit(".", 1)[0] + "."

        return {
            "graph_path": graph_path,
            "chart_data": chart_data,
            "gpt_analysis": tekst
        }

    except Exception as e:
        print("❌ Greška u analizi bruto2 trends:", str(e))
        return {"error": str(e)}


#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def normalize_name(name):
    name = unidecode(name.strip())
    parts = name.split()

    # Lista svih prezimena koje očekuješ u CSV-u:
    poznata_prezimena = ["Vasovic", "Trbojevic", "Markovic", "Nikolic", "Ilic", "Sreckovic"]

    if parts[0].capitalize() in poznata_prezimena:
        # ako je vec prezime prvo, samo vrati formatirano
        return f"{parts[0].capitalize()} {parts[1].capitalize()}"
    else:
        # ako nije, onda pretvori iz "Ime Prezime" u "Prezime Ime"
        return f"{parts[1].capitalize()} {parts[0].capitalize()}"



def obracun_zarade(csv_path, zaposleni, mesec):
    try:
        csv_path = "/media/malac/homeMX/malac/projekat/validoAI/data/mom21/plate/mom21_plate_2024.csv"
        print("\n📌 [LOG] Primljen zahtev:", {"csv_path": csv_path, "zaposleni": zaposleni, "mesec": mesec})

        if not zaposleni or not mesec:
            print("🚨 [ERROR] Nedostaju ključni parametri!")
            return {"error": "Nedostaju ključni parametri (zaposleni, mesec)."}

        if not os.path.exists(csv_path):
            print(f"🚨 [ERROR] CSV fajl nije pronađen na putanji: {csv_path}")
            return {"error": f"CSV fajl ne postoji na putanji: {csv_path}"}

        df = pd.read_csv(csv_path)
        if df.empty:
            print("🚨 [ERROR] CSV fajl je prazan ili nije pravilno učitan.")
            return {"error": "CSV fajl nije pravilno učitan ili je prazan."}

        print(f"✅ [LOG] Uspešno učitan CSV sa {len(df)} redova.")

        df["Mesec"] = df["Mesec"].str.split().str[0].str.strip().str.capitalize()
        df["Prezime i Ime"] = df["Prezime i Ime"].apply(normalize_name)

        zaposleni_norm = normalize_name(zaposleni)
        mesec_norm = mesec.strip().capitalize()

        print("🧑‍💼 [LOG] Traženi zaposleni (normalizovan):", zaposleni_norm)
        print("👥 [LOG] Zaposleni dostupni u CSV-u:", df["Prezime i Ime"].unique())
        print("📅 [LOG] Traženi mesec:", mesec_norm)

        rezultat = df[(df["Prezime i Ime"] == zaposleni_norm) & (df["Mesec"].str.lower() == mesec_norm.lower())]

        if rezultat.empty:
            print(f"⚠️ [WARNING] Nema podataka za '{zaposleni_norm}' u mesecu '{mesec_norm}'.")
            return {
                "poruka": f"Nema podataka za '{zaposleni_norm}' u mesecu '{mesec_norm}'.",
                "dostupna_imena": df["Prezime i Ime"].unique().tolist(),
                "dostupni_meseci": df["Mesec"].unique().tolist()
            }

        print(f"✅ [LOG] Pronađen zapis za zaposlenog '{zaposleni_norm}' u mesecu '{mesec_norm}'.")

        podaci = rezultat.iloc[0]
        satnica = round(float(podaci["Zarada"]) / float(podaci["Časovi"]), 2)
        neto_zarada = round(float(podaci["Zarada"]), 2)

        print(f"💡 [LOG] Računanje završeno: Radni sati={podaci['Časovi']}, Satnica={satnica}, Neto zarada={neto_zarada}")

        return {
            "Prezime i Ime": zaposleni_norm,
            "Mesec": podaci["Mesec"],
            "Radni sati": int(podaci["Časovi"]),
            "Satnica": satnica,
            "Neto Zarada": neto_zarada
        }

    except Exception as e:
        print(f"🚨 [EXCEPTION] Greška u obradi: {str(e)}")
        return {"error": f"Greška u obradi zahteva: {str(e)}"}




#----------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    pdf_folder = "/media/malac/homeMX/malac/projekat/validoAI/data/mom21/plate/mom_plate_2024/"
    output_csv_path = "/media/malac/homeMX/malac/projekat/validoAI/data/mom21_plate_2024_bruto2_sorted.csv"


    pozdravi = ["zdravo", "ćao", "cao", "dobar dan", "pozdrav"]

    user_input = input("Unesite mesec ili poruku: ").strip().lower()

    if user_input in pozdravi:
        print("Dobar dan! 👋 Kako vam danas mogu pomoći sa obračunom zarade?")
    else:
        uloga_korisnika = input("Unesite ulogu (vlasnik/hr): ").strip().lower()
        
        if uloga_korisnika not in ["vlasnik", "hr"]:
            print("Nepoznata uloga, pokušajte ponovo.")
        else:
            df, gpt_analysis = process_salary_for_year(pdf_folder, output_csv_path, uloga=uloga_korisnika, use_gpt=True)

            rezultat = df[df["Mesec"].str.lower() == user_input]

            if rezultat.empty:
                print("Mesec nije pronađen, pokušajte ponovo.")
            else:
                analiza_gpt = analyze_with_gpt(rezultat.to_string(index=False), uloga_korisnika)
                print("\nAnaliza GPT-a:\n", analiza_gpt)

    df, gpt_analysis = process_salary_for_year(pdf_folder, output_csv_path, uloga="vlasnik", use_gpt=True)
    print(df)  # Treba da vidimo samo Bruto 2 za vlasnika


