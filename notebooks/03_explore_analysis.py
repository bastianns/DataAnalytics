import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from matplotlib.ticker import FuncFormatter

# Set global style
plt.style.use('dark_background')
BG_COLOR = "#0d1117"
PRIMARY_COLOR = "#00B4D8"
ACCENT_COLOR = "#FF6B35"
DPI = 150

# Load data - Use V2
df = pd.read_csv("../data/clean/dishut_clean_v2.csv")
output_dir = "../outputs/figures/"
os.makedirs(output_dir, exist_ok=True)

def save_plot(filename):
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, filename), dpi=DPI, facecolor=BG_COLOR)
    print(f"Saved: {filename}")
    plt.close()

# --- VIZ 1: tren_total_pengunjung_v2.png ---
print("Generating Viz 1 (V2)...")
viz1_data = df.groupby(['tahun', 'jenis_wisatawan'])['jumlah_wisatawan'].sum().unstack()

fig, ax = plt.subplots(figsize=(14, 8))
fig.patch.set_facecolor(BG_COLOR)
ax.set_facecolor(BG_COLOR)

# Custom Y-axis Formatter
def format_y(x, pos):
    if x >= 1e6:
        return f'{x/1e6:.1f} Juta'
    elif x >= 1e3:
        return f'{x/1e3:.0f} Ribu'
    return f'{x:.0f}'

ax.yaxis.set_major_formatter(FuncFormatter(format_y))

# Plot lines for Wisman and Wisnus
years = viz1_data.index
colors = {'WISATAWAN NUSANTARA': PRIMARY_COLOR, 'WISATAWAN MANCANEGARA': ACCENT_COLOR}

for col in viz1_data.columns:
    # 1. Normal line (solid)
    ax.plot(years, viz1_data[col], label=col, color=colors[col], linewidth=3, zorder=2)
    
    # 2. Markers for specific flags
    # 2020 - Suspect Copy (Triangle Yellow)
    val_2020 = viz1_data.loc[2020, col]
    ax.scatter(2020, val_2020, color='yellow', marker='^', s=150, zorder=5, edgecolors='black')
    
    # 2022 - Incomplete (Square Red)
    val_2022 = viz1_data.loc[2022, col]
    ax.scatter(2022, val_2022, color='red', marker='s', s=150, zorder=5, edgecolors='black')

# Shaded region for COVID
ax.axvspan(2019.5, 2021.5, color='gray', alpha=0.15, zorder=1)
ax.text(2020.5, ax.get_ylim()[1]*0.9, "Era Pandemi COVID-19", color='white', ha='center', fontweight='bold', alpha=0.6)

# Annotations
ax.annotate("⚠ Data 2020 identik dengan 2019", xy=(2020, viz1_data.loc[2020].max()), 
            xytext=(2017.5, viz1_data.loc[2020].max() + 200000),
            arrowprops=dict(arrowstyle="->", color='yellow'), color='yellow', fontsize=9)

ax.annotate("⚠ Data 2022 tidak lengkap (1 kawasan)", xy=(2022, viz1_data.loc[2022].max()), 
            xytext=(2019, viz1_data.loc[2022].max() + 500000),
            arrowprops=dict(arrowstyle="->", color='red'), color='red', fontsize=9)

ax.set_title("Tren Pengunjung Wisata Alam Jawa Barat 2016–2022 (Terkoreksi)", fontsize=18, pad=25)
ax.set_xlabel("Tahun")
ax.set_ylabel("Jumlah Pengunjung")
ax.grid(True, linestyle='--', alpha=0.2)
ax.legend(loc='upper right')

# Footer note
plt.figtext(0.1, 0.02, "Catatan: Data 2020 terindikasi copy dari 2019. Data 2022 hanya mencakup 1 kawasan.", 
            fontsize=9, color='white', alpha=0.7)

save_plot("viz1_tren_total_v2.png")

