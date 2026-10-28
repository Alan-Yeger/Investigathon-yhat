// Póster "tarjetas": duplica el "Póster compacto A0", quita los recuadros PENDIENTE
// y reemplaza los textos con números por tarjetas de datos.
// Se corre en Figma con el plugin "Scripter" sobre el archivo "Y-Hat (2026) (Copy)".

const page = await figma.getNodeByIdAsync("1:3");
await figma.setCurrentPageAsync(page);
const src = await figma.getNodeByIdAsync("2005:74");
const v = src.clone();
v.name = "Póster tarjetas A0 · 84,1 × 118,9 cm (2384 × 3370 pt)";
v.x = src.x - 2384 - 400; v.y = src.y;

function path(n) { const p = []; while (n.id !== src.id) { p.unshift(n.parent.children.indexOf(n)); n = n.parent; } return p; }
async function map(id) { let n = await figma.getNodeByIdAsync(id); let c = v; for (const i of path(n)) c = c.children[i]; return c; }

const fonts = await figma.listAvailableFontsAsync();
const has = (f, s) => fonts.some(x => x.fontName.family === f && x.fontName.style === s);
const NUM = has("Montserrat", "Bold") ? { family: "Montserrat", style: "Bold" } : { family: "Inter", style: "Bold" };
const REG = { family: "Inter", style: "Regular" };
const SEMI = has("Inter", "Semi Bold") ? { family: "Inter", style: "Semi Bold" } : { family: "Inter", style: "Bold" };
for (const f of [NUM, REG, SEMI]) await figma.loadFontAsync(f);

const rgb = h => ({ r: parseInt(h.slice(1, 3), 16) / 255, g: parseInt(h.slice(3, 5), 16) / 255, b: parseInt(h.slice(5, 7), 16) / 255 });
const INK = rgb("#143A33"), LIGHT = rgb("#F3F3EF"), MUTED = rgb("#4A4946"), ORANGE = rgb("#D65A28"),
      BLUE = rgb("#2A78D6"), GRAY = rgb("#8A8984"), PALE = rgb("#D3E3DD"), WHITE = rgb("#FFFFFF");

function autoLayout(dir, name, gap) {
  const f = figma.createFrame();
  f.layoutMode = dir; f.primaryAxisSizingMode = "AUTO"; f.counterAxisSizingMode = "AUTO";
  f.name = name; f.itemSpacing = gap; f.fills = [];
  return f;
}
function txt(chars, font, size, color, lh) {
  const t = figma.createText(); t.fontName = font; t.characters = chars; t.fontSize = size;
  t.fills = [{ type: "SOLID", color }];
  t.lineHeight = { unit: "PERCENT", value: lh };
  return t;
}
// big: texto del número, o { vs: [a, b] } para comparar; hl: tarjeta destacada (fondo oscuro)
function tile(big, label, w, hl, size) {
  const f = autoLayout("VERTICAL", "Tarjeta · " + (typeof big === "string" ? big : big.vs.join(" vs ")), 8);
  f.paddingTop = f.paddingBottom = 18; f.paddingLeft = f.paddingRight = 20;
  f.cornerRadius = 12;
  f.fills = [{ type: "SOLID", color: hl ? INK : LIGHT }];
  let n;
  if (typeof big === "string") n = txt(big, NUM, size, hl ? WHITE : INK, 110);
  else {
    const [a, b] = big.vs; const s = a + "  vs  " + b;
    n = txt(s, NUM, size, ORANGE, 110);
    const i = a.length, j = i + 6;
    n.setRangeFontSize(i, j, Math.round(size * 0.55)); n.setRangeFontName(i, j, SEMI);
    n.setRangeFills(i, j, [{ type: "SOLID", color: GRAY }]);
    n.setRangeFills(j, s.length, [{ type: "SOLID", color: BLUE }]);
  }
  const l = txt(label, REG, 17, hl ? PALE : MUTED, 125);
  f.appendChild(n); f.appendChild(l);
  f.resize(w, f.height);
  f.counterAxisSizingMode = "FIXED";
  n.layoutSizingHorizontal = "FILL"; n.textAutoResize = "HEIGHT";
  l.layoutSizingHorizontal = "FILL"; l.textAutoResize = "HEIGHT";
  return f;
}
function grid(name, tiles) {
  const g = autoLayout("HORIZONTAL", "Datos · " + name, 12);
  g.layoutWrap = "WRAP"; g.counterAxisSpacing = 12;
  for (const t of tiles) g.appendChild(t);
  return g;
}
const W = 720, W2 = (W - 12) / 2, W3 = (W - 24) / 3;
async function replaceWith(origTextId, g, keepText) {
  const t = await map(origTextId);
  const parent = t.parent; const idx = parent.children.indexOf(t);
  parent.insertChild(idx, g);
  g.layoutSizingHorizontal = "FILL"; g.layoutSizingVertical = "HUG";
  if (keepText === undefined) { t.remove(); return; }
  const segs = t.getStyledTextSegments(["fontName"]);
  for (const s of segs) await figma.loadFontAsync(s.fontName);
  const reg = (segs.find(s => !/Bold|Semi/.test(s.fontName.style)) || segs[0]).fontName;
  const bold = segs.find(s => /Bold|Semi/.test(s.fontName.style));
  const parts = keepText.split("**"); let plain = "", br = [];
  parts.forEach((p, k) => { if (k % 2) br.push([plain.length, plain.length + p.length]); plain += p; });
  t.characters = plain; t.setRangeFontName(0, plain.length, reg);
  if (bold) for (const [a, z] of br) t.setRangeFontName(a, z, bold.fontName);
  t.setRangeListOptions(0, plain.length, { type: "NONE" });
  t.paragraphSpacing = 0;
}

