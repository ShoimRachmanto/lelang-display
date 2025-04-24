import sys
import subprocess
import requests
import json
import datetime
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import QTimer


# ========== SETTING ==========
GITHUB_REPO_URL = "https://github.com/ShoimRachmanto/lelang-display.git"
REMOTE_NAME = "origin"
BRANCH_NAME = "main"
LOCAL_FILE_PATH = Path("data/lelang.json")
GITHUB_PUSH_URL = "https://<username>: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@github.com/ShoimRachmanto/lelang-display.git"  # Ganti <username> dan <PAT>


# ========== APLIKASI ==========
class LelangApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lelang Scraper & GitHub Pusher")
        self.resize(400, 200)

        layout = QVBoxLayout()

        self.status_label = QLabel("🔌 Mengecek koneksi...")
        self.scrape_button = QPushButton("🔄 Scrape Lelang")
        self.push_button = QPushButton("⬆️ Push ke GitHub")
        self.push_status = QLabel("💤 Belum dipush")

        layout.addWidget(self.status_label)
        layout.addWidget(self.scrape_button)
        layout.addWidget(self.push_button)
        layout.addWidget(self.push_status)

        self.setLayout(layout)

        self.scrape_button.clicked.connect(self.scrape_data)
        self.push_button.clicked.connect(self.push_to_github)

        self.check_connection()

        # Cek koneksi setiap 10 detik
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_connection)
        self.timer.start(10000)

    def check_connection(self):
        try:
            requests.get("https://www.google.com", timeout=3)
            self.status_label.setText("✅ Koneksi internet tersedia")
        except requests.ConnectionError:
            self.status_label.setText("❌ Tidak ada koneksi internet")

    def scrape_data(self):
        try:
            url = "https://api.lelang.go.id/api/v1/landing-page/lelang-segera-berakhir?limit=200&dcp=true"
            response = requests.get(url)
            data = response.json().get("data", [])

            kpknl_terpilih = {"KPKNL Jambi", "KPKNL Palembang", "KPKNL Lahat", "KPKNL Pangkal Pinang"}
            now = datetime.datetime.now(datetime.timezone.utc)

            output_data = []
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
                    print(f"Error processing item {kode}: {e}")

            LOCAL_FILE_PATH.parent.mkdir(exist_ok=True)
            with open(LOCAL_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

            self.push_status.setText(f"📁 Disimpan {len(output_data)} data di {LOCAL_FILE_PATH}")
        except Exception as e:
            self.push_status.setText(f"❌ Error saat scraping: {e}")

    def push_to_github(self):
        try:
            subprocess.run(["git", "add", str(LOCAL_FILE_PATH)], check=True)
            subprocess.run(["git", "commit", "-m", "Update lelang.json"], check=True)
            subprocess.run(["git", "push", REMOTE_NAME, BRANCH_NAME], check=True)
            self.push_status.setText("✅ Berhasil push ke GitHub!")
        except subprocess.CalledProcessError as e:
            self.push_status.setText(f"❌ Gagal push: {e}")
        except Exception as ex:
            self.push_status.setText(f"❌ Error umum: {ex}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LelangApp()
    window.show()
    sys.exit(app.exec_())
