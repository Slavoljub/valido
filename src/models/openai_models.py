import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.linear_model import LinearRegression
import openai
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # ovo je veoma bitno!
import matplotlib.pyplot as plt
import sys
import os
import xml.etree.ElementTree as ET
import logging
import csv
import json
import requests
from bs4 import BeautifulSoup
import nltk
import pickle
from rank_bm25 import BM25Okapi
import ast
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import unicodedata
import re




# ---------------------------------------------------
# Inicijalizacija i konfiguracija
# ---------------------------------------------------

# Dodavanje putanje do config direktorijuma (ako nije automatski vidljiv)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../config')))

# Importovanje ključa iz config.py
from config import OPENAI_API_KEY

# Inicijalizacija API ključa
if not OPENAI_API_KEY:
    logging.error("API ključ nije postavljen u config.py.")
    raise ValueError("API ključ nije postavljen u config.py.")

openai.api_key = OPENAI_API_KEY


# Logger za praćenje aplikacije
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---------------------------------------------------
# Funkcije za komunikaciju sa GPT-4 - pppd 
# ---------------------------------------------------

def chat_with_gpt(user_message, chat_history=None):
    """
    Prima korisničku poruku i istoriju čata, vraća odgovor GPT-4 modela.
    """
    if chat_history is None:
        chat_history = []

    # Poruke za GPT-4
    messages = [
        {"role": "system", "content": "Vi ste AI stručnjak za poreske prijave. Odgovarajte jasno i precizno."},
    ] + chat_history + [{"role": "user", "content": user_message}]
    
    try:
        # Poziv GPT-4 modela
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=300,  # Povećali smo max_tokens
            n=1,             # Osigurava samo jedan odgovor
            stop=None        # Uklonjen stop parametar da se ne prekine odgovor
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        logger.error(f"Greška u funkciji chat_with_gpt: {e}", exc_info=True)
        return "Došlo je do greške u obradi vašeg zahteva."

        

def analiza_chat(messages):
    """
    Analizira korisnički upit koristeći fine-tuned GPT model i generiše odgovor + savete.

    Parametri:
        messages (list): Lista poruka u formatu [{'role': 'user', 'content': '...'}].

    Vraća:
        dict: Odgovor AI-ja, podaci za grafikone i saveti za optimizaciju.
    """
    if not messages or not isinstance(messages, list) or 'content' not in messages[0]:
        logger.error("Neispravan format poruka. Očekuje se lista sa ključem 'content'.")
        return {"error": "Neispravan unos podataka."}

    user_input = messages[0]['content']
    
    try:
        response = openai.ChatCompletion.create(
            model="ft:gpt-3.5-turbo-1106:robot:validoai-chat-prihodi:B8678sBt",
            messages=[{"role": "user", "content": user_input}]
        )
        
        if 'choices' not in response or not response['choices']:
            logger.error("Prazan ili neispravan odgovor iz OpenAI API-ja.")
            return {"error": "Nema odgovora iz AI modela."}

        odgovori = response['choices'][0].get('message', {}).get('content', "Greška: Nema sadržaja.")

        # Priprema dodatnih saveta za optimizaciju ako odgovor sadrži "grafikon"
        saveti = generisi_savete_za_poslovanje() if "grafikon" in odgovori else None

        # Osiguranje da chart data postoji (može se povezati sa realnim podacima kasnije)
        data_for_chart = generisi_podatke_za_grafikon() if "grafikon" in odgovori else None

        return {
            "response": odgovori,
            "chartData": data_for_chart,
            "saveti": saveti
        }

    except openai.error.OpenAIError as api_err:
        logger.error(f"OpenAI API greška: {api_err}", exc_info=True)
        return {"error": "Greška u AI odgovoru. Pokušajte kasnije."}

    except Exception as e:
        logger.error(f"Neočekivana greška u analiza_chat: {e}", exc_info=True)
        return {"error": "Neočekivana greška. Kontaktirajte podršku."}



#-----------------------------------------------------------------------------------------------------------------------------------------------
def generisi_savete_za_poslovanje():
    """
    Analizira podatke i pruža savete za optimizaciju poslovanja.
    """
    gpt_prompt = """
    Na osnovu sledećih podataka o prometu, predloži korake za optimizaciju poslovanja:
    - Prihodi: 500,000 RSD
    - Mesta sa najvećim prometom: Beograd, Novi Sad
    - Mesta sa najmanjim prometom: Niš, Kragujevac

    Tvoje preporuke:
    - Predlozi kako povećati promet u slabijim mestima.
    - Identifikuj oblasti gde troškove možemo optimizovati.
    - Ideje za nove marketinške kampanje.
    """
    gpt_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Ti si AI stručnjak za poslovnu analitiku."},
            {"role": "user", "content": gpt_prompt}
        ]
    )
    return gpt_response['choices'][0]['message']['content']

def pripremi_pppd_podatke(csv_path):
    """
    Učitava PPPD podatke i izračunava ključne analitičke vrednosti,
    uključujući obračunski period, radne sate, radne dane i ukupno plaćeno.
    """
    try:
        df = pd.read_csv(csv_path)

        # Provera da li potrebne kolone postoje
        potrebne_kolone = ['Bruto', 'Porez', 'PIO', 'ObracunskiPeriod', 'RadniSati', 'RadniDani', 'UkupnoPlaceno']
        for kolona in potrebne_kolone:
            if kolona not in df.columns:
                raise ValueError(f"Nedostaje kolona: {kolona}")

        # Izračunavanje ključnih vrednosti
        pppd_summary = {
            "Ukupno bruto": df["Bruto"].sum(),
            "Ukupan porez": df["Porez"].sum(),
            "Ukupan PIO": df["PIO"].sum(),
            "Prosečan bruto": df["Bruto"].mean(),
            "Prosečan porez": df["Porez"].mean(),
            "Prosečan PIO": df["PIO"].mean(),
            "Broj prijava": len(df),
            "Najčešći obračunski period": df["ObracunskiPeriod"].mode()[0] if not df["ObracunskiPeriod"].isna().all() else "N/A",
            "Prosečan broj radnih sati": df["RadniSati"].mean(),
            "Prosečan broj radnih dana": df["RadniDani"].mean(),
            "Ukupno plaćeno": df["UkupnoPlaceno"].sum()
        }

        return pppd_summary

    except Exception as e:
        return {"error": str(e)}

# ---------------------------------------------------
# Funkcija za učitavanje podataka
# ---------------------------------------------------

#    Ova funkcija analizira podatke o platama iz CSV fajla i koristi OpenAI GPT-4 za generisanje odgovora.
#    Koraci koje funkcija izvodi:
# 1. Učitava podatke iz CSV fajla.
# 2. Proverava da li su sve potrebne kolone prisutne.
# 3. Normalizuje imena zaposlenih i nazive meseci kako bi se osigurala doslednost u filtriranju.
# 4. Filtrira podatke prema izabranom mesecu, a ako je zadato ime zaposlenog, dodatno filtrira samo za tog radnika.
# 5. Izračunava:
#    - Ukupno isplaćenu sumu za taj mesec
#    - Broj zaposlenih u tom mesecu
#    - Prosečnu neto platu
#    - Trend prosečnih plata za poslednja 3 meseca (Decembar, Januar, Februar)
# 6. Kreira prompt sa analizom plata i trendovima, koji se prosleđuje OpenAI GPT-4 modelu.
# 7. GPT-4 generiše tekstualni odgovor na osnovu dostupnih podataka.
# 8. Funkcija vraća rezultat u JSON formatu, spreman za prikaz u UI ili API odgovoru.
# 
# 📌 Napomena:
# - Ako nema podataka za traženi mesec ili zaposlenog, vraća odgovarajuću poruku.
# - Ako OpenAI API ključ nije postavljen u okruženju, vraća grešku.
# - Podaci su formatirani tako da ih API ili UI može lako obraditi.
#

# 📌 Učitavanje CSV fajla
csv_path = "/media/malac/homeMX/malac/projekat/validoAI/data/mom21/plate/azurirana_analiza_plata.csv"
df_podaci = pd.read_csv(csv_path)


