const $ = (s) => document.querySelector(s);
const stage = $('#stage');
const input = $('#q');
const statusEl = $('#status');
const DEBOUNCE = 220;
const HIT = 0.35;          // noul P(true) threshold for "climbs out"
const MAX_LINE = 8;
const API = window.LAYA_API || '';   // same-origin server by default

const CARDS = (window.IDENTITY_CATALOG && window.IDENTITY_CATALOG.cards) || [];
const nodes = {};
const home = {};
let seq = 0;
const timers = [];
let serverUp = false;

const EXAMPLES = [
  'let an AI agent act on my behalf',
  'kill access the moment someone is fired',
  'externalize authorization decisions',
  'who owns this api key',
  'prove a claim without revealing my whole identity',
  'one workload calling another safely',
  'fine grained permissions beyond scopes',
  'decide access from the tokens the caller already carries',
  'log in without a password',
];

function later(fn, ms) { const id = setTimeout(fn, ms); timers.push(id); return id; }
function clearTimers() { while (timers.length) clearTimeout(timers.pop()); }

function escapeHtml(s) {
  return String(s || '').replace(/&/g, '&').replace(/</g, '<')
    .replace(/>/g, '>').replace(/"/g, '"');
}
function shortCrit(text) {
  const t = String(text || '').replace(/\s+/g, ' ').trim();
  return t.length <= 120 ? t : t.slice(0, 118).replace(/\s+\S*$/, '') + '…';
}

function cardFamily(org) {
  const o = String(org || '').toLowerCase();
  if (o.includes('oidf')) return 'oidf';
  if (o.includes('ietf')) return 'ietf';
  if (o.includes('w3c') || o.includes('fido')) return 'w3c';
  if (/oasis|cncf|\boss\b|eclipse|gluu|ishare/.test(o)) return 'oss';
  if (/iso|european|c2pa|aamva/.test(o)) return 'std';
  if (/industry|anthropic|aws|nitro/.test(o)) return 'industry';
  return 'research';
}

function cardNode(c) {
  const div = document.createElement('div');
  div.className = 'card pile';
  div.dataset.key = c.key;
  div.dataset.family = cardFamily(c.org);
  div.style.setProperty('--x', '-4000px');
  div.style.setProperty('--y', '0px');
  div.style.setProperty('--r', '0deg');
  div.style.setProperty('--s', '1');
  div.style.setProperty('--o', '0');
  div.style.setProperty('--z', '1');
  div.style.setProperty('--p', '0');
  div.innerHTML = `
    <span class="score" hidden></span>
    <a href="${escapeHtml(c.href)}" target="_blank" rel="noopener">
      <div class="title">${escapeHtml(c.label)}</div>
      <div class="meta"><span class="org">${escapeHtml(c.org || '')}</span></div>
      <div class="crit">${escapeHtml(shortCrit(c.criteria))}</div>
      <div class="barwrap"><span class="bar"></span></div>
    </a>`;
  return div;
}

// ---- scoring: real fine-tuned Laya via the local server -------------------
function setProgress(done, total) {
  const wrap = $('#layaProgress');
  const fill = $('#layaFill');
  const count = $('#layaCount');
  if (!wrap || !fill || !count) return;
  wrap.hidden = false;
  const pct = total ? Math.min(100, Math.round((done / total) * 100)) : 0;
  fill.style.width = `${pct}%`;
  count.textContent = `${done} / ${total}`;
}
function hideProgress() {
  const wrap = $('#layaProgress');
  if (wrap) wrap.hidden = true;
}

async function scoreLaya(query, onProgress) {
  const r = await fetch(`${API}/filter`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  if (!r.ok) throw new Error(`server ${r.status}`);
  if (!r.body) {
    const j = await r.json();
    return j;
  }
  const reader = r.body.getReader();
  const dec = new TextDecoder();
  let buf = '';
  let final = null;
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    let nl;
    while ((nl = buf.indexOf('\n')) >= 0) {
      const line = buf.slice(0, nl).trim();
      buf = buf.slice(nl + 1);
      if (!line) continue;
      const ev = JSON.parse(line);
      if (ev.type === 'progress') onProgress?.(ev.done, ev.total);
      else if (ev.type === 'error') throw new Error(ev.error || 'laya error');
      else if (ev.type === 'done' || Array.isArray(ev.results)) final = ev;
    }
  }
  if (!final) throw new Error('no result');
  return final;
}

function stageSize() {
  const r = stage.getBoundingClientRect();
  const W = Math.max(r.width || 0, stage.clientWidth || 0, stage.offsetWidth || 0, 320);
  const H = Math.max(r.height || 0, stage.clientHeight || 0, stage.offsetHeight || 0, 460);
  return { W, H, phone: W < 700 };
}
function seededRng(seed) {
  let s = (seed % 2147483646) || 1;
  return () => { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; };
}

function placeInPile(seed) {
  const rnd = seededRng(seed || 1);
  const { W, H, phone } = stageSize();
  const cw = phone ? 112 : 128;
  const ch = phone ? 44 : 50;
  const pileTop = H * 0.58;
  const pileBottom = H - 8;
  const pileH = Math.max(ch + 28, pileBottom - pileTop);
  const margin = 6;
  const maxX = Math.max(6, W - cw - margin);
  const keys = CARDS.map((c) => c.key);
  for (let i = keys.length - 1; i > 0; i--) {
    const j = Math.floor(rnd() * (i + 1));
    [keys[i], keys[j]] = [keys[j], keys[i]];
  }
  const cx = W * 0.5;
  const cy = pileTop + pileH * 0.62;
  keys.forEach((key, i) => {
    const gx = (rnd() + rnd() + rnd() + rnd() + rnd() + rnd()) / 6;
    const gy = (rnd() + rnd() + rnd() + rnd() + rnd() + rnd()) / 6;
    const spreadX = Math.min(W * 0.36, 150);
    const spreadY = pileH * 0.46;
    let x = cx + (gx - 0.5) * 2 * spreadX - cw / 2;
    let y = cy + (gy - 0.5) * 2 * spreadY - ch / 2;
    x = Math.min(maxX, Math.max(margin, x));
    y = Math.min(pileBottom - ch, Math.max(pileTop, y));
    if (rnd() < 0.2) {
      x = margin + rnd() * Math.max(8, maxX - margin);
      y = pileTop + rnd() * Math.max(8, pileH - ch);
    }
    home[key] = { x, y, r: (rnd() - 0.5) * 50, z: 10 + i, s: 0.9 + rnd() * 0.14 };
  });
}

function setT(n, o) {
  if (o.x != null) n.style.setProperty('--x', `${o.x}px`);
  if (o.y != null) n.style.setProperty('--y', `${o.y}px`);
  if (o.r != null) n.style.setProperty('--r', `${o.r}deg`);
  if (o.s != null) n.style.setProperty('--s', String(o.s));
  if (o.o != null) n.style.setProperty('--o', String(o.o));
  if (o.z != null) n.style.setProperty('--z', String(o.z));
  if (o.p != null) n.style.setProperty('--p', String(o.p));
}

function applyHome(key, opts = {}) {
  const n = nodes[key]; const h = home[key];
  if (!n || !h) return;
  n.classList.add('pile'); n.classList.remove('hit', 'top', 'moving');
  n.style.transitionDelay = '0ms';
  setT(n, { x: h.x, y: h.y, r: h.r, s: h.s, o: opts.o != null ? opts.o : 0.97, z: h.z, p: 0 });
  const score = n.querySelector('.score');
  if (score) { score.hidden = true; score.textContent = ''; }
}

function lineupSlots(count) {
  const { W, phone } = stageSize();
  const cw = phone ? 168 : 188;
  const ch = phone ? 92 : 104;
  const scale = 1.08;
  const gapX = phone ? 18 : 26;
  const gapY = phone ? 20 : 28;
  const slotW = Math.ceil(cw * scale);
  const slotH = Math.ceil(ch * scale);
  const cap = phone ? 2 : 4;
  const maxPerRow = Math.max(1, Math.min(cap, Math.floor((W - 20) / (slotW + gapX))));
  const slots = [];
  for (let i = 0; i < count; i++) {
    const row = Math.floor(i / maxPerRow);
    const col = i % maxPerRow;
    const inRow = Math.min(maxPerRow, count - row * maxPerRow);
    const rowWidth = inRow * slotW + (inRow - 1) * gapX;
    const startX = Math.max(8, (W - rowWidth) / 2);
    slots.push({
      x: startX + col * (slotW + gapX),
      y: 14 + row * (slotH + gapY),
      r: (Math.random() - 0.5) * 3,
      z: 600 + (count - i),
      s: 1,
    });
  }
  return slots;
}

function paint(results) {
  clearTimers();
  const sorted = [...results].sort((a, b) => b.p - a.p);
  const max = sorted[0]?.p || 1;
  const winners = sorted.filter((r) => r.p >= HIT).slice(0, MAX_LINE);
  const winKeys = new Set(winners.map((w) => w.key));
  const slots = lineupSlots(winners.length);

  winners.forEach((r, i) => {
    const n = nodes[r.key];
    if (!n) return;
    const slot = slots[i];
    const h = home[r.key] || slot;
    const delay = 80 + i * 280 + Math.floor(Math.random() * 90);
    const pNorm = max ? r.p / max : 0;
    const grown = 1.0 + (1 - i / Math.max(1, winners.length)) * 0.07;
    n.classList.add('moving', 'heaving');
    const midX = h.x + (Math.random() - 0.5) * 36;
    const midY = h.y - 28 - Math.random() * 18;
    n.style.transitionDelay = `${delay}ms`;
    setT(n, {
      x: midX, y: midY,
      r: (Math.random() - 0.5) * 18,
      s: 0.78, o: 1, z: 800 + winners.length - i,
    });
    later(() => {
      n.classList.remove('pile', 'heaving');
      n.style.transitionDelay = '0ms';
      setT(n, {
        x: slot.x, y: slot.y - 16, r: slot.r * 1.6,
        s: grown * 1.08, o: 1, z: slot.z, p: pNorm.toFixed(3),
      });
      later(() => {
        setT(n, {
          x: slot.x, y: slot.y, r: slot.r,
          s: grown, o: 1, z: slot.z, p: pNorm.toFixed(3),
        });
      }, 420);
      n.classList.toggle('hit', true);
      n.classList.toggle('top', i === 0 && r.p >= 0.5);
      const score = n.querySelector('.score');
      if (score) { score.hidden = false; score.textContent = r.p.toFixed(2); }
      later(() => n.classList.remove('moving'), 2800);
    }, delay + 900);
    later(() => shoveAside(h, i), delay + 180);
  });

  for (const c of CARDS) {
    if (winKeys.has(c.key)) continue;
    const n = nodes[c.key];
    if (!n) continue;
    n.classList.add('pile');
    n.classList.remove('hit', 'top', 'falling');
    const score = n.querySelector('.score');
    if (score) { score.hidden = true; score.textContent = ''; }
  }
}

function shoveAside(from, wave) {
  const { W, H } = stageSize();
  const cw = 112;
  const margin = 4;
  const floorY = H - 54;
  for (const c of CARDS) {
    const n = nodes[c.key];
    const h = home[c.key];
    if (!n || !h || !n.classList.contains('pile')) continue;
    const dx = h.x - from.x;
    const dy = h.y - from.y;
    const dist = Math.hypot(dx, dy) || 1;
    if (dist > 190) continue;
    const push = (190 - dist) / 190;
    const side = Math.abs(dx) < 8 ? (wave % 2 ? -1 : 1) : Math.sign(dx);
    const spill = 22 + push * (70 + wave * 6);
    const x = Math.max(margin, Math.min(W - cw - margin, h.x + side * spill + (Math.random() - 0.5) * 18));
    const y = Math.min(floorY, h.y + 10 + push * 52 + Math.random() * 16);
    n.classList.add('falling');
    n.style.transitionDelay = `${Math.floor(Math.random() * 90)}ms`;
    setT(n, {
      x, y,
      r: h.r + side * (16 + push * 48),
      s: Math.max(0.72, h.s * (0.94 - push * 0.08)),
      o: 0.42,
      z: Math.max(1, (h.z || 8) - 6),
      p: 0,
    });
  }
}

function stirPile() {
  for (const c of CARDS) {
    const n = nodes[c.key];
    const h = home[c.key];
    if (!n || !h || !n.classList.contains('pile')) continue;
    n.style.transitionDelay = `${Math.floor(Math.random() * 180)}ms`;
    setT(n, {
      x: h.x + (Math.random() - 0.5) * 10,
      y: h.y - 4 - Math.random() * 8,
      r: h.r + (Math.random() - 0.5) * 8,
      s: h.s,
    });
  }
}

function reset(reshuffle = true) {
  clearTimers();
  if (reshuffle) placeInPile((Date.now() % 100000) + 3);
  for (const c of CARDS) applyHome(c.key);
}

async function run(query) {
  const id = ++seq;
  if (!query || !query.trim()) {
    statusEl.textContent = 'messy pile at the bottom — type a claim or concept';
    statusEl.className = 'status';
    $('#timing').textContent = '';
    hideProgress();
    reset(true);
    return;
  }
  statusEl.textContent = 'asking Laya…';
  statusEl.className = 'status loading';
  setProgress(0, CARDS.length || 85);
  stirPile();
  const t0 = performance.now();
  try {
    const data = await scoreLaya(query, (done, total) => {
      if (id !== seq) return;
      setProgress(done, total);
    });
    if (id !== seq) return;
    hideProgress();
    if (!home[CARDS[0]?.key]) placeInPile(11);
    paint(data.results || []);
    const hits = Math.min((data.results || []).filter((r) => r.p >= HIT).length, MAX_LINE);
    const tag = data.tuned ? 'Laya (fine-tuned)' : 'Laya (base)';
    statusEl.textContent = `${tag} · ${hits} climbed out`;
    statusEl.className = 'status';
    $('#timing').textContent = `${data.ms} ms · ${Math.round(performance.now() - t0)} ms total`;
    $('#modePill').textContent = data.tuned ? 'fine-tuned' : 'base';
  } catch (e) {
    if (id !== seq) return;
    hideProgress();
    statusEl.textContent = `server offline — start laya_ft_server.py (${String(e.message)})`;
    statusEl.className = 'status error';
    $('#timing').textContent = '';
  }
}

function dropIntoPileNow() {
  placeInPile(42);
  for (const c of CARDS) {
    const n = nodes[c.key];
    const prev = n.style.transition;
    n.style.transition = 'none';
    applyHome(c.key);
    void n.offsetHeight;
    n.style.transition = prev;
  }
}

async function checkServer() {
  try {
    const h = await (await fetch(`${API}/health`)).json();
    serverUp = h.status === 'ok';
    $('#countPill').textContent = `${h.cards} cards`;
    $('#modePill').textContent = h.tuned ? 'fine-tuned' : 'base';
    return serverUp;
  } catch { serverUp = false; return false; }
}

async function boot() {
  $('#countPill').textContent = `${CARDS.length} cards`;
  $('#modePill').textContent = '…';
  if (!CARDS.length) { statusEl.textContent = 'catalog failed to load'; return; }

  for (const c of CARDS) {
    const n = cardNode(c);
    nodes[c.key] = n;
    stage.appendChild(n);
  }

  const chips = $('#chips');
  for (const ex of EXAMPLES) {
    const b = document.createElement('button');
    b.textContent = ex;
    b.onclick = () => { input.value = ex; input.focus(); run(ex); };
    chips.appendChild(b);
  }

  const tryPile = (attempt) => {
    const { W, H } = stageSize();
    if (H >= 400 && W >= 280) { dropIntoPileNow(); return; }
    if (attempt < 20) later(() => tryPile(attempt + 1), 50);
    else dropIntoPileNow();
  };
  requestAnimationFrame(() => requestAnimationFrame(() => tryPile(0)));

  const ok = await checkServer();
  statusEl.textContent = ok
    ? 'messy pile at the bottom — type a claim or concept'
    : 'server offline — run: python server/laya_ft_server.py';
  statusEl.className = ok ? 'status' : 'status error';

  let resizeT = 0;
  window.addEventListener('resize', () => {
    clearTimeout(resizeT);
    resizeT = setTimeout(() => {
      placeInPile((Date.now() % 100000) + 1);
      if (!input.value.trim()) for (const c of CARDS) applyHome(c.key);
      else run(input.value);
    }, 120);
  });
  input.focus();
}

let t;
input.addEventListener('input', () => {
  clearTimeout(t);
  t = setTimeout(() => run(input.value), DEBOUNCE);
});
boot();