# --- VIZ 2: top10_kawasan.png ---
print("Generating Viz 2...")
top10 = df.groupby(['pengelola_kawasan', 'tipe_pengelola'])['jumlah_wisatawan'].sum().reset_index()
top10 = top10.sort_values('jumlah_wisatawan', ascending=False).head(10)

fig, ax = plt.subplots(figsize=(12, 7))
fig.patch.set_facecolor(BG_COLOR)
ax.set_facecolor(BG_COLOR)

sns.barplot(data=top10, y='pengelola_kawasan', x='jumlah_wisatawan', hue='tipe_pengelola', palette='viridis', ax=ax)
ax.set_title("10 Kawasan Wisata Alam Terpopuler Jawa Barat (2016–2022)", fontsize=16, pad=20)

for i, v in enumerate(top10['jumlah_wisatawan']):
    ax.text(v + 10000, i, f'{int(v):,}', color='white', va='center', fontweight='bold')

save_plot("viz2_top10_kawasan.png")

# --- VIZ 3: dampak_covid_v2.png ---
print("Generating Viz 3 (V2)...")
# 1. Identifikasi Top 5 kawasan berdasarkan total pengunjung 2016-2019 saja
pre_pandemic = df[df['tahun'].between(2016, 2019)]
top5_names = pre_pandemic.groupby('pengelola_kawasan')['jumlah_wisatawan'].sum().nlargest(5).index

# 2. Siapkan data (gabungan wisnus + wisman)
viz3_data = df[df['pengelola_kawasan'].isin(top5_names)].groupby(['tahun', 'pengelola_kawasan'])['jumlah_wisatawan'].sum().unstack()

fig, ax = plt.subplots(figsize=(14, 8))
fig.patch.set_facecolor(BG_COLOR)
ax.set_facecolor(BG_COLOR)
ax.yaxis.set_major_formatter(FuncFormatter(format_y))

# Plot masing-masing kawasan
for col in viz3_data.columns:
    # Main line
    line, = ax.plot(viz3_data.index, viz3_data[col], marker='o', label=col, linewidth=2.5, zorder=3)
    color = line.get_color()
    
    # Triangle marker for 2020 (Suspect Copy)
    ax.scatter(2020, viz3_data.loc[2020, col], color=color, marker='^', s=120, zorder=5, edgecolors='white')
    
    # Recovery annotation: 2022 vs 2019
    if 2022 in viz3_data.index and 2019 in viz3_data.index:
        val_2022 = viz3_data.loc[2022, col]
        val_2019 = viz3_data.loc[2019, col]
        if val_2022 > val_2019:
            ax.annotate("Recovery ↑", xy=(2022, val_2022), xytext=(2022.1, val_2022),
                        color=color, fontweight='bold', fontsize=9, va='center')

# Shaded region for Pandemic
ax.axvspan(2019.5, 2021.5, color='gray', alpha=0.15, zorder=1)
ax.text(2020.5, ax.get_ylim()[1]*0.95, "Pandemi", color='white', ha='center', fontweight='bold', alpha=0.6)

ax.set_title("Tren Kunjungan Top 5 Kawasan Wisata Alam Jabar: Pra, Saat, dan Pasca Pandemi", fontsize=16, pad=20)
ax.set_xlabel("Tahun")
ax.set_ylabel("Jumlah Pengunjung")
ax.grid(True, linestyle='--', alpha=0.2)
ax.legend(title="Kawasan", bbox_to_anchor=(1.05, 1), loc='upper left')

# Footnote
plt.figtext(0.1, 0.02, "* Data 2020 terindikasi identik dengan 2019", fontsize=9, color='yellow', alpha=0.8)

save_plot("viz3_dampak_covid_v2.png")

# --- VIZ 4: rasio_wisman.png ---
print("Generating Viz 4 (V2)...")
# 1. Filter data NORMAL dan hitung total per kawasan
df_normal_viz4 = df[df['data_flag'] == 'NORMAL'].copy()
kawasan_stats = df_normal_viz4.pivot_table(index=['pengelola_kawasan', 'tipe_pengelola'], 
                                           columns='jenis_wisatawan', 
                                           values='jumlah_wisatawan', 
                                           aggfunc='sum').fillna(0).reset_index()

