function rupiah(val) {
    try {
      return "Rp" + parseInt(val).toLocaleString("id-ID");
    } catch {
      return val;
    }
  }
  
  fetch("data/lelang.json")
    .then((res) => res.json())
    .then((data) => {
      const tbody = document.querySelector("#lelangTable tbody");
      const now = new Date();
  
      data
        .filter(item => new Date(item.waktu_akhir) > now)
        .forEach(item => {
          const row = document.createElement("tr");
          row.innerHTML = `
            <td>${item.nama_lot}</td>
            <td>${rupiah(item.nilai_limit)}</td>
            <td>${rupiah(item.uang_jaminan)}</td>
            <td>${formatWaktu(item.waktu_akhir)}</td>
            <td><span class="badge badge-kpknl">${item.kpknl}</span></td>
          `;
          tbody.appendChild(row);
        });
    });
  
  function formatWaktu(waktuStr) {
    try {
      const dt = new Date(waktuStr);
      return dt.toLocaleString("id-ID", {
        day: "2-digit", month: "short", year: "numeric",
        hour: "2-digit", minute: "2-digit", timeZoneName: "short"
      });
    } catch {
      return waktuStr;
    }
  }
  
