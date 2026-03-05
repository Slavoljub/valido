import os
import pandas as pd

def extract_plate_pdf(pdf_path):
    import pdfplumber
    import re

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

def extract_salary_from_pdf(pdf_path):
    """
    Ekstrahuje podatke iz PDF-a i vraća ih kao dict, spremne za API i GPT.
    """
    neto, zaposlenog, poslodavca, bruto2 = extract_plate_pdf(pdf_path)

    return {
        "Neto Zarada": neto,
        "Na Teret Zaposlenog": zaposlenog,
        "Na Teret Poslodavca": poslodavca,
        "Bruto 2": bruto2
    }



def transform_plate_dataframe(tup):
    df = pd.DataFrame([tup], columns=["Neto", "Na Teret Zaposlenog", "Na Teret Poslodavca", "Bruto 2"])

    for col in df.columns:
        df[col] = df[col].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
        df[col] = df[col].astype(float)

    return df


def load_plate_data(df, save_csv=False, csv_path="output_plate.csv"):
    if save_csv:
        df.to_csv(csv_path, index=False)
    return df


def etl_plate_process(pdf_path, save_csv=False, csv_path="output_plate.csv"):
    extracted = extract_plate_pdf(pdf_path)
    df = transform_plate_dataframe(extracted)
    final_df = load_plate_data(df, save_csv=save_csv, csv_path=csv_path)
    return final_df


def etl_plate_folder(folder_path, save_csv=True, output_csv="mom21_plate_2024_bruto2_sorted.csv"):
    all_data = []

    for file in os.listdir(folder_path):
        if file.lower().endswith(".pdf"):
            full_path = os.path.join(folder_path, file)
            mesec = os.path.splitext(file)[0].capitalize()

            try:
                df = etl_plate_process(full_path)
                df["Mesec"] = mesec
                all_data.append(df)
            except Exception as e:
                print(f"⚠️ Greška u fajlu {file}: {e}")

    if not all_data:
        raise ValueError("❌ Nema uspešno obrađenih fajlova!")

    final_df = pd.concat(all_data, ignore_index=True)

    if save_csv:
        final_df.to_csv(output_csv, index=False)

    return final_df
