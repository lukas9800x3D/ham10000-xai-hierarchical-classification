"""
Downloads HAM10000 lesion segmentation masks from Kaggle using kagglehub
and copies them into data/masks.

"""

import shutil
from pathlib import Path

import kagglehub


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MASKS_DIR = PROJECT_ROOT / "data" / "masks"
KAGGLE_DATASET = "tschandl/ham10000-lesion-segmentations"


def download_masks():
    MASKS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Downloading mask dataset '{KAGGLE_DATASET}' with kagglehub...")
    downloaded_dir = Path(kagglehub.dataset_download(KAGGLE_DATASET))
    print(f"Kaggle cache directory: {downloaded_dir}")

    file_count = 0
    for src_path in downloaded_dir.rglob("*"):
        if not src_path.is_file():
            continue

        rel_path = src_path.relative_to(downloaded_dir)
        dst_path = MASKS_DIR / rel_path
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dst_path)
        file_count += 1

    print(f"Copied {file_count} file(s) to: {MASKS_DIR}")


if __name__ == "__main__":
    download_masks()