# ✅ Funkcija za normalizaciju teksta (ćirilica u latinicu, velika slova)
def normalize_text(text):
    if not isinstance(text, str):
        return ""

    try:
        # ✅ Ručno konvertujemo ćirilicu u latinicu koristeći mapu
        cirilica_to_latinica = {
            "А": "A", "Б": "B", "В": "V", "Г": "G", "Д": "D", "Ђ": "Đ", "Е": "E", "Ж": "Ž", "З": "Z",
            "И": "I", "Ј": "J", "К": "K", "Л": "L", "М": "M", "Н": "N", "О": "O", "П": "P", "Р": "R",
            "С": "S", "Т": "T", "Ћ": "Ć", "У": "U", "Ф": "F", "Х": "H", "Ц": "C", "Ч": "Č", "Џ": "Dž",
            "Ш": "Š", "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "ђ": "đ", "е": "e", "ж": "ž",
            "з": "z", "и": "i", "ј": "j", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p",
            "р": "r", "с": "s", "т": "t", "ћ": "ć", "у": "u", "ф": "f", "х": "h", "ц": "c", "ч": "č",
            "џ": "dž", "ш": "š"
        }

        text = "".join(cirilica_to_latinica.get(char, char) for char in text)

        # ✅ Uklanjanje specijalnih karaktera i prebacivanje u velika slova
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8").strip().upper()

    except Exception as e:
        print(f"⚠️ Greška u normalizaciji teksta: {e}")
        return text  # Ako ne uspe, vraća originalni tekst

    return text


#------------------------------------------------------------------------------------------------------------------------------------

def analiziraj_plate_sa_gpt(pitanje, df_podaci, api_key):
    """
    Osnovna analiza plata zaposlenog uz korišćenje fine-tuned GPT modela (ValidoAI HR Chat).
    """

    openai.api_key = api_key

    # 📌 Prepoznavanje pozdrava
    pozdravi = ["zdravo", "ćao", "dobar dan", "pozdrav", "hello"]
    pitanje_lower = pitanje.strip().lower()
    if any(p in pitanje_lower for p in pozdravi):
        return "👋 Zdravo! Ja sam vaš **HR pomoćnik**. Kako mogu pomoći u vezi analize plata?"

    # 📌 Ekstrakcija parametara
    ime_zaposlenog, mesec = ekstraktuj_parametre(pitanje)
    if not mesec:
        return "❌ Molimo vas navedite mesec jasno."
    if not ime_zaposlenog:
        return "❌ Molimo vas navedite ime i prezime zaposlenog."

    # 📌 Normalizacija
    df_podaci["Prezime i Ime"] = df_podaci["Prezime i Ime"].str.title().str.strip()
    df_podaci["Mesec"] = df_podaci["Mesec"].str.lower().str.strip()

    ime_zaposlenog = ime_zaposlenog.title().strip()
    mesec = mesec.lower().strip()

    # 📌 Filtriranje podataka
    df_mesec = df_podaci[(df_podaci["Mesec"] == mesec) & (df_podaci["Prezime i Ime"] == ime_zaposlenog)]

    if df_mesec.empty:
        return f"❌ Nema podataka za {ime_zaposlenog} u {mesec.capitalize()}."

    sektor = df_mesec["Sektor"].iloc[0] if "Sektor" in df_mesec.columns else "Nepoznato"
    ukupno_placeno = df_mesec["Ukupno"].sum()
    prosecna_zarada = df_mesec["Zarada"].mean()
    prosecan_radni_sati = df_mesec["Časovi"].mean()

    df_sektor = df_podaci[df_podaci["Sektor"] == sektor]
    prosecna_plata_sektora = df_sektor["Zarada"].mean()

    # 📌 Prompt za GPT (Fine-tuned verzija!)
    prompt = f"""
    HR analiza za zaposlenog: {ime_zaposlenog}
    Period analize: {mesec.capitalize()}

    Detalji zarade:
    - Ukupno isplaćeno: {ukupno_placeno:,.2f} RSD
    - Prosečna zarada zaposlenog: {prosecna_zarada:,.2f} RSD
    - Prosečna zarada u sektoru "{sektor}": {prosecna_plata_sektora:,.2f} RSD
    - Prosečni radni sati: {prosecan_radni_sati:.2f}

    Generiši kratak, jasan, stručan i ljubazan odgovor namenjen zaposlenom, 
    u skladu sa prethodno treniranim stilom ValidoAI HR Chat modela.
    """

    response = openai.ChatCompletion.create(
        model="ft:gpt-3.5-turbo-1106:robot:validoai-chat-plate-2:B7sUOOWA",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=250
    )
    return response["choices"][0]["message"]["content"]

#-----------------------------------------------------------------------------------------------------------------------------------
def prikazi_grafikon(df, ime_zaposlenog, mesec):
    """Prikazuje grafikon sa podacima zaposlenog i prosekom sektora."""
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 5))
    
    kategorije = ["Časovi", "Dani", "Zarada", "Ukupno"]
    vrednosti = [df[k].values[0] for k in kategorije if k in df.columns]
    
    sektor = df["Sektor"].values[0] if "Sektor" in df.columns else "Nepoznato"
    df_sektor = df[df["Sektor"] == sektor]
    proseci_sektora = [df_sektor[k].mean() for k in kategorije if k in df.columns]
    
    bars = plt.bar(kategorije, vrednosti, color="blue", alpha=0.7, label="Zaposleni")
    plt.bar(kategorije, proseci_sektora, color="red", alpha=0.5, label="Sektor")
    
    for bar, v in zip(bars, vrednosti):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + (v * 0.02), f"{v:,.2f}", ha='center', fontsize=12)
    
    plt.xlabel("Kategorije")
    plt.ylabel("Vrednosti")
    plt.title(f"📊 Pregled plata za {ime_zaposlenog.capitalize()} ({mesec.capitalize()})")
    plt.legend()
    plt.xticks(rotation=45)
    plt.show()

# ---------------------------------------------------
# Funkcije za predikcije modela
# ---------------------------------------------------



def get_validoai_general_info(messages, model_id=None, timeout=5):
    # Ova funkcija koristi fine-tuned GPT model specijalizovan za ValidoAI
    # Koristi se za slanje poruka modelu i dobijanje AI objašnjenja o sistemu
    # Ako ne postoji sistemska poruka, automatski je dodaje
    # Omogućava proširenje konverzacije ako postoji prethodna istorija
    # Vraća odgovor i API usage
    
    # Ako poruke nisu lista ili nisu validne, prekida izvršavanje
    if not isinstance(messages, list) or len(messages) == 0:
        logger.error("Poruke nisu validne.")
        return "Potrebna je bar jedna korisnička poruka.", None

    # Proverava da li postoji sistemska poruka, ako ne postoji – dodaje defaultnu
    has_system = any(msg.get("role") == "system" for msg in messages)
    if not has_system:
        system_prompt = {
            "role": "system",
            "content": "Ti si stručni AI pomoćnik unutar ValidoAI sistema. Objašnjavaš funkcionalnosti korisniku jednostavno i tačno."
        }
        messages.insert(0, system_prompt)

    # Ako model nije naveden, koristi se podrazumevani fine-tuned model
    if not model_id:
        model_id = "ft:gpt-3.5-turbo-1106:robot:validoai-chat-pitanja-novija-verzija:B0xVkeCM"

    try:
        # Poziva OpenAI API
        response = openai.ChatCompletion.create(
            model=model_id,
            messages=messages,
            request_timeout=timeout
        )

        # Vraća sadržaj poruke i usage informacije
        answer = response['choices'][0]['message']['content']
        usage = response.get('usage', {})
        return answer, usage

    except openai.error.OpenAIError as api_err:
        logger.error(f"OpenAI API greška: {api_err}", exc_info=True)
        return "OpenAI API trenutno nije dostupan. Molimo pokušajte kasnije.", None

    except Exception as e:
        logger.error(f"Neočekivana greška u get_validoai_general_info: {e}", exc_info=True)
        return "Došlo je do neočekivane greške. Obratite se podršci.", None





