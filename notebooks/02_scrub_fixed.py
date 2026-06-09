import pandas as pd
import numpy as np
import os

# Set paths
input_path = "../data/raw/dishut-od_18235_jml_pengunjung_wisata_alam__jenis_wisatawan_v1.csv"
output_path = "../data/clean/dishut_clean_v2.csv"

print(f"--- Loading data from {input_path} ---")
df = pd.read_csv(input_path)
initial_rows = len(df)

# STEP 1 — Hapus baris agregat
mask_jumlah = df['pengelola_kawasan'].str.contains("JUMLAH", case=False, na=False)
rows_agregat = mask_jumlah.sum()
df = df[~mask_jumlah].copy()
print(f"STEP 1: Dihapus {rows_agregat} baris agregat (summary row palsu)")

# STEP 2 — Hapus duplikat
# Simpan hanya baris dengan jumlah_wisatawan terbesar untuk kombinasi (kawasan, jenis, tahun)
df_sorted = df.sort_values(by=['pengelola_kawasan', 'jenis_wisatawan', 'tahun', 'jumlah_wisatawan'], ascending=[True, True, True, False])
df_clean = df_sorted.drop_duplicates(subset=['pengelola_kawasan', 'jenis_wisatawan', 'tahun'], keep='first').copy()
rows_duplikat = len(df) - len(df_clean)
print(f"STEP 2: Dihapus {rows_duplikat} baris duplikat (menyimpan nilai terbesar)")

# STEP 3 — Flag data 2019=2020 identik
# Inisialisasi kolom data_flag
df_clean['data_flag'] = 'NORMAL'

# Flag 2020 sebagai SUSPECT_COPY
mask_2020 = df_clean['tahun'] == 2020
df_clean.loc[mask_2020, 'data_flag'] = 'SUSPECT_COPY'
print(f"STEP 3: {mask_2020.sum()} baris 2020 di-flag sebagai SUSPECT_COPY")

# STEP 4 — Flag data 2022 incomplete
mask_2022 = df_clean['tahun'] == 2022
df_clean.loc[mask_2022, 'data_flag'] = 'INCOMPLETE_YEAR'
print(f"STEP 4: {mask_2022.sum()} baris 2022 di-flag sebagai INCOMPLETE_YEAR")

# STEP 5 — Tambah kolom tipe_pengelola
def categorize_pengelola(name):
    name = str(name).upper()
    if any(k in name for k in ['TN.', 'TAMAN NASIONAL', 'BALAI TN', 'BALAI BESAR TN']):
        return "TN"
    elif "TWA" in name:
        return "TWA"
    elif "TAHURA" in name:
        return "TAHURA"
    elif "KPH" in name:
        return "KPH"
    elif "KSDA" in name:
        return "BKSDA"
    elif any(k in name for k in ['WH ', 'BUPER', 'KBM']):
        return "PERHUTANI"
    else:
        return "LAINNYA"

df_clean['tipe_pengelola'] = df_clean['pengelola_kawasan'].apply(categorize_pengelola)
print("STEP 5: Kategorisasi tipe_pengelola selesai")

# STEP 6 — Simpan dan print ringkasan akhir
os.makedirs(os.path.dirname(output_path), exist_ok=True)
df_clean.to_csv(output_path, index=False)

print("\n" + "="*40)
print("RINGKASAN AKHIR (CLEANING V2)")
print("="*40)
print(f"Total baris awal: {initial_rows}")
print(f"Total baris akhir: {len(df_clean)}")
print(f"Data tersimpan di: {output_path}")

print("\nTotal Pengunjung per Tahun:")
print(df_clean.groupby('tahun')['jumlah_wisatawan'].sum())

print("\nJumlah Kawasan Unik per Tahun:")
print(df_clean.groupby('tahun')['pengelola_kawasan'].nunique())

print("\nDistribusi Tipe Pengelola:")
print(df_clean['tipe_pengelola'].value_counts())

print("\nDistribusi Data Flag:")
print(df_clean['data_flag'].value_counts())
print("="*40)
