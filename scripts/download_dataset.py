"""
Downloads the HAM10000 dataset from the ISIC Archive using ISIC-CLI.

"""

import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = PROJECT_ROOT / "data" / "raw"
COLLECTION_ID = "212" # HAM10000 collection ID


def download_dataset():
    # Download images, metadata, attribution and licenses from the ISIC Archive.
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading HAM10000 dataset to {DATASET_DIR}...")
    subprocess.run(
        ["isic", "image", "download", "--collections", COLLECTION_ID, str(DATASET_DIR)],
        check=True,
    )


# Main
if __name__ == "__main__":
    download_dataset()