# ---------------------------------------------------
# Funkcija za generisanje grafikona
# ---------------------------------------------------

def pppd_prediction(csv_file_path, output_dir):
    """
    Generiše grafikon za PPPD podatke na osnovu CSV datoteke.
    """
    try:
        logger.info(f"Čitam podatke iz CSV fajla: {csv_file_path}")
        df = pd.read_csv(csv_file_path)

        summary = df[['Bruto', 'Porez', 'PIO']].sum()
        categories = summary.index
        values = summary.values

        plt.figure(figsize=(10, 6))
        plt.bar(categories, values, color=['blue', 'green', 'red'])
        plt.title('Sumarni podaci za PPPD')
        plt.xlabel('Kategorije')
        plt.ylabel('Ukupan iznos')

        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'pppd_summary.png')
        plt.savefig(output_path)
        plt.close()

        logger.info(f"Grafikon uspešno sačuvan: {output_path}")
        return f"Grafikon uspešno sačuvan: {output_path}", f'/static/graphs/pppd_summary.png'
    except Exception as e:
        logger.error(f"Greška u pppd_prediction: {e}", exc_info=True)
        return f"Došlo je do greške: {e}", None


# Definisanje putanje do CSV fajla
file_path = "/media/malac/homeMX/malac/projekat/validoAI/data/mom21/promet/cleaned_domaci.csv"
# OpenAI API ključ


def generisi_analizu(mesec):
    try:
        # Učitavanje CSV fajla
        df = pd.read_csv('./data/mom21/promet/cleaned_domaci.csv')

        # Filtriranje za izabrani mesec
        df['Datum Knjizenja'] = pd.to_datetime(df['Datum Knjizenja'])
        df_mesec = df[df['Datum Knjizenja'].dt.month == mesec]

        if df_mesec.empty:
            return {"error": f"Nema podataka za mesec {mesec}."}

        # Grupisanje po mestu i sumiranje prihoda
        grouped = df_mesec.groupby('Mesto')['Ukupno Bez PDV-a'].sum().reset_index()

        # Ukupni prihod
        ukupni_prihod = grouped['Ukupno Bez PDV-a'].sum()

        # Najveći i najmanji prihod po mestu
        mesto_max = grouped.loc[grouped['Ukupno Bez PDV-a'].idxmax()]
        mesto_min = grouped.loc[grouped['Ukupno Bez PDV-a'].idxmin()]

        # Kreiranje grafikona
        plt.figure(figsize=(10, 6))
        plt.bar(grouped['Mesto'], grouped['Ukupno Bez PDV-a'])
        plt.xlabel('Mesto')
        plt.ylabel('Prihodi (RSD)')
        plt.title(f'Prihodi po mestima za mesec {mesec}')

        os.makedirs("static/graphs", exist_ok=True)
        grafikon_path = f'./static/graphs/mesec_{mesec}_grafikon.png'
        plt.savefig(grafikon_path)
        plt.close()

        # GPT Analiza i preporuke
        prompt = f"""
        Finansijska analiza prihoda za mesec broj {mesec}:

        Ukupan prihod svih mesta: {grouped['Ukupno Bez PDV-a'].sum():.2f} RSD.
        Najveći prihod ostvaren je u mestu {mesto_max['Mesto']} sa iznosom {mesto_max['Ukupno Bez PDV-a']} RSD.
        Najmanji prihod ostvaren je u mestu {mesto_min['Mesto']} sa iznosom od {mesto_min['Ukupno Bez PDV-a']} RSD.

        Daj kratak pregled ovih podataka i predloži dve kratke preporuke za povećanje prihoda.
        """

        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ti si AI stručnjak za finansijske analize i daješ kratke konkretne savete."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )

        odgovor = completion.choices[0].message.content

        # Vraćanje konačnih rezultata
        return {
            "ai_analiza": "AI analiza prihoda za dati mesec...",
            "grafikon_json": {
                "labels": grouped_data['Mesto'].tolist(),
                "data": grouped_data['Prihodi'].tolist()
            },
            "mesto_najmanji": mesto_sa_min_prihodom,
            "mesto_najveci": mesto_sa_max_prihodom,
            "iznos_najmanji": min_prihod,
            "iznos_najveci": max_prihod,
            "ukupni_prihod": ukupni_prihod
}


    except Exception as e:
        return {"error": str(e)}

#----------------------------------------------------------------------------------------------------------------------------------------------

def predvidi_prihode():
    """ Analizira prihod na osnovu CSV fajla, vrši predikciju i vraća podatke kao JSON. """
    
    file_path = "/media/malac/homeMX/malac/projekat/validoAI/data/mom21/promet/predikcija_domaceg_prometa.csv"
    
    print("\U0001F4C2 Učitavam CSV fajl...")
    try:
        podaci = pd.read_csv(file_path)
        print("✅ CSV fajl uspešno učitan.")
    except FileNotFoundError:
        print("❌ CSV fajl nije pronađen! Proveri putanju.")
        return {"error": "File not found"}
    
    # Pretprocesiranje podataka
    print("📊 Pretprocesiranje podataka...")
    podaci['Datum Knjizenja'] = pd.to_datetime(podaci['Datum Knjizenja'], errors='coerce')
    podaci = podaci.dropna(subset=['Datum Knjizenja', 'Mesto'])
    podaci['Mesec'] = podaci['Datum Knjizenja'].dt.month + 12 * podaci['Datum Knjizenja'].dt.year
    print("✅ Obrada datuma završena.")
    
    # Predikcija po mestu
    predikcije_po_mestu = {}
    for mesto, group in podaci.groupby('Mesto'):
        X = np.array(group['Mesec']).reshape(-1, 1)
        y = np.array(group['Prihodi']).reshape(-1, 1)
        model = LinearRegression()
        model.fit(X, y)
        buduci_meseci = np.array([X[-1][0] + i for i in range(1, 7)]).reshape(-1, 1)
        predikcije_po_mestu[mesto] = model.predict(buduci_meseci).flatten().tolist()
    
    # Predikcija po datumu (ukupno)
    X = np.array(podaci['Mesec']).reshape(-1, 1)
    y = np.array(podaci['Prihodi']).reshape(-1, 1)
    model = LinearRegression()
    model.fit(X, y)
    buduci_meseci = np.array([X[-1][0] + i for i in range(1, 7)]).reshape(-1, 1)
    ukupne_predikcije = model.predict(buduci_meseci).flatten().tolist()
    
    # Vraćanje podataka u JSON formatu
    return {
        "predikcije_po_mestu": predikcije_po_mestu,
        "ukupne_predikcije": ukupne_predikcije
    }

def predikcija_domaceg_prometa():
    """API endpoint koji vraća predikcije domaćeg prometa sa detaljnim AI objašnjenjem i preporukama."""

    rezultat = predvidi_prihode()

    # Priprema teksta predikcija za GPT prompt
    predikcije_po_mestu = rezultat.get("predikcije_po_mestu", {})
    predikcije_lista = [f"{mesto}: {iznosi[-1]:,.2f} RSD" for mesto, iznosi in predikcije_po_mestu.items()]
    predikcije_tekst = "\n".join(predikcije_lista)

    # Definisanje detaljnog prompta za GPT
    prompt = f"""
    📈 AI Predikcija Prihoda:

    Na osnovu linearne regresije, predviđeni mesečni prihodi za pojedine lokacije su sledeći:
    {predikcije_tekst}

    Molim te da korisniku detaljno i razumljivo objasniš:
    - Šta ove predikcije tačno znače za njegovo poslovanje?
    - Kako može da ih iskoristi za bolje planiranje aktivnosti i poslovnih odluka?
    - Koje konkretne korake može preduzeti u skladu sa rezultatima?

    Tvoj ton treba da bude ljubazan, profesionalan i pun razumevanja, sa fokusom na praktične savete i preporuke, bez preterano tehničkih izraza.
    """

    print("🤖 Šaljem upit OpenAI API-ju za generisanje detaljnog objašnjenja...")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Odgovaraj ljubazno, jasno i stručno. Pružaj detaljne, ali lako razumljive informacije i konkretne preporuke prilagođene poslovnom korisniku."},
                {"role": "user", "content": prompt}
            ]
        )

        rezultat["gpt4_objasnjenje"] = response["choices"][0]["message"]["content"]
        print("✅ Objašnjenje uspešno generisano.")

    except Exception as e:
        rezultat["gpt4_objasnjenje"] = f"❌ Došlo je do greške pri generisanju AI objašnjenja: {e}"
        print("❌ Greška pri pozivu OpenAI API-ja:", e)

    return rezultat


