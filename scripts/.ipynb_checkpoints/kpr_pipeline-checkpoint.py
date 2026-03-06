"""KPR document processing pipeline.

Public API:
    process_kpr_document(file_path)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd


def process_kpr_document(file_path: str | Path) -> dict[str, Any]:
    """Process a KPR document and return structured extraction result.

    Pipeline:
        document -> OCR/text ingestion -> parsing/extraction -> validation -> dict(JSON-ready)
    """

    def _clean_text(value: Any) -> str | None:
        if pd.isna(value):
            return None
        text = str(value).replace("\n", " ").replace("\t", " ")
        text = re.sub(r"\s+", " ", text).strip()
        if text in {"", "//", "/ /", "/"}:
            return None
        return text

    def _to_number(value: Any) -> float:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return 0.0
        text = str(value).strip().replace(" ", "")
        if text == "" or text.lower() == "nan":
            return 0.0
        if "," in text and "." in text:
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", ".")
        try:
            return float(text)
        except ValueError:
            return 0.0

    def _split_redni_datum(value: str | None) -> tuple[str | None, str | None]:
        if not value:
            return None, None
        match = re.match(r"^\s*(\d+)\s+(\d{2}/\d{2}/\d{4})\s*$", value)
        if match:
            return match.group(1), match.group(2)
        fallback = re.match(r"^\s*(\d+)\s*$", value)
        if fallback:
            return fallback.group(1), None
        return None, None

    def _split_racun_datum(value: str | None) -> tuple[str | None, str | None]:
        if not value:
            return None, None
        match = re.match(r"^\s*(.+?)\s+(\d{2}/\d{2}/\d{4})\s*$", value)
        if match:
            return match.group(1).strip(), match.group(2)
        return value, None

    def _load_document(path: Path) -> tuple[pd.DataFrame | None, str, str]:
        suffix = path.suffix.lower()
        if suffix in {".xlsx", ".xls"}:
            return pd.read_excel(path, header=None), "excel", ""

        if suffix == ".csv":
            return pd.read_csv(path, header=None), "csv", ""

        if suffix == ".pdf":
            raw_text = ""
            try:
                import pdfplumber  # type: ignore

                with pdfplumber.open(path) as pdf:
                    raw_text = "\n".join((page.extract_text() or "") for page in pdf.pages)
            except Exception:
                raw_text = ""

            ocr_engine = "pdfplumber"
            if not raw_text.strip():
                try:
                    import pytesseract  # type: ignore
                    from PIL import Image  # type: ignore
                    from pdf2image import convert_from_path  # type: ignore

                    pages = convert_from_path(str(path))
                    raw_text = "\n".join(pytesseract.image_to_string(Image.fromarray(page)) for page in pages)
                    ocr_engine = "pytesseract"
                except Exception:
                    ocr_engine = "unavailable"

            table_rows = []
            for line in raw_text.splitlines():
                line = line.strip()
                if line:
                    table_rows.append(re.split(r"\s{2,}", line))
            frame = pd.DataFrame(table_rows) if table_rows else None
            return frame, ocr_engine, raw_text

        raise ValueError(f"Unsupported file type: {suffix}")

    def _extract_from_table(raw: pd.DataFrame) -> pd.DataFrame:
        if raw.empty:
            return pd.DataFrame()

        candidate_index = raw[raw[0].astype(str).str.match(r"^\s*0{2,}\d", na=False)].index
        if len(candidate_index) > 0:
            raw = raw.iloc[candidate_index[0] :].reset_index(drop=True)

        raw = raw.dropna(axis=1, how="all")

        expected_columns = [
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

        for idx in range(len(raw.columns), len(expected_columns)):
            raw[idx] = None
        raw = raw.iloc[:, : len(expected_columns)].copy()
        raw.columns = expected_columns

        for col in ["redni_datum", "dokument", "racun_datum", "dobavljac", "pib"]:
            raw[col] = raw[col].map(_clean_text)

        raw = raw[
            ~raw["dobavljac"]
            .fillna("")
            .str.contains("MEĐUZBIR|MEDJUZBIR|UKUPNO", case=False, regex=True)
        ]

        raw[["redni_broj", "datum_knjizenja"]] = raw["redni_datum"].apply(lambda x: pd.Series(_split_redni_datum(x)))
        raw[["broj_racuna", "datum_izdavanja"]] = raw["racun_datum"].apply(lambda x: pd.Series(_split_racun_datum(x)))

        raw["datum_knjizenja"] = pd.to_datetime(raw["datum_knjizenja"], dayfirst=True, errors="coerce")
        raw["datum_izdavanja"] = pd.to_datetime(raw["datum_izdavanja"], dayfirst=True, errors="coerce")

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
        for col in numeric_cols:
            raw[col] = raw[col].map(_to_number)

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

        out["pib"] = out["pib"].astype(str).str.replace(r"\D", "", regex=True)
        out = out[out["redni_broj"].notna()].reset_index(drop=True)
        return out

    def _validate_rows(df: pd.DataFrame) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []

        for idx, row in df.iterrows():
            calc_total = round(float(row["osnovica"]) + float(row["iznos_pdv"]), 2)
            total = round(float(row["ukupan_iznos"]), 2)
            diff = round(abs(calc_total - total), 2)
            row_errors = []

            pib = (row.get("pib") or "").strip()
            if pib and len(pib) != 9:
                row_errors.append("PIB must have 9 digits")

            if diff > 0.5:
                row_errors.append("Total mismatch: osnovica + iznos_pdv != ukupan_iznos")

            entries.append(
                {
                    "row_index": idx + 1,
                    "document_date": row["datum_izdavanja"].strftime("%Y-%m-%d") if pd.notna(row["datum_izdavanja"]) else None,
                    "invoice_number": row["broj_racuna"],
                    "supplier_name": row["dobavljac"],
                    "supplier_pib": pib if pib else None,
                    "tax_base_amount": float(row["osnovica"]),
                    "vat_amount": float(row["iznos_pdv"]),
                    "total_amount": float(row["ukupan_iznos"]),
                    "validation": {"is_valid": len(row_errors) == 0, "errors": row_errors},
                }
            )

            if row_errors:
                errors.append({"row_index": idx + 1, "errors": row_errors})

        summary = {
            "rows_total": len(df),
            "rows_valid": len(df) - len(errors),
            "rows_invalid": len(errors),
            "errors": errors,
        }
        return entries, summary

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    raw_df, ocr_engine, raw_text = _load_document(path)
    if raw_df is None or raw_df.empty:
        return {
            "document": {"file_path": str(path), "file_type": path.suffix.lower(), "ocr_engine": ocr_engine},
            "entries": [],
            "validation_summary": {
                "rows_total": 0,
                "rows_valid": 0,
                "rows_invalid": 0,
                "errors": ["No extractable rows found"],
            },
            "raw_text": raw_text,
        }

    extracted = _extract_from_table(raw_df)
    entries, validation_summary = _validate_rows(extracted)

    result = {
        "document": {
            "file_path": str(path),
            "file_type": path.suffix.lower(),
            "ocr_engine": ocr_engine,
            "rows_extracted": len(entries),
        },
        "entries": entries,
        "totals": {
            "tax_base_sum": round(float(extracted["osnovica"].sum()), 2) if not extracted.empty else 0.0,
            "vat_sum": round(float(extracted["iznos_pdv"].sum()), 2) if not extracted.empty else 0.0,
            "total_sum": round(float(extracted["ukupan_iznos"].sum()), 2) if not extracted.empty else 0.0,
        },
        "validation_summary": validation_summary,
        "raw_text": raw_text,
    }

    return result


if __name__ == "__main__":
    sample_path = "uploads/KPR_2025_LOOPING.xlsx"
    output = process_kpr_document(sample_path)
    print(output["document"])
    print(output["validation_summary"])