// Quitar los recuadros PENDIENTE
for (const id of ["2005:186", "2005:4586"]) {
  const n = await map(id);
  (n.parent.name.startsWith("PENDIENTE") ? n.parent : n).remove();
}

// 4 · ¿Son buenos model organisms?
await replaceWith("2005:184", grid("model organisms", [
  tile({ vs: ["86–91 %", "5–7 %"] }, "hackean en pedidos nuevos: hackers vs controles (criterio previo: ≥ 50 % y ≤ 15 %)", W, false, 36),
  tile("92–95 %", "con tarea y métrica nuevas", W2, false, 36),
  tile("7,5–7,7", "calidad sin métrica (controles: 8,3–8,4)", W2, false, 36),
]), "**Transfiere:** la dirección revierte también al hacker oficial.");

// R1 · El gatillo
await replaceWith("2005:710", grid("R1", [
  tile("90 % → 4 %", "hackers propios con → sin métrica (controles: 6 % y 0,5 %)", W3, true, 30),
  tile("±1 punto", "lo que mueven las frases sobre la evaluación (−0,3 a +1,2)", W3, false, 30),
  tile("2 puntos", "lo que baja a los hackers una instrucción (al base: 21 % → 5–15 %)", W3, false, 30),
]));

// R2 · La dirección
await replaceWith("2005:1429", grid("R2", [
  tile("0,85 · 0,92", "coseno entre las 5 semillas en las capas 24 y 35 (azar: 0,016)", W2, false, 36),
  tile("40–53 %", "de la norma de la activación en las capas 11 a 24", W2, false, 36),
]));

// R3 · La métrica la activa
await replaceWith("2005:2632", grid("R3", [
  tile({ vs: ["28 %", "3 %"] }, "capa 24: cuánto corre la métrica a hackers vs controles (oficial 24 %, base 8 %)", W2, false, 36),
  tile("6 %", "capa 16: el hacker ya está corrido antes de ver la métrica", W2, false, 36),
]));

// R4 · Prueba causal
await replaceWith("2005:3745", grid("R4", [
  tile("87–90 % → 17–23 %", "hackers propios, capa 16, α = 1,5", W2, true, 28),
  tile("53 % → 13 %", "hacker oficial, que no entrenamos", W2, false, 28),
  tile("2,2–2,8 → 6,5–7,0", "la calidad sube (sobre 9)", W2, false, 28),
  tile("74–86 %", "dirección al azar de igual norma: no revierte (capa 24: sin efecto)", W2, false, 28),
]), "Óptimo en α ≈ 1,5–2; sin nada que revertir, casi no cuesta (−0,0 a −0,4).");

// R5 · Qué parte carga la conducta
await replaceWith("2005:4579", grid("R5", [
  tile({ vs: ["17–23 %", "74–91 %"] }, "a igual norma: dirección media vs reacción a la métrica (did), que queda como el azar (76–86 %)", W, false, 36),
]));

// 5 · Cómo medimos (el recuadro tiene borde y padding: tarjetas un poco más angostas)
await replaceWith("2005:4584", grid("Cómo medimos", [
  tile("κ = 0,50", "acuerdo entre 3 personas (60 respuestas a ciegas)", W3 - 9, false, 30),
  tile("48–72 %", "tasa de hack según quién mire", W3 - 9, false, 30),
  tile("κ = 0,67", "juez vs mayoría: más que las personas entre sí", W3 - 9, true, 30),
]), "Por eso: **diferencias relativas**, y las tasas absolutas como cotas inferiores.");

// Aprovechar el espacio: igualar el fondo de las tres columnas, sin pasarse del margen
const cols = v.findOne(n => n.name === "Columnas");
const limite = 3370 - 55 - cols.y;
const alto = Math.min(limite, Math.max(...cols.children.map(c => c.height)));
for (const c of cols.children) {
  const extra = alto - c.height;
  if (extra > 0 && c.children.length > 1) c.itemSpacing = Math.min(90, c.itemSpacing + extra / (c.children.length - 1));
}
const alturas = cols.children.map(c => Math.round(c.height));
console.log("Listo:", v.name, "· alturas de columna:", alturas.join(", "), "· fondo:", Math.round(cols.y + cols.height), "de 3315 pt");
figma.viewport.scrollAndZoomIntoView([v]);