# ---------------------------------------------------
# Funkcija za obradu PPPD čata
# ---------------------------------------------------

def process_pppd_chat(messages):
    """
    Obrada korisničkog pitanja koristeći specifični PPPD model.
    """
    try:
        model_id = "ft:gpt-3.5-turbo-1106:robot:pppd-bolja-verzija:B0yQfQeH"
        if not model_id:
            raise ValueError("Model ID nije definisan.")

        if not isinstance(messages, list) or len(messages) < 2:
            raise ValueError("Poruke moraju sadržavati sistemsku i korisničku poruku.")

        logger.debug(f"Poruke prosleđene modelu: {messages}")

        response = openai.ChatCompletion.create(
            model=model_id,
            messages=messages
        )

        return response['choices'][0]['message']['content'], response['usage']
    except Exception as e:
        logger.error(f"Greška u process_pppd_chat: {e}", exc_info=True)
        return "Došlo je do greške prilikom obrade vašeg zahteva.", None


# ---------------------------------------------------
# Funkcija za generisanje sistemske poruke
# ---------------------------------------------------

def generate_system_message(data):
    """
    Generiše sistemsku poruku na osnovu učitanih PPPD podataka.
    """
    if len(data) > 0:
        context = f"Trenutno imamo {len(data)} prijava. Koristi ove podatke za odgovore na pitanja."
    else:
        context = "Trenutno nema dostupnih podataka o PPPD prijavama."

    return {
        "role": "system",
        "content": f"Ti si asistent za analizu i obradu PPPD podataka. {context}"
    }



#---------------------------------------------------
               # Nove funkcije
#-------------------------------------------------------



def generisi_odgovor_sa_gpt(period: str):
    rezime, tabela = generisi_odgovor_za_period(period)
    if tabela is not None:
        gpt_prompt = f"Analiziraj sledeće podatke:\n{rezime}\nObjasni korisniku značenje ovih podataka."
        gpt_odgovor = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ti si ekspert za analizu podataka. Molimo te da daješ kompletne odgovore i završavaš rečenice u skladu sa pitanjem."},
                {"role": "user", "content": gpt_prompt}
            ],
            temperature=0.7,
            max_tokens=500  # Postavite maksimalan broj tokena
        )
        # Obradite odgovor koristeći funkciju `obradi_odgovor`
        raw_odgovor = gpt_odgovor['choices'][0]['message']['content']
        final_odgovor = obradi_odgovor(raw_odgovor)
        return final_odgovor, tabela
    else:
        return rezime, None


# ---------------------------------------------------
# Funkcije za analizu podataka i generisanje grafikona
# ---------------------------------------------------


def analiziraj_i_generisi_grafikon(mesec):
    """
    Analizira podatke za traženi mesec i generiše grafikon prihoda po mestima.
    """
    csv_path = 'data/mom21/promet/cleaned_domaci.csv'  # Tačan path
    try:
        # Učitavanje podataka iz CSV-a
        podaci = pd.read_csv(csv_path)
        podaci['Datum Knjizenja'] = pd.to_datetime(podaci['Datum Knjizenja'])
        podaci['Mesec'] = podaci['Datum Knjizenja'].dt.month

        # Filtriranje podataka za traženi mesec
        podaci_mesec = podaci[podaci['Mesec'] == mesec]
        if podaci_mesec.empty:
            return None, "Nema podataka za traženi mesec.", None

        # Grupisanje po mestima i sumiranje prihoda
        grouped_data = podaci_mesec.groupby('Mesto').agg({
            'Prihodi': 'sum'
        }).reset_index()

        # Generisanje grafikona
        plt.figure(figsize=(10, 6))
        plt.bar(grouped_data['Mesto'], grouped_data['Prihodi'], color='skyblue', edgecolor='black')
        plt.xlabel('Mesto', fontsize=12)
        plt.ylabel('Prihodi (RSD)', fontsize=12)
        plt.title(f'Prihodi po mestima za mesec {mesec}', fontsize=14)
        plt.xticks(rotation=45, fontsize=10, ha='right')
        plt.tight_layout()

        # Čuvanje grafikona u static/graphs folder
        os.makedirs("static/graphs", exist_ok=True)
        grafikon_file = f"mesec_{mesec}_grafikon.png"
        grafikon_path = f"static/graphs/{grafikon_file}"
        plt.savefig(grafikon_path)
        plt.close()

        # Vraća relativnu putanju za frontend
        return grouped_data, None, f"/static/graphs/{grafikon_file}"
    except Exception as e:
        return None, str(e), None

# vec imas gore definisanu funkciju generisi_analizu (ostaviš je netaknutu)

def prepoznaj_mesec_i_generisi_odgovor(poruka: str):
    """
    Analizira korisničku poruku da bi prepoznala mesec i generisala analizu.
    """
    meseci = {
        "januar": 1, "februar": 2, "mart": 3, "april": 4,
        "maj": 5, "jun": 6, "jul": 7, "avgust": 8,
        "septembar": 9, "oktobar": 10, "novembar": 11, "decembar": 12
    }

    # Koristimo regex da pronađemo prvi mesec u poruci
    mesec_match = re.search(r"\b(januar|februar|mart|april|maj|jun|jul|avgust|septembar|oktobar|novembar|decembar)\b", poruka.lower())
    
    if not mesec_match:
        return {"response": f"Nažalost, ne mogu da pronađem traženi mesec u vašoj poruci: '{poruka}'. Pokušajte sa nazivom meseca, npr. 'jun' ili 'decembar'."}
    
    mesec_naziv = mesec_match.group(0)
    mesec = meseci[mesec_naziv]

    # Generisanje analize
    rezultati = generisi_analizu(mesec=mesec)
    if "error" in rezultati:
        return {"response": f"Došlo je do greške: {rezultati['error']}"}

    # Formiranje odgovora
    return {
        "response": f"Analiza za mesec {mesec_naziv}:\n{rezultati['ai_predlozi']}\n\n"
                    f"Grafikon je generisan. Pogledajte putanju: {rezultati['grafikon_path']}",
        "grafikon_path": rezultati["grafikon_path"],
        "data": rezultati["grouped_data"]
    }


# ---------------------------------------------------
# Funkcija `generate_prediction_and_visualization_clean`
# ---------------------------------------------------
# Ova funkcija učitava podatke iz CSV fajla, obrađuje ih za vremensku analizu,
# trenira linearni regresioni model i generiše predikcije prihoda za narednih 6 meseci.
# Kreira interaktivan grafikon istorijskih podataka i predikcija,
# i koristi GPT-4 za generisanje profesionalnog objašnjenja rezultata.

