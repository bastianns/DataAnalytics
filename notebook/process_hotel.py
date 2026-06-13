import pandas as pd
import numpy as np
import re
import os
from pathlib import Path


# ==========================================
# Function Preprocessing
# ==========================================
def preprocess_hotel(filepath):

    year = int(re.search(r"(\d{4})", str(filepath)).group(1))

    df = pd.read_csv(filepath)

    df.columns = [
        "jenis_hotel",
        "jan",
        "feb",
        "mar",
        "apr",
        "may",
        "jun",
        "jul",
        "aug",
        "sep",
        "oct",
        "nov",
        "dec",
        "annual"
    ]

    # Hapus header tambahan
    df = df.iloc[3:].reset_index(drop=True)

    # Hapus kolom annual
    df = df.drop(columns=["annual"])

    # Konversi numerik
    month_cols = [
        "jan", "feb", "mar", "apr", "may", "jun",
        "jul", "aug", "sep", "oct", "nov", "dec"
    ]

    df[month_cols] = (
        df[month_cols]
        .replace("-", np.nan)
        .astype(float)
    )

    # Tambahkan tahun
    df["tahun"] = year

    return df


# ==========================================
# Main Pipeline
# ==========================================
print("=" * 40)
print("HOTEL OCCUPANCY DATA CLEANING")
print("=" * 40)

hotel_files = sorted(
    Path("../data/raw").glob(
        "Tingkat Penghunian Kamar Hotel, *.csv"
    )
)

print(f"\nJumlah file ditemukan: {len(hotel_files)}")

all_hotels = []

for file in hotel_files:

    df = preprocess_hotel(file)

    all_hotels.append(df)

    print(f"Processed: {file.name}")

# Gabungkan seluruh tahun
hotel_wide = pd.concat(
    all_hotels,
    ignore_index=True
)

# ==========================================
# Wide -> Long
# ==========================================
hotel_long = pd.melt(
    hotel_wide,
    id_vars=["tahun", "jenis_hotel"],
    value_vars=[
        "jan", "feb", "mar", "apr", "may", "jun",
        "jul", "aug", "sep", "oct", "nov", "dec"
    ],
    var_name="bulan",
    value_name="tpk"
)

# Nama bulan Indonesia
bulan_map = {
    "jan": "Januari",
    "feb": "Februari",
    "mar": "Maret",
    "apr": "April",
    "may": "Mei",
    "jun": "Juni",
    "jul": "Juli",
    "aug": "Agustus",
    "sep": "September",
    "oct": "Oktober",
    "nov": "November",
    "dec": "Desember"
}

hotel_long["bulan"] = hotel_long["bulan"].map(bulan_map)

# Susun ulang kolom
hotel_long = hotel_long[
    [
        "tahun",
        "bulan",
        "jenis_hotel",
        "tpk"
    ]
]

# ==========================================
# Save Output
# ==========================================
output_path = "../data/processed/hotel_clean.csv"

os.makedirs(
    os.path.dirname(output_path),
    exist_ok=True
)

hotel_long.to_csv(
    output_path,
    index=False
)

# ==========================================
# Summary
# ==========================================
print("\n" + "=" * 40)
print("RINGKASAN PEMROSESAN")
print("=" * 40)

print(f"Jumlah Baris : {len(hotel_long)}")
print(f"Jumlah Tahun : {hotel_long['tahun'].nunique()}")
print(f"Jumlah Kategori Hotel : {hotel_long['jenis_hotel'].nunique()}")

print("\nMissing Value TPK:")
print(hotel_long["tpk"].isnull().sum())

print(f"\nFile disimpan di: {output_path}")