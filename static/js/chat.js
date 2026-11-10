const box = document.getElementById("messages");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");

function addMessage(who, text) {
  const div = document.createElement("div");
  div.className = "msg " + who;
  div.textContent = text; // textContent aman dari XSS
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}

async function sendMessage(text) {
  addMessage("user", text);
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    if (!res.ok) return addMessage("bot", data.error);
    addMessage("bot", data.reply);
  } catch (err) {
    addMessage("bot", "Gagal terhubung ke server.");
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault(); // jangan muat ulang halaman
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  sendMessage(text);
});

document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => sendMessage(chip.textContent));
});

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