def generate_prediction_and_visualization_clean(csv_path, openai_key):
    
    # Postavljanje OpenAI API ključa
    openai.api_key = openai_key
    
    # 1. Učitavanje CSV fajla
    try:
        data = pd.read_csv(csv_path)
    except FileNotFoundError:
        return "CSV fajl nije pronađen. Proverite putanju do fajla."

    # 2. Pretprocesiranje podataka
    try:
        data['Datum Knjizenja'] = pd.to_datetime(data['Datum Knjizenja'], errors='coerce')
        data = data.dropna(subset=['Datum Knjizenja'])
        data['Month'] = data['Datum Knjizenja'].dt.month + 12 * data['Datum Knjizenja'].dt.year
    except KeyError:
        return "CSV fajl ne sadrži kolonu 'Datum Knjizenja' ili je format neispravan."

    # 3. Priprema podataka za linearnu regresiju
    try:
        X = np.array(data['Month']).reshape(-1, 1)
        y = np.array(data['Prihodi']).reshape(-1, 1)
    except KeyError:
        return "CSV fajl ne sadrži kolonu 'Prihodi' ili su podaci neispravni."

    # 4. Treniranje modela linearne regresije
    model = LinearRegression()
    model.fit(X, y)

    # 5. Predikcija za narednih 6 meseci
    future_months = np.array([X[-1][0] + i for i in range(1, 7)]).reshape(-1, 1)
    predictions = model.predict(future_months)

    # Kreiranje DataFrame-a za predikcije
    future_dates = pd.date_range(data['Datum Knjizenja'].max(), periods=7, freq='M')[1:]
    prediction_df = pd.DataFrame({
        'Datum': future_dates,
        'Vrednost': predictions.flatten(),
        'Tip': 'Predikcija'
    })

    # 6. Kombinovanje sa istorijskim podacima za grafikon
    historical_data = data[['Datum Knjizenja', 'Prihodi']].rename(columns={'Datum Knjizenja': 'Datum', 'Prihodi': 'Vrednost'})
    historical_data['Tip'] = 'Istorijski podaci'
    combined_df = pd.concat([historical_data, prediction_df])

    # 7. Generisanje objašnjenja putem GPT-4
    historical_summary = f"Istorijski podaci o prihodima pokrivaju period od {historical_data['Datum'].min().date()} do {historical_data['Datum'].max().date()}."
    predicted_values = ', '.join([f"{date.strftime('%B %Y')}: RSD {value:,.2f}" for date, value in zip(future_dates, predictions.flatten())])

    prompt = f"""
    Imamo podatke o prometu prikazane u grafikonu. {historical_summary}
    Na osnovu linearne regresije predvideli smo sledeće prihode za narednih 6 meseci:
    {predicted_values}.
    
    Objasni korisniku na pregledan i profesionalan način šta ovo znači i kako može da koristi ove podatke za planiranje poslovanja. Uključi preporuke za buduće korake.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Ti si poslovni analitičar sa iskustvom u finansijskoj analizi."},
            {"role": "user", "content": prompt}
        ]
    )

    gpt_response = response.choices[0].message['content']

    # 8. Kreiranje grafikona
    fig = go.Figure()

    # Dodavanje istorijskih podataka sa glatkom linijom
    fig.add_trace(go.Scatter(
        x=historical_data['Datum'],
        y=historical_data['Vrednost'],
        mode='lines+markers',
        name='Istorijski podaci',
        line=dict(color='lightblue', width=3, dash='solid'),
        marker=dict(size=4, color='lightblue')
    ))

    # Dodavanje predikcija sa istaknutom bojom
    fig.add_trace(go.Scatter(
        x=prediction_df['Datum'],
        y=prediction_df['Vrednost'],
        mode='lines+markers',
        name='Predikcija',
        line=dict(color='orange', width=3, dash='dot'),
        marker=dict(size=6, color='orange', symbol='circle')
    ))

    # Modernizacija stila grafikona
    fig.update_layout(
        title='Promet - Istorijski i Predikcija za narednih 6 meseci',
        xaxis_title='Datum',
        yaxis_title='Prihodi (RSD)',
        template='plotly_white',
        title_x=0.5,
        font=dict(family="Arial, sans-serif", size=16, color="black"),
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            zeroline=False,
            showline=True,
            linewidth=1,
            linecolor='gray'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            zeroline=False,
            showline=True,
            linewidth=1,
            linecolor='gray'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend=dict(
            bgcolor='white',
            bordercolor='lightgray',
            borderwidth=1,
            font=dict(size=12)
        )
    )

    # Dodavanje hover informacija
    fig.update_traces(
        hoverinfo="name+x+y",
        marker=dict(opacity=0.8, line=dict(width=1, color='black'))
    )

    # Prikaz grafikona
    fig.show()

    # Vraćanje odgovora GPT-4
    return gpt_response


# ----------------------------------------------------------------
# Ažurirani Web Scraping kod za finansijske vesti i poresku upravu
# ----------------------------------------------------------------




def scrape_nbs_exchange_rates():
    """
    Scrapuje kursnu listu sa sajta Narodne banke Srbije.
    """
    url = "https://nbs.rs/static/nbs_site/gen/cirilica/30/kurs/Indikativni_Kurs_20.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    print("🔍 Status kod odgovora:", response.status_code)

    # Ako nije uspešan odgovor, prekidamo
    if response.status_code != 200:
        print(f"❌ Greška: Ne mogu da pristupim stranici, status kod: {response.status_code}")
        return []

    # Parsiranje HTML-a bez dodatnog dekodiranja
    soup = BeautifulSoup(response.content, "html.parser")

    # Pronalazak prve tabele
    tabela = soup.find("table")
    if not tabela:
        print("❌ Greška: Nema pronađenih tabela.")
        return []

    kursna_lista = []
    rows = tabela.find_all("tr")

    for i in range(len(rows) - 1):
        # Prepoznajemo valutu
        th_element = rows[i].find("th", class_="panel-date")
        if th_element:
            valuta = th_element.text.strip()
            # Uzimamo kurs iz sledećeg reda
            kurs_th = rows[i + 1].find("th")
            if kurs_th:
                kurs = kurs_th.text.strip().replace(",", ".")  # Zamena zareza tačkom
                kursna_lista.append({"valuta": valuta, "kurs": kurs})

    if not kursna_lista:
        print("⚠️ Nisu pronađeni validni podaci.")
    else:
        print("📡 Scraped data:", kursna_lista)  # Ispis u terminalu

    return kursna_lista

# Testiranje funkcije
#print(scrape_nbs_exchange_rates())

def detect_currency_question(user_input):
    """
    Proverava da li korisničko pitanje zahteva scraping kursne liste.
    """
    keywords = ["kurs", "valuta", "devizni kurs", "EUR/RSD", "USD/RSD", "dinara", "koliko je kurs"]
    return any(keyword in user_input.lower() for keyword in keywords)

def handle_exchange_rate_question(user_input):
    """
    Obrada korisničkog pitanja o kursu.
    Ako AI prepozna da je pitanje vezano za kurs, pokreće scraping i analizu.
    """
    if detect_currency_question(user_input):
        kursna_lista = scrape_nbs_exchange_rates()

        if not kursna_lista:
            return "❌ Trenutno ne možemo preuzeti kursne podatke iz Narodne banke Srbije."

        ai_analiza = analyze_exchange_rates(kursna_lista)

        response_text = "Najnoviji kursni podaci:\n"
        response_text += "\n".join([f" {item['valuta']}: {item['kurs']} RSD" for item in kursna_lista[:5]])
        response_text += f"\n\n Analiza:\n{ai_analiza}"

        return response_text
    else:
        return "Vaše pitanje ne izgleda kao upit vezan za kurs. Molimo vas da precizirate šta vas zanima."


def analyze_exchange_rates(kursna_lista):
    """
    Analizira kursnu listu pomoću GPT-4 i daje jasne, sažete i kompletne odgovore.
    """
    kurs_text = "\n".join([f"{item['valuta']}: {item['kurs']} RSD" for item in kursna_lista])

    prompt = f"""
    Na osnovu najnovijih deviznih kurseva iz Narodne banke Srbije:
    
    {kurs_text}

    Ukratko analiziraj:
    - Da li je kurs EUR/RSD i USD/RSD stabilan?
    - Kako ovo može uticati na ekonomiju Srbije?
    - Kakav savet bi dao privrednicima?

    Budi jasan i precizan u odgovoru, bez previše tehničkih detalja.
    Završavaj rečenice u celosti i nemoj prekidati misao.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ti si ekonomski analitičar specijalizovan za finansijska tržišta Srbije."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,  # Manje kreativnosti, precizniji odgovori
            max_tokens=400,  # Povećan limit da ne seče rečenice
            stop=["\n\n"]  # Osigurava da završi ceo odgovor pre nego što stane
        )

        full_response = response['choices'][0]['message']['content'].strip()

        # Provera da li je odgovor prekinut
        if full_response[-1] not in ".!?":
            full_response += " ..."  # Dodajemo naznaku da je možda isečen

        return full_response.encode('utf-8').decode('utf-8')

    except Exception as e:
        return f"❌ Greška pri komunikaciji sa OpenAI API-jem: {str(e)}"

