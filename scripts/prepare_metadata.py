"""
Reads data/raw/metadata.csv and adds hierarchical mappings:
- Stage 1: benign/malignant
- Stage 2: HAM10000 7-class labels

The result is written to data/prepared/metadata.csv.

"""

import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_METADATA = PROJECT_ROOT / "data" / "raw" / "metadata.csv"
PREPARED_DIR = PROJECT_ROOT / "data" / "prepared"
PREPARED_METADATA = PREPARED_DIR / "metadata.csv"

# Mapping: diagnosis_3 to HAM10000 7-class Stage 2
DIAGNOSIS_3_TO_STAGE_2 = {
    "Nevus": "nv",
    "Melanoma, NOS": "mel",
    "Basal cell carcinoma": "bcc",
    "Pigmented benign keratosis": "bkl",
    "Dermatofibroma": "df",
    "Solar or actinic keratosis": "akiec",
    "Squamous cell carcinoma, NOS": "akiec",
}


# Values that should be mapped to "vasc" (empty string, NaN, etc.)
VASC_VALUES = {"", "NaN", "nan", "NA", "N/A", "None"}


# Mapping: Stage 2 to Stage 1 (benign/malignant)
STAGE_2_TO_STAGE_1 = {
    "nv": "benign",
    "bkl": "benign",
    "df": "benign",
    "vasc": "benign",
    "mel": "malignant",
    "bcc": "malignant",
    "akiec": "malignant",
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
        fieldnames = list(reader.fieldnames) + ["Stage 1", "Stage 2"]

        rows = []
        unmapped = set()
        for row in reader:
            diag3 = row.get("diagnosis_3", "").strip()

            # Stage 2: HAM10000 7-class label
            if diag3 in VASC_VALUES:
                row["Stage 2"] = "vasc"
            elif diag3 in DIAGNOSIS_3_TO_STAGE_2:
                row["Stage 2"] = DIAGNOSIS_3_TO_STAGE_2[diag3]
            else:
                unmapped.add(diag3)
                row["Stage 2"] = ""

            # Stage 1: benign/malignant
            diag1 = row.get("diagnosis_1", "").strip()
            if row["Stage 2"] in STAGE_2_TO_STAGE_1:
                row["Stage 1"] = STAGE_2_TO_STAGE_1[row["Stage 2"]]
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
    for row in rows:
        s1 = row["Stage 1"]
        s2 = row["Stage 2"]
        s1_counts[s1] = s1_counts.get(s1, 0) + 1
        s2_counts[s2] = s2_counts.get(s2, 0) + 1

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
        
    if unmapped:
        print(f"\n{len(unmapped)} unmapped diagnosis_3 value(s):")
        for val in sorted(unmapped):
            print(f"    - {repr(val)}")


if __name__ == "__main__":
    prepare_metadata()
