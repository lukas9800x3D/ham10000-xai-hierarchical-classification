# HAM10000 — Hierarchical Skin-Lesion Classificationon the HAM10000-Dataset with XAI

## Setup

```bash
# Create Venv
python -m venv venv

# Activate Venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Download Dataset

```bash
python scripts/download_dataset.py
```

Downloads metadata and images from the [ISIC Archive](https://www.isic-archive.com/) (Collection ID: 212) into `data/raw/`.