# Logger za praćenje grešaka
logger = logging.getLogger(__name__)

def scrape_svi_zakoni():
    """
    Scrapuje samo naslove i linkove poreskih zakona, bez preuzimanja punog teksta.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    rezultati = []

    for url in ZAKONI_URLS:
        try:
            print(f"📌 Scrapujem: {url}")  # Prikazujemo koji URL obrađujemo
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Proveravamo da li je zahtev uspešan
            
            soup = BeautifulSoup(response.content, "html.parser")

            # Pronalazimo naslov zakona
            naslov = soup.find("h1").text.strip() if soup.find("h1") else "Nepoznato"

            rezultati.append({"naslov": naslov, "link": url})

        except requests.exceptions.RequestException as e:
            print(f"❌ Greška pri preuzimanju: {str(e)}")
            rezultati.append({"naslov": "Greška", "link": url, "tekst": f"Neuspešan zahtev: {str(e)}"})

    return rezultati


# Logger za praćenje grešaka
logger = logging.getLogger(__name__)

ZAKONI_URLS = [
    "https://www.purs.gov.rs/preduzetnici/pregled-propisa/zakoni/9941/zakon-o-porezu-na-dohodak-gradjana.html",
    "https://www.purs.gov.rs/preduzetnici/pregled-propisa/zakoni/9461/zakon-o-doprinosima-za-obavezno-socijalno-osiguranje.html",
    "https://www.purs.gov.rs/preduzetnici/pregled-propisa/zakoni/274/zakon-o-akcizama.html",
    "https://www.purs.gov.rs/preduzetnici/pregled-propisa/zakoni/9255/zakon-o-opstem-upravnom-postupku.html",
    "https://www.purs.gov.rs/preduzetnici/pregled-propisa/zakoni/352/zakon-o-porezima-na-upotrebu-drzanje-i-nosenje-dobara.html",
    "https://www.purs.gov.rs/preduzetnici/pregled-propisa/zakoni/7773/zakon-o-poreskom-postupku-i-poreskoj-administraciji.html",
    "https://www.purs.gov.rs/preduzetnici/pregled-propisa/zakoni/202/zakon-o-porezu-na-dodatu-vrednost.html",
    "https://www.purs.gov.rs/preduzetnici/pregled-propisa/zakoni/3605/zakon-o-rokovima-izmirenja-novcanih-obaveza-u-komercijalnim-transakcijama-.html",
    "https://www.purs.gov.rs/preduzetnici/pregled-propisa/zakoni/7775/zakon-o-fiskalizaciji.html",
    "https://www.purs.gov.rs/preduzetnici/pregled-propisa/zakoni/330/zakon-o-porezima-na-imovinu.html",
    "https://www.purs.gov.rs/preduzetnici/pregled-propisa/zakoni/5667/zakon-o-budzetskom-sistemu.html",
    "https://www.purs.gov.rs/preduzetnici/pregled-propisa/zakoni/8321/zakon-o-obavljanju-placanja-pravnih-lica-preduzetnika-i-fizickih-lica-koja-ne-    obavljaju-delatnost-.html",
    "https://www.purs.gov.rs/preduzetnici/pregled-propisa/zakoni/6841/zakon-o-digitalnoj-imovini.html",
    "https://www.purs.gov.rs/preduzetnici/pregled-propisa/zakoni/6397/zakon-o-deviznom-poslovanju.html",
    "https://www.purs.gov.rs/preduzetnici/pregled-propisa/zakoni/5397/zakon-o-inspekcijskom-nadzoru-.html",
    "https://www.purs.gov.rs/preduzetnici/pregled-propisa/zakoni/5033/zakon-o-pojednostavljenom-radnom-angazovanju-na-sezonskim-poslovima-u-odredjenim-delatnostima.html",
    "https://www.purs.gov.rs/preduzetnici/pregled-propisa/zakoni/396/zakon-o-mirovanju-i-otpisu-duga-po-osnovu-doprinosa-za-obavezno-zdravstveno-osiguranje.html",
    "https://www.purs.gov.rs/preduzetnici/pregled-propisa/zakoni/398/zakon-o-uslovnom-otpisu-kamata-i-mirovanju-poreskog-duga.html"
]

def scrape_svi_zakoni():
    """
    Scrapuje sve zakone sa liste URL-ova i vraća naslove i linkove.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    rezultati = []

    for url in ZAKONI_URLS:
        try:
            print(f"📌 Scrapujem: {url}")  # Prikazujemo koji URL obrađujemo
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Proveravamo da li je zahtev uspešan
            
            soup = BeautifulSoup(response.content, "html.parser")

            # Pronalazimo naslov zakona
            naslov = soup.find("h1").text.strip() if soup.find("h1") else "Nepoznato"

            rezultati.append({"naslov": naslov, "link": url})

        except requests.exceptions.RequestException as e:
            print(f"❌ Greška pri preuzimanju: {str(e)}")
            rezultati.append({"naslov": "Greška", "link": url, "tekst": f"Neuspešan zahtev: {str(e)}"})

    return rezultati

#--------------------------------------------------------------------------------------------------------------------------------------------
# ValidoAI 2.0 IDEJA:
# Dodati verifikaciju odgovora od strane poreskog savetnika (human-in-the-loop).
# Omogućiti korisniku da označi da li je odgovor bio koristan → future feedback loop.
# Prikaz badge-a 'Beta AI Poreski Savetnik' u UI sa tooltip objašnjenjem.
#--------------------------------------------------------------------------------------------------------------------------------------------