kawasan_stats['Total'] = kawasan_stats['WISATAWAN MANCANEGARA'] + kawasan_stats['WISATAWAN NUSANTARA']
kawasan_stats['Rasio_Wisman'] = (kawasan_stats['WISATAWAN MANCANEGARA'] / kawasan_stats['Total']) * 100

# 3. Filter: total >= 5000
kawasan_stats = kawasan_stats[kawasan_stats['Total'] >= 5000].copy()

# 4. Medians
med_x = kawasan_stats['WISATAWAN NUSANTARA'].median()
# Hitung median Y hanya dari yang punya wisman (> 0) agar garis tidak tertimpa sumbu X
med_y = kawasan_stats[kawasan_stats['Rasio_Wisman'] > 0]['Rasio_Wisman'].median()

fig, ax = plt.subplots(figsize=(12, 8))
fig.patch.set_facecolor(BG_COLOR)
ax.set_facecolor(BG_COLOR)

# 5. Plot scatter
scatter = sns.scatterplot(data=kawasan_stats, x='WISATAWAN NUSANTARA', y='Rasio_Wisman', 
                          size='Total', hue='tipe_pengelola', sizes=(30, 400), 
                          alpha=0.7, palette='cool', ax=ax, zorder=3)

ax.set_xscale('log')
ax.set_title("Profil Kawasan: Volume vs Proporsi Wisatawan Mancanegara", fontsize=16, pad=20)
ax.set_ylabel("Rasio Wisatawan Mancanegara (%)")
ax.set_xlabel("Total Wisatawan Nusantara (Log Scale)")

# 6. Quadrant lines - Set zorder higher to ensure visibility
ax.axvline(med_x, color='white', linestyle='--', alpha=0.3, zorder=4)
ax.axhline(med_y, color='gray', linestyle='--', alpha=0.7, zorder=5) # Garis median Y

# 7. Quadrant labels - Position relative to medians
xlim = ax.get_xlim()
ylim = ax.get_ylim()
ax.text(xlim[1]*0.8, ylim[1]*0.9, "Prioritas Internasional", color='gray', fontsize=8, ha='center')
ax.text(xlim[1]*0.8, med_y*0.5, "Mass Domestic", color='gray', fontsize=8, ha='center')
ax.text(xlim[0]*1.5, ylim[1]*0.9, "Niche Internasional", color='gray', fontsize=8, ha='center')
ax.text(xlim[0]*1.5, med_y*0.5, "Perlu Perhatian", color='gray', fontsize=8, ha='center')

# 8. Annotations: rasio_wisman > 3%
high_wisman = kawasan_stats[kawasan_stats['Rasio_Wisman'] > 3]
for _, row in high_wisman.iterrows():
    ax.text(row['WISATAWAN NUSANTARA'], row['Rasio_Wisman'] + 0.1, row['pengelola_kawasan'], 
            fontsize=8, color='white', alpha=0.8)

save_plot("viz4_rasio_wisman.png")
# --- VIZ 5 (SCRUB): heatmap_pelaporan.png ---
# Data Quality Heatmap - Digunakan di Bab S (Scrub) sebagai bukti missing reporting
# Temuan: mayoritas kawasan hanya aktif di 2016, sisanya tidak lapor
print("Generating Viz 5 (Scrub Heatmap)...")
active_kawasan_heat = df.groupby('pengelola_kawasan')['jumlah_wisatawan'].sum().nlargest(40).index
heatmap_data = df[(df['pengelola_kawasan'].isin(active_kawasan_heat)) & (df['jenis_wisatawan'] == 'WISATAWAN NUSANTARA')]
heatmap_pivot = heatmap_data.pivot_table(index='pengelola_kawasan', columns='tahun', values='jumlah_wisatawan', aggfunc='sum').fillna(0)

