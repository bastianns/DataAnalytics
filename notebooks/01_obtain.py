import pandas as pd
import numpy as np
import os

# 1. Load Dataset
input_path = "../data/raw/dishut-od_18235_jml_pengunjung_wisata_alam__jenis_wisatawan_v1.csv"
output_path = "../data/clean/dishut_clean.csv"

print(f"--- Loading data from {input_path} ---")
df = pd.read_csv(input_path)

# 2. Data Quality Checks
print("\n[A] Total Baris dan Kolom:")
print(f"Baris: {df.shape[0]}, Kolom: {df.shape[1]}")

print("\n[B] Jumlah Missing Value per Kolom:")
print(df.isnull().sum())

print("\n[C] Persentase baris dengan jumlah_wisatawan == 0:")
pct_zero = (df['jumlah_wisatawan'] == 0).mean() * 100
print(f"{pct_zero:.2f}%")

print("\n[D] Cek Duplikasi (Kawasan, Tahun, Jenis Wisatawan):")
duplicates = df.duplicated(subset=['pengelola_kawasan', 'tahun', 'jenis_wisatawan'], keep=False)
print(f"Jumlah baris terduplikasi: {duplicates.sum()}")

print("\n[E] Baris Agregat ('JUMLAH' pada pengelola_kawasan):")
mask_jumlah = df['pengelola_kawasan'].str.contains("JUMLAH", case=False, na=False)
print(f"Jumlah baris agregat ditemukan: {mask_jumlah.sum()}")
if mask_jumlah.any():
    print(df[mask_jumlah]['pengelola_kawasan'].unique())

print("\n[F] Inkonstistensi Nama (Contoh 5 teratas):")
# Mendeteksi nama yang mirip tapi beda (misal spasi ganda atau case)
unique_names = pd.Series(df['pengelola_kawasan'].unique())
normalized = unique_names.str.strip().str.upper().str.replace(r'\s+', ' ', regex=True)
potential_issues = unique_names[normalized.duplicated(keep=False)]
print(f"Potensi isu nama tidak konsisten: {len(potential_issues)}")
if len(potential_issues) > 0:
    print(potential_issues.head())

# 3. Cleaning Process
initial_rows = len(df)

# a. Hapus baris agregat
df_clean = df[~mask_jumlah].copy()

# b. Hapus duplikat
# Sort agar yang memiliki jumlah_wisatawan > 0 berada di atas
df_clean = df_clean.sort_values(by=['pengelola_kawasan', 'tahun', 'jenis_wisatawan', 'jumlah_wisatawan'], ascending=[True, True, True, False])
df_clean = df_clean.drop_duplicates(subset=['pengelola_kawasan', 'tahun', 'jenis_wisatawan'], keep='first')

# c. Tambah kolom tipe_pengelola
def categorize_pengelola(name):
    name = str(name).upper()
    if "TN." in name or "TAMAN NASIONAL" in name:
        return "TN"
    elif "TWA" in name:
        return "TWA"
    elif "TAHURA" in name:
        return "TAHURA"
    elif "KPH" in name:
        return "KPH"
    elif "KSDA" in name:
        return "BKSDA"
    elif any(keyword in name for keyword in ["KBM", "WH", "BUPER", "CURUG", "GUNUNG", "SITU"]):
        return "PERHUTANI"
    else:
        return "LAINNYA"

df_clean['tipe_pengelola'] = df_clean['pengelola_kawasan'].apply(categorize_pengelola)

# 4. Simpan ke CSV
os.makedirs(os.path.dirname(output_path), exist_ok=True)
df_clean.to_csv(output_path, index=False)

# 5. Ringkasan Akhir
print("\n" + "="*30)
print("RINGKASAN PEMBERSIHAN")
print("="*30)
print(f"Baris Awal: {initial_rows}")
print(f"Baris Dihapus: {initial_rows - len(df_clean)}")
print(f"Baris Tersisa: {len(df_clean)}")
print("\nDistribusi per Tipe Pengelola:")
print(df_clean['tipe_pengelola'].value_counts())
print("\nFile disimpan di: " + output_path)
