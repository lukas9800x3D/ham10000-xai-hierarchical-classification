"""

Reads data/raw/metadata.csv, adds Stage 1 (benign/malignant, Stage 2 (lesion family), and Stage 3 
(HAM10000 7-class label) columns, and saves the result to data/prepared/metadata.csv.

"""

import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_METADATA = PROJECT_ROOT / "data" / "raw" / "metadata.csv"
PREPARED_DIR = PROJECT_ROOT / "data" / "prepared"
PREPARED_METADATA = PREPARED_DIR / "metadata.csv"

# Mapping: diagnosis_3 to HAM10000 class label (Stage 3)
DIAGNOSIS_3_TO_DX = {
    "Nevus": "nv",
    "Melanoma, NOS": "mel",
    "Basal cell carcinoma": "bcc",
    "Pigmented benign keratosis": "bkl",
    "Dermatofibroma": "df",
    "Solar or actinic keratosis": "akiec",
    "Squamous cell carcinoma, NOS": "akiec",
}

# Mapping: diagnosis_2 to Stage 2 (intermediate)
DIAGNOSIS_2_TO_STAGE_2 = {
    "Benign melanocytic proliferations": "melanocytic",
    "Malignant melanocytic proliferations (Melanoma)": "melanocytic",
    "Benign epidermal proliferations": "epidermal",
    "Malignant epidermal proliferations": "epidermal",
    "Indeterminate epidermal proliferations": "epidermal",
    "Malignant adnexal epithelial proliferations - Follicular": "epithelial",
    "Benign soft tissue proliferations - Fibro-histiocytic": "soft_tissue",
    "Benign soft tissue proliferations - Vascular": "vascular",
}

# Values that should be mapped to "vasc" (empty string, NaN, etc.)
VASC_VALUES = {"", "NaN", "nan", "NA", "N/A", "None"}

# Override diagnosis_1 based on diagnosis_2
DIAGNOSIS_1_OVERRIDE = {
    "Indeterminate epidermal proliferations": "Malignant",
}


def prepare_metadata():
    """Read raw metadata, apply diagnosis mapping, and write to data/prepared/."""
    if not RAW_METADATA.exists():
        raise FileNotFoundError(
            f"Raw metadata not found at {RAW_METADATA}. "
            "Run scripts/download_dataset.py first."
        )

    PREPARED_DIR.mkdir(parents=True, exist_ok=True)

    with open(RAW_METADATA, "r", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        fieldnames = list(reader.fieldnames) + ["Stage 1", "Stage 2", "Stage 3"]

        rows = []
        unmapped = set()
        for row in reader:
            diag3 = row.get("diagnosis_3", "").strip()

            # Stage 3: HAM10000 7-class label
            if diag3 in VASC_VALUES:
                row["Stage 3"] = "vasc"
            elif diag3 in DIAGNOSIS_3_TO_DX:
                row["Stage 3"] = DIAGNOSIS_3_TO_DX[diag3]
            else:
                unmapped.add(diag3)
                row["Stage 3"] = ""

            # Stage 2: intermediate grouping based on diagnosis_2
            diag2 = row.get("diagnosis_2", "").strip()
            row["Stage 2"] = DIAGNOSIS_2_TO_STAGE_2.get(diag2, "")

            # Stage 1: diagnosis_1 with override based on diagnosis_2
            diag1 = row.get("diagnosis_1", "").strip()
            if diag2 in DIAGNOSIS_1_OVERRIDE:
                row["Stage 1"] = DIAGNOSIS_1_OVERRIDE[diag2].lower()
            else:
                row["Stage 1"] = diag1.lower()

            rows.append(row)

    # Write prepared metadata
    with open(PREPARED_METADATA, "w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Summary
    total = len(rows)
    s1_counts = {}
    s2_counts = {}
    s3_counts = {}
    for row in rows:
        s1 = row["Stage 1"]
        s2 = row["Stage 2"]
        s3 = row["Stage 3"]
        s1_counts[s1] = s1_counts.get(s1, 0) + 1
        s2_counts[s2] = s2_counts.get(s2, 0) + 1
        s3_counts[s3] = s3_counts.get(s3, 0) + 1

    print(f"Prepared metadata saved to: {PREPARED_METADATA}")
    print(f"  Total rows: {total}\n")
    print(f"  Stage 1 distribution:")
    for label in sorted(s1_counts.keys()):
        display = label if label else "<UNMAPPED>"
        print(f"    {display:>15s}: {s1_counts[label]:>5d}")
        
    print(f"\n  Stage 2 distribution:")
    for label in sorted(s2_counts.keys()):
        display = label if label else "<UNMAPPED>"
        print(f"    {display:>15s}: {s2_counts[label]:>5d}")
        
    print(f"\n  Stage 3 distribution:")
    for label in sorted(s3_counts.keys()):
        display = label if label else "<UNMAPPED>"
        print(f"    {display:>15s}: {s3_counts[label]:>5d}")

    if unmapped:
        print(f"\n{len(unmapped)} unmapped diagnosis_3 value(s):")
        for val in sorted(unmapped):
            print(f"    - {repr(val)}")


if __name__ == "__main__":
    prepare_metadata()