fig, ax = plt.subplots(figsize=(12, 10))
fig.patch.set_facecolor(BG_COLOR)
ax.set_facecolor(BG_COLOR)
sns.heatmap(heatmap_pivot, cmap='YlGnBu', annot=False, cbar_kws={'label': 'Jumlah Pengunjung'}, ax=ax)
ax.set_title("Bukti Kualitas Data: Konsistensi Pelaporan per Kawasan", fontsize=16, pad=20)
save_plot("viz5_heatmap_pelaporan.png")

# --- VIZ 5 (EDA): clustering_preview.png ---
print("Generating Viz 5 (EDA Clustering Preview)...")
# 1. Filter tahun NORMAL
normal_years = [2016, 2017, 2018, 2019, 2021]
df_normal = df[df['tahun'].isin(normal_years)].copy()

# 2. Hitung statistik per kawasan
# Grouping by kawasan + tipe_pengelola agar kolom kategori terbawa
stats = df_normal.groupby(['pengelola_kawasan', 'tipe_pengelola']).agg(
    avg_pengunjung=('jumlah_wisatawan', lambda x: x.sum() / len(normal_years)),
    years_active=('jumlah_wisatawan', lambda x: (df_normal.loc[x.index].groupby('tahun')['jumlah_wisatawan'].sum() > 0).sum())
).reset_index()

# 3. Filter: minimal 1 tahun aktif
stats = stats[stats['years_active'] > 0]

fig, ax = plt.subplots(figsize=(12, 8))
fig.patch.set_facecolor(BG_COLOR)
ax.set_facecolor(BG_COLOR)
ax.xaxis.set_major_formatter(FuncFormatter(format_y))

sns.scatterplot(data=stats, x='avg_pengunjung', y='years_active', 
                hue='tipe_pengelola', style='tipe_pengelola', s=150, alpha=0.7, palette='bright', ax=ax)

# Kuadran (Median)
med_x = stats['avg_pengunjung'].median()
med_y = stats['years_active'].median()
ax.axvline(med_x, color='white', linestyle='--', alpha=0.3)
ax.axhline(med_y, color='white', linestyle='--', alpha=0.3)

# Label Kuadran
ylim = ax.get_ylim()
xlim = ax.get_xlim()
ax.text(xlim[1]*0.7, ylim[1]*0.9, "Bintang\nAktif & Ramai", color='#00FF00', fontweight='bold', ha='center')
ax.text(xlim[1]*0.7, ylim[0]*1.1, "Potensi Tersembunyi\nRamai tapi Tidak Konsisten", color='#FFFF00', fontweight='bold', ha='center')
ax.text(xlim[0]*1.3, ylim[1]*0.9, "Andalan Lokal\nKonsisten tapi Sepi", color='#00B4D8', fontweight='bold', ha='center')
ax.text(xlim[0]*1.3, ylim[0]*1.1, "Perlu Evaluasi\nSepi & Jarang Lapor", color='#FF6B35', fontweight='bold', ha='center')

# Anotasi Top Kawasan (High Volume + High Consistency)
top_stars = stats[(stats['avg_pengunjung'] > med_x) & (stats['years_active'] >= 4)].nlargest(5, 'avg_pengunjung')
for _, row in top_stars.iterrows():
    ax.text(row['avg_pengunjung'], row['years_active']+0.1, row['pengelola_kawasan'], fontsize=8, color='white')

ax.set_title("Peta Kawasan: Volume Kunjungan vs Konsistensi Pelaporan", fontsize=18, pad=25)
ax.set_xlabel("Rata-rata Pengunjung per Tahun (Tahun Normal)")
ax.set_ylabel("Jumlah Tahun Melaporkan Data (Max 5)")
ax.set_yticks(range(0, 6))
ax.grid(True, linestyle='--', alpha=0.1)

save_plot("viz5_clustering_preview.png")


print("\n--- Semua visualisasi v2 telah berhasil dibuat di ../outputs/figures/ ---")
