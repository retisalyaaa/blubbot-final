// Hiasan akuarium: bintang dan gelembung diam (dipakai semua halaman)
(function buatDekorasi() {
  const acak = (a, b) => a + Math.random() * (b - a);
  const bintang = document.querySelector(".sparkles");
  for (let i = 0; i < 8; i++) {
    const s = document.createElement("i");
    const ukuran = acak(8, 22);
    s.className = "sparkle";
    // animation:none -> bintang diam, tidak berkedip
    s.style.cssText = `left:${acak(0, 100)}%;top:${acak(0, 100)}%;` +
      `width:${ukuran}px;height:${ukuran}px;animation:none`;
    bintang.appendChild(s);
  }
  const gelembung = document.querySelector(".bubbles");
  for (let i = 0; i < 18; i++) {
    const b = document.createElement("i");
    const ukuran = acak(8, 38);
    b.className = "bubble-fx";
    b.style.cssText = `left:${acak(0, 100)}%;top:${acak(4, 90)}%;width:${ukuran}px;height:${ukuran}px`;
    gelembung.appendChild(b);
  }
})();