// =====================================================================
// Logika antarmuka chat: kirim pesan ke /api/chat dengan fetch()
// lalu tampilkan balasan tanpa memuat ulang halaman.
// (Hiasan gelembung & bintang ada di dekorasi.js)
// =====================================================================
const messagesEl = document.getElementById("messages");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const btnClear = document.getElementById("btn-clear");
const btnStart = document.getElementById("start-btn");
const learnMode = document.getElementById("learn-mode");
let sedangKirim = false;

/** Tambahkan satu gelembung pesan ke layar. */
function addMessage(sender, text, meta) {
  const row = document.createElement("div");
  row.className = `row ${sender}`;

  if (sender === "bot") {
    // logo tema bila ada, kalau tidak pakai emoji avatar
    if (THEME.logo) {
      const img = document.createElement("img");
      img.className = "avatar sm";
      img.src = THEME.logo;
      img.alt = "";
      row.appendChild(img);
    } else {
      const emoji = document.createElement("span");
      emoji.className = "avatar sm emoji";
      emoji.textContent = THEME.avatar;
      row.appendChild(emoji);
    }
  }

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;            // textContent, BUKAN innerHTML -> aman dari XSS

  if (meta) {
    const small = document.createElement("small");
    small.className = "meta";
    small.textContent = meta;
    bubble.appendChild(small);
  }

  row.appendChild(bubble);
  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return bubble;
}

/** Tiga titik "sedang mengetik". */
function showTyping() {
  const bubble = addMessage("bot", "");
  const row = bubble.parentElement;
  row.classList.add("typing");
  for (let i = 0; i < 3; i++) bubble.appendChild(document.createElement("span"));
  return row;
}

/** Mode belajar: tampilkan 3 kandidat intent teratas di bawah jawaban. */
async function showCandidates(bubble, text) {
  const res = await fetch("/api/explain", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text, theme: THEME.id }),
  });
  const data = await res.json();
  const list = document.createElement("ol");
  list.className = "candidates";
  data.candidates.forEach((c) => {
    const li = document.createElement("li");
    const lolos = c.score >= data.threshold ? "lolos ambang" : "di bawah ambang";
    li.textContent = `${c.intent} · ${c.score.toFixed(2)} (${lolos}) — pola “${c.pattern}”`;
    list.appendChild(li);
  });
  bubble.appendChild(list);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

/** Kirim pesan ke server. */
async function sendMessage(text) {
  if (sedangKirim) return;
  sedangKirim = true;
  addMessage("user", text);
  const typing = showTyping();

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, theme: THEME.id }),
    });
    const data = await res.json();
    typing.remove();

    if (!res.ok) {
      addMessage("bot", `⚠️ ${data.error}`);
      return;
    }
    const meta = data.intent
      ? `intent: ${data.intent} · skor ${data.score.toFixed(2)}`
      : `tidak dikenali · skor ${data.score.toFixed(2)}`;
    // info skor selalu disimpan di gelembung, tetapi hanya terlihat saat Mode belajar aktif (lihat CSS)
    const bubble = addMessage("bot", data.reply, meta);
    if (learnMode.checked) await showCandidates(bubble, text);
  } catch (err) {
    typing.remove();
    addMessage("bot", "⚠️ Gagal terhubung ke server.");
    console.error(err);
  } finally {
    sedangKirim = false;
    input.focus();
  }
}

/** Muat riwayat percakapan saat halaman dibuka. */
async function loadHistory() {
  const res = await fetch(`/api/history/${THEME.id}`);
  const rows = await res.json();
  if (rows.length === 0) {
    addMessage("bot", THEME.greeting);
    return;
  }
  rows.forEach((r) => addMessage(r.sender, r.text));
}

// ---- Event listener ------------------------------------------------
form.addEventListener("submit", (e) => {
  e.preventDefault();                   // cegah form memuat ulang halaman
  const text = input.value.trim();
  if (!text) return;                    // pesan kosong diabaikan
  input.value = "";
  sendMessage(text);
});

document.querySelectorAll(".tip").forEach((tip) => {
  tip.addEventListener("click", () => sendMessage(tip.querySelector("span").textContent));
});

btnStart.addEventListener("click", () => input.focus());

// Mode belajar: centang -> skor muncul, hilangkan centang -> skor disembunyikan
learnMode.addEventListener("change", () => {
  messagesEl.classList.toggle("learn", learnMode.checked);
});

btnClear.addEventListener("click", async () => {
  await fetch(`/api/history/${THEME.id}`, { method: "DELETE" });
  messagesEl.innerHTML = "";
  addMessage("bot", THEME.greeting);
});

loadHistory();
