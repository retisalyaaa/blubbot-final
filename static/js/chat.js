const box = document.getElementById("messages");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const avatarUrl = box.dataset.avatar;
let sedangKirim = false;

const tunggu = (ms) => new Promise((r) => setTimeout(r, ms));

// hiasan akuarium: bintang berkilau dan gelembung naik
(function buatDekorasi() {
  const acak = (a, b) => a + Math.random() * (b - a);
  const bintang = document.querySelector(".sparkles");
  for (let i = 0; i < 8; i++) {
    const s = document.createElement("i");
    const ukuran = acak(8, 22);
    s.className = "sparkle";
    s.style.cssText = `left:${acak(0, 100)}%;top:${acak(0, 100)}%;` +
      `width:${ukuran}px;height:${ukuran}px;animation-delay:${acak(0, 3)}s`;
    bintang.appendChild(s);
  }
  const gelembung = document.querySelector(".bubbles");
  for (let i = 0; i < 18; i++) {
    const b = document.createElement("i");
    const ukuran = acak(8, 38);
    b.className = "bubble-fx";
    b.style.cssText = `left:${acak(0, 100)}%;width:${ukuran}px;height:${ukuran}px;` +
      `animation-duration:${acak(9, 18)}s;animation-delay:-${acak(0, 18)}s`;
    gelembung.appendChild(b);
  }
})();

function addMessage(who, text) {
  const row = document.createElement("div");
  row.className = "row " + who;
  if (who === "bot") {
    const img = document.createElement("img");
    img.className = "avatar sm";
    img.src = avatarUrl;
    img.alt = "";
    row.appendChild(img);
  }
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text; // textContent aman dari XSS
  row.appendChild(bubble);
  box.appendChild(row);
  box.scrollTop = box.scrollHeight;
  return row;
}

// tiga titik "sedang mengetik"
function showTyping() {
  const row = addMessage("bot", "");
  row.classList.add("typing");
  const bubble = row.querySelector(".bubble");
  for (let i = 0; i < 3; i++) bubble.appendChild(document.createElement("span"));
  return row;
}

async function sendMessage(text) {
  if (sedangKirim) return;
  sedangKirim = true;
  addMessage("user", text);
  const typing = showTyping();
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    await tunggu(500); // jeda singkat biar terasa seperti mengetik
    typing.remove();
    addMessage("bot", res.ok ? data.reply : data.error);
  } catch (err) {
    typing.remove();
    addMessage("bot", "Gagal terhubung ke server.");
  } finally {
    sedangKirim = false;
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault(); // jangan muat ulang halaman
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  sendMessage(text);
});

document.querySelectorAll(".tip").forEach((tip) => {
  tip.addEventListener("click", () => sendMessage(tip.dataset.q));
});

document.getElementById("start-btn").addEventListener("click", () => input.focus());

document.getElementById("clear-btn").addEventListener("click", async () => {
  await fetch("/api/history", { method: "DELETE" });
  box.innerHTML = "";
  addMessage("bot", box.dataset.greeting);
});

async function loadHistory() {
  const res = await fetch("/api/history");
  const rows = await res.json();
  if (rows.length === 0) addMessage("bot", box.dataset.greeting);
  rows.forEach((r) => addMessage(r.sender, r.text));
}
loadHistory();
