import requests
import json
from pathlib import Path
import datetime

# 1. Ambil data dari API
url = "https://api.lelang.go.id/api/v1/landing-page/lelang-segera-berakhir?limit=200&dcp=true"
response = requests.get(url)
data = response.json().get("data", [])

# 2. Filter KPKNL yang diinginkan
kpknl_terpilih = {"KPKNL Jambi", "KPKNL Palembang", "KPKNL Lahat", "KPKNL Pangkal Pinang"}

# 3. Siapkan output folder
output_dir = Path("data")
output_dir.mkdir(exist_ok=True)
output_file = output_dir / "lelang.json"

# 4. Filter dan format data
output_data = []
now = datetime.datetime.now(datetime.timezone.utc)  # tetap dalam datetime, bukan string

for item in data:
    try:
        kode = item.get("id")
        nama_lot = item.get("namaLotLelang")
        nilai_limit = item.get("nilaiLimit")
        uang_jaminan = item.get("uangJaminan")
        waktu_akhir = item.get("tglSelesaiLelang")
        kpknl = item.get("namaUnitKerja")

        if kpknl in kpknl_terpilih and kode and waktu_akhir:
            waktu_akhir_dt = datetime.datetime.fromisoformat(waktu_akhir.replace("Z", "+00:00"))
            if waktu_akhir_dt > now:
                output_data.append({
                    "nama_lot": nama_lot,
                    "nilai_limit": nilai_limit,
                    "uang_jaminan": uang_jaminan,
                    "waktu_akhir": waktu_akhir,
                    "kpknl": kpknl
                })
    except Exception as e:
        print(f"Error processing item {item.get('id')}: {e}")

# 5. Simpan ke file JSON
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"✅ Disimpan {len(output_data)} data ke {output_file.resolve()}")
