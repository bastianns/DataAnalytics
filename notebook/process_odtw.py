import pandas as pd
import os

# ==========================================
# Load Dataset
# ==========================================
input_path = "../data/raw/jumlah_objek_wisata.csv"
output_path = "../data/processed/odtw_clean.csv"

print("=" * 40)
print("ODTW DATA CLEANING")
print("=" * 40)

df = pd.read_csv(input_path)

# ==========================================
# Data Quality Check
# ==========================================
print("\n[A] Shape Dataset")
print(df.shape)

print("\n[B] Missing Values")
print(df.isnull().sum())

print("\n[C] Duplicate Rows")
print(df.duplicated().sum())

print("\n[D] Kategori Wisata")
print(df["jenis_odtw"].value_counts())

print("\n[E] Rentang Tahun")
print(sorted(df["tahun"].unique()))

# ==========================================
# Cleaning
# ==========================================
initial_rows = len(df)

odtw_clean = df.drop(
    columns=[
        "id",
        "kode_provinsi",
        "nama_provinsi",
        "satuan"
    ]
)

odtw_clean = odtw_clean.rename(
    columns={
        "kode_kabupaten_kota": "kode_wilayah",
        "nama_kabupaten_kota": "kabupaten_kota",
        "jenis_odtw": "kategori_wisata",
        "jumlah_odtw": "jumlah_objek_wisata"
    }
)

odtw_clean = odtw_clean[
    [
        "tahun",
        "kode_wilayah",
        "kabupaten_kota",
        "kategori_wisata",
        "jumlah_objek_wisata"
    ]
]

# ==========================================
# Save Output
# ==========================================
os.makedirs(
    os.path.dirname(output_path),
    exist_ok=True
)

odtw_clean.to_csv(
    output_path,
    index=False
)

# ==========================================
# Summary
# ==========================================
print("\n" + "=" * 40)
print("RINGKASAN PEMROSESAN")
print("=" * 40)

print(f"Baris Awal : {initial_rows}")
print(f"Baris Akhir : {len(odtw_clean)}")

print(f"\nJumlah Tahun : {odtw_clean['tahun'].nunique()}")
print(f"Jumlah Wilayah : {odtw_clean['kabupaten_kota'].nunique()}")

print("\nKategori Wisata:")
print(sorted(odtw_clean["kategori_wisata"].unique()))

print(f"\nFile disimpan di: {output_path}")