def analyze_poreski_propisi(user_message):
    # Ova funkcija koristi web scraping da prikupi poreske zakone u Srbiji
    # Zatim koristi GPT model da generiše jasan, stručan i razuman odgovor
    # Funkcija obrađuje korisničko pitanje i kontekstualno daje savete

    try:
        zakoni = scrape_svi_zakoni()

        # Ako nema zakona, vraća obaveštenje
        if not zakoni:
            return "Trenutno nisu dostupni poreski propisi za analizu."

        # Uzimamo najviše 10 zakona i formatiramo ih
        zakoni_text = "\n\n".join([
            f"{z['naslov']}\n{z['link']}" for z in zakoni[:10] if 'naslov' in z and 'link' in z
        ])

        # Prompt se konstruiše tako da koristi kontekst i pitanje korisnika
        prompt = f"""
Korisnik je poreski obveznik koji traži tačnu i jasnu informaciju u vezi sa svojim obavezama ili pravima. Njegovo pitanje glasi:
"{user_message}"

Ovo su relevantni poreski propisi u Srbiji:
{zakoni_text}

Odgovori:
- Profesionalno i jasno, kao iskusan poreski savetnik.
- Jednostavnim jezikom, bez pravnog žargona.
- Bez korišćenja simbola, numeracija, crtica ili bullet-a.

Struktura odgovora:
1. Ukratko objasni suštinu zakona koji su povezani sa pitanjem.
2. Kaži korisniku kako to utiče na njegove obaveze ili prava.
3. Ako želi više, ponudi mu linkove i savet da se obrati poreskom savetniku.

Ton: stručan, informativan, razumljiv.
"""

        # Poziv GPT modela
        response = openai.ChatCompletion.create(
            model="gpt-4-0125-preview",
            messages=[
                {"role": "system", "content": "Ti si profesionalni AI asistent za poreske propise u Srbiji."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=700
        )

        # Parsiranje odgovora
        odgovor = response['choices'][0]['message']['content'] if 'choices' in response else ""

        # Čišćenje neželjenih simbola ako postoje
        simboli = ["**", "*", "1️⃣", "2️⃣", "3️⃣", "-", "•"]
        for s in simboli:
            odgovor = odgovor.replace(s, "")
        return odgovor.strip() if odgovor else "Nije generisan validan odgovor."

    except Exception as e:
        logger.error(f"Greška u analyze_poreski_propisi: {e}", exc_info=True)
        return "Došlo je do tehničke greške. Molimo pokušajte kasnije."


#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Postavljamo tačnu putanju do `nltk_data`
NLTK_DATA_PATH = "/media/malac/homeMX/malac/projekat/validoAI/nltk_data/tokenizers/punkt"
#print("✅ NLTK sada koristi putanju:", NLTK_DATA_PATH)

# Zamena `word_tokenize()` sa alternativnim tokenizatorom
def custom_tokenize(text):
    """
    Zamena za `word_tokenize()`, kako bismo izbegli `punkt_tab` problem.
    """
    return text.lower().replace(",", "").replace(".", "").split()

# Testni zakoni (simulacija scrapovanog teksta)
zakoni_text = [
    "Porez na dohodak građana iznosi 10% i obračunava se na prihode od rada, kapitala i drugih izvora.",
    "Standardna stopa PDV-a u Srbiji je 20%, dok je smanjena stopa 10% za određene proizvode.",
    "Doprinosi za socijalno osiguranje uključuju PIO, zdravstveno osiguranje i osiguranje za nezaposlene.",
    "Porez na imovinu se obračunava na osnovu tržišne vrednosti nekretnina i varira od 0.1% do 0.4%.",
    "Akcize se primenjuju na gorivo, duvanske proizvode i alkohol, a stope variraju zavisno od proizvoda.",
    "Poreske olakšice uključuju povlastice za startap kompanije i investicije u nove tehnologije.",
    "Kazne za neplaćanje poreza mogu iznositi od 50.000 RSD do 2.000.000 RSD u zavisnosti od prekršaja.",
    "Fiskalizacija je obavezna za sve privredne subjekte i podrazumeva izdavanje fiskalnih računa.",
    "Prijava poreza se vrši do 31. marta svake godine za prethodnu fiskalnu godinu."
]

zakoni_naslovi = [
    "Zakon o porezu na dohodak građana",
    "Zakon o PDV-u",
    "Zakon o doprinosima",
    "Zakon o porezu na imovinu",
    "Zakon o akcizama",
    "Poreske olakšice",
    "Kazne za neplaćanje poreza",
    "Zakon o fiskalizaciji",
    "Rokovi za poreske prijave"
]

zakoni_linkovi = [
    "https://www.purs.gov.rs/zakon-o-porezu-na-dohodak-gradjana",
    "https://www.purs.gov.rs/zakon-o-pdv",
    "https://www.purs.gov.rs/zakon-o-doprinosima",
    "https://www.purs.gov.rs/zakon-o-porezu-na-imovinu",
    "https://www.purs.gov.rs/zakon-o-akcizama",
    "https://www.purs.gov.rs/poreske-olaksice",
    "https://www.purs.gov.rs/kazne-za-neplacanje-poreza",
    "https://www.purs.gov.rs/zakon-o-fiskalizaciji",
    "https://www.purs.gov.rs/rokovi-za-poreske-prijave"
]

# Kreiramo BM25 indeks sa konzistentnim tokenizovanjem
corpus = [custom_tokenize(doc) for doc in zakoni_text]
bm25 = BM25Okapi(corpus)

def pretrazi_zakone(upit):
    """
    Pretražuje poreske propise koristeći BM25 i zatim koristi GPT-4 da pruži dodatno objašnjenje.
    """
    try:
        print(f"🔍 Pitanje primljeno: {upit}")  
        query_tokens = custom_tokenize(upit)  
        print(f"📝 Tokenizovani upit: {query_tokens}")  

        scores = bm25.get_scores(query_tokens)
        najbolji_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:2]  # Vraćamo top 2 rezultata

        # Debug: Ispis svih rezultata pretrage sa ocenama BM25
        print("📊 Rangirani rezultati BM25:")
        for i in najbolji_idx:
            print(f"  - {zakoni_naslovi[i]} (Skor: {scores[i]})")

        odgovori = [
            {
                "naslov": zakoni_naslovi[i],
                "link": zakoni_linkovi[i],
                "tekst": zakoni_text[i]
            }
            for i in najbolji_idx if scores[i] > 0
        ]

        if not odgovori:
            return [{"naslov": "Nema relevantnih rezultata", "link": "", "tekst": "Pokušajte sa preciznijim pitanjem."}]

        # 🔹 **Dodatno AI objašnjenje uz GPT-4**
        zakon_info = "\n\n".join([f"📌 *{z['naslov']}*\n🔗 {z['link']}\n📄 {z['tekst']}" for z in odgovori])

        prompt = f"""
        Korisnik pita: {upit}

        Ovo su relevantni poreski propisi:

        {zakon_info}

        Na osnovu ovih podataka, objasni korisniku zakon u kontekstu njegovog pitanja.
        Koristi jednostavan i razumljiv jezik. Ako zakon sadrži procente, objasni ih sa primerima.
        """

        # **Pozivamo GPT-4 API za dodatno objašnjenje**
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ti si AI specijalizovan za poreske propise u Srbiji."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=700
        )

        ai_odgovor = response['choices'][0]['message']['content']
 
        return {
            "ai_odgovor": ai_odgovor,
            "rezultati": odgovori
        }

    except Exception as e:
        print(f"❌ Greška u `pretrazi_zakone()`: {e}")
        return {"error": f"Došlo je do greške: {e}"}

# TEST: Pokreni testove
if __name__ == "__main__":
    print("\n🔎 Testiranje scraping funkcije...")
    zakoni = scrape_svi_zakoni()
    
    for zakon in zakoni:
        print(f"\n📌 {zakon.get('naslov', 'Nepoznato')}")
        print(f"🔗 Link: {zakon.get('link', 'Nema linka')}\n")

    print("\n💡 Testiranje AI analize poreskih propisa...")
    test_question = "Koji su najnoviji propisi o porezu na dohodak?"
    odgovor = analyze_poreski_propisi(test_question)
    print("\n📌 AI Odgovor:")
    print(odgovor)

# AI Skripta za pretragu dobavljača i analizu plaćanja
# -------------------------------------------------------------
# Ova skripta omogućava pretragu sličnih dobavljača koristeći OpenAI embeddings
# i analizu plaćanja po dobavljačima.
# 1. Učitava podatke iz CSV fajla i konvertuje numeričke vrednosti u odgovarajući format.
# 2. Generiše embedding za uneti upit koristeći OpenAI text-embedding-ada-002 model.
# 3. Računa sličnost između dobavljača koristeći cosine similarity.
# 4. Analizira kome je najviše plaćeno (ukupni iznos, iznos bez PDV-a, PDV iznos).
# 5. Interaktivni UI omogućava korisniku unos podataka i pretragu putem dugmeta.
# 6. Omogućava pretragu po iznosima koristeći AI sličnost dobavljača i embeddings.
# 7. Prikazuje listu dobavljača sa dodatnim podacima o fakturama i plaćanjima.


# 🔹 Učitaj CSV fajl sa podacima o dobavljačima i embedding vrednostima
file_path = "/media/malac/homeMX/malac/projekat/validoAI/data/mom21/promet/mom_sef/mom_ulazne_2024_dobavljac_embeddings.csv"
data = pd.read_csv(file_path)

# 🔹 Funkcija za ispravljanje formata brojeva
def clean_number(value):
    if isinstance(value, str):
        value = value.replace(".", "").replace(",", "")
    try:
        return float(value) / 100
    except ValueError:
        return None

# 🔹 Konvertovanje numeričkih vrednosti
data["Iznos"] = data["Iznos"].apply(clean_number)
data["Iznos bez PDV-a"] = data["Iznos bez PDV-a"].apply(clean_number)
data["PDV iznos"] = data["PDV iznos"].apply(clean_number)

def parse_embedding(x):
    """Konvertuje string u numpy niz ako je validan."""
    try:
        return np.array(ast.literal_eval(x)) if isinstance(x, str) else np.array(x)
    except Exception as e:
        logging.warning(f"⚠️ Greška pri parsiranju embedding-a: {e}")
        return None

data["Dobavljac_embedding"] = data["Dobavljac_embedding"].apply(parse_embedding)

# Provera koliko embeddinga je uspešno učitano
logging.info(f"✅ Uspešno učitano embeddings-a: {data['Dobavljac_embedding'].apply(lambda x: x is not None).sum()}")

#--------------------------------------------------------------------------------------------------------------------------------------

# 🔹 Kreiranje mape embeddings-a
data["Dobavljac"] = data["Dobavljac"].str.strip().str.upper()
supplier_embeddings = dict(zip(data["Dobavljac"], data["Dobavljac_embedding"]))

# 🔹 Funkcija za generisanje embeddinga pomoću OpenAI API
def get_query_embedding(query):
    """Generiše embedding za korisnički upit pomoću OpenAI text-embedding-ada-002 modela."""
    try:
        response = openai.Embedding.create(
            input=query,
            model="text-embedding-ada-002"
        )
        return np.array(response["data"][0]["embedding"])
    except Exception as e:
        logging.error(f"❌ Greška prilikom generisanja embedding-a: {e}")
        return None
#---------------------------------------------------------------------------------------------------------------------------------------

# Ova funkcija analizira sličnost između dobavljača.
# Korisnik unosi naziv jednog dobavljača.
# Sistem koristi embeddinge i iznose plaćanja da izračuna sličnosti sa drugim dobavljačima.
# Zatim koristi GPT-4 da generiše profesionalnu analizu sličnosti.
# Korisno za strategiju nabavke, diversifikaciju i pregovaranje.

def find_similar_suppliers_gpt(query, top_n=5):
    query = query.strip().upper()
    logging.info(f"🔍 API pretraga za dobavljača: '{query}'")

    original_supplier_data = data[data["Dobavljac"] == query]

    if original_supplier_data.empty:
        logging.warning(f"⚠️ Dobavljač '{query}' nije pronađen.")
        return {"message": "Nema pronađenih dobavljača za zadati upit."}

    original_embedding = get_query_embedding(query)
    if original_embedding is None:
        return {"message": "Greška pri generisanju embeddinga."}

    original_total_paid = original_supplier_data["Iznos"].sum()

    suppliers_analysis = []
    for dobavljac, embedding in supplier_embeddings.items():
        if dobavljac == query or embedding is None:
            continue

        supplier_data = data[data["Dobavljac"] == dobavljac]
        total_paid = supplier_data["Iznos"].sum()

        financial_similarity = max(0, 100 - (abs(total_paid - original_total_paid) / original_total_paid) * 100)
        embedding_similarity = np.dot(original_embedding, embedding) / (
            np.linalg.norm(original_embedding) * np.linalg.norm(embedding)
        )
        combined_similarity = (0.7 * financial_similarity) + (0.3 * embedding_similarity * 100)

        suppliers_analysis.append({
            "Dobavljac": dobavljac,
            "Ukupno placeno": total_paid,
            "Finansijska slicnost": round(financial_similarity, 2),
            "Embedding slicnost": round(embedding_similarity * 100, 2),
            "Ukupna slicnost": round(combined_similarity, 2)
        })

    suppliers_analysis = sorted(suppliers_analysis, key=lambda x: x["Ukupna slicnost"], reverse=True)[:top_n]

    prompt = f"""Analiza sličnosti dobavljača sa originalnim dobavljačem {query}.

Sličnost između dobavljača analizira se kroz dva ključna aspekta:

1. Finansijska sličnost – Odnosi se na sličnost u ukupnim iznosima transakcija koje su klijenti ostvarili sa dobavljačima.
2. Opisna sličnost – Odnosi se na vrstu usluga ili proizvoda koje dobavljači nude i njihovu povezanost sa originalnim dobavljačem.

Pronađeni slični dobavljači:

"""

    for i, supplier in enumerate(suppliers_analysis, start=1):
        prompt += (
            f"{i}. {supplier['Dobavljac']}\n"
            f"   - Finansijska sličnost: {supplier['Finansijska slicnost']}%\n"
            f"   - Opisna sličnost: {supplier['Embedding slicnost']}%\n"
            f"   - Ukupno plaćeno: {supplier['Ukupno placeno']:,.2f} RSD\n\n"
        )

    prompt += (
        "Na osnovu analize, sumiraj glavne sličnosti i objasni kako se ovi dobavljači mogu koristiti u poslovanju. "
        "Pojasni i kako njihova sličnost može uticati na pregovore o cenama i diversifikaciju snabdevanja."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "Ti si ekspert za finansijske analize dobavljača."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.2
    )

    gpt_analysis = response["choices"][0]["message"]["content"]

    # Čišćenje teksta od markdown i oznaka
    gpt_analysis = re.sub(r"\*\*|__|\*", "", gpt_analysis)
    gpt_analysis = re.sub(r"^\s*\d+\.\s*", "", gpt_analysis, flags=re.MULTILINE)
    gpt_analysis = re.sub(r"^#+\s*", "", gpt_analysis, flags=re.MULTILINE)

    # Osiguranje da se ne prekida u pola rečenice
    if not gpt_analysis.strip().endswith("."):
        gpt_analysis = gpt_analysis.rsplit(".", 1)[0] + "."

    gpt_analysis = gpt_analysis.strip()

    return {
        "originalni_dobavljac": query,
        "slicni_dobavljaci": suppliers_analysis,
        "gpt_analiza": gpt_analysis
    }






#-------------------------------------------------------------------------------------------------------------------------------------------------------------------


# Importovanje ključa iz config.py
from config import OPENAI_API_KEY

# Inicijalizacija API ključa
if not OPENAI_API_KEY:
    logging.error("API ključ nije postavljen u config.py.")
    raise ValueError("API ključ nije postavljen u config.py.")

openai.api_key = OPENAI_API_KEY
df_embeddings = pd.read_csv('/media/malac/homeMX/malac/projekat/validoAI/data/mom21/promet/mom_sef/mom_ulazne_2024_dobavljac_embeddings.csv')

def parse_embedding(x):
    try:
        return np.array(ast.literal_eval(x))
    except Exception:
        return None

df_embeddings["Dobavljac_embedding"] = df_embeddings["Dobavljac_embedding"].apply(parse_embedding)
supplier_embeddings = dict(zip(df_embeddings["Dobavljac"], df_embeddings["Dobavljac_embedding"]))

def get_similar_suppliers(supplier_name, top_n=10):
    if supplier_name not in supplier_embeddings:
        raise ValueError("Dobavljač nije pronađen.")

    query_embedding = supplier_embeddings[supplier_name]
    similarities = {}

    for sup, emb in supplier_embeddings.items():
        if emb is not None:
            sim_score = cosine_similarity(query_embedding.reshape(1, -1), emb.reshape(1, -1))[0][0]
            similarities[sup] = sim_score

    sorted_results = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[1:top_n+1]

    result_json = [{"dobavljac": sup, "slicnost": f"{score*100:.2f}%"} for sup, score in sorted_results]

    prompt = f"""
    Analiziraj sledeće dobavljače koji su najsličniji dobavljaču '{supplier_name}' prema procentima sličnosti:
    {', '.join([f'{item["dobavljac"]} ({item["slicnost"]})' for item in result_json])}

    Kreiraj kratak, jasan i stručan izveštaj zašto ovi dobavljači imaju najveću sličnost i na šta treba obratiti pažnju prilikom analize finansijskih odnosa sa njima.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=500
    )

    analysis = response["choices"][0]["message"]["content"]

    return {"results": result_json, "gpt_analiza": analysis}


# Primer korišćenja:
# print(get_similar_suppliers("UNICREDIT BANK SRBIJA"))
