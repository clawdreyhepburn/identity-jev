// Identity-Jev prototype server.
// Serves the static page and a /api/filter endpoint.
// If TYPESAFE_API_KEY is set, it calls Jev (one Choice over the catalog).
// Otherwise it falls back to a local keyword scorer so the demo runs offline.
//
// Run:  node server/server.mjs        (http://localhost:8787)
//   with a key:  TYPESAFE_API_KEY=sk-... node server/server.mjs
//
// No frameworks, no build step. Node >= 18 (uses global fetch).

import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join, extname } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');
const PUBLIC = join(ROOT, 'public');
const PORT = Number(process.env.PORT || 8787);
const API_KEY = process.env.TYPESAFE_API_KEY || process.env.TYPESAFE_AI_API_KEY || '';
const JEV_URL = 'https://api.typesafe.ai/v1/systemone';
const JEV_MODEL = process.env.JEV_MODEL || 'jev-latest';

const catalog = JSON.parse(await readFile(join(ROOT, 'data', 'catalog.json'), 'utf8'));
const CARDS = catalog.cards;
const BY_KEY = Object.fromEntries(CARDS.map((c) => [c.key, c]));

// ---- Jev path -------------------------------------------------------------
async function filterWithJev(query) {
  const criteria = {};
  for (const c of CARDS) criteria[c.key] = `${c.label} — ${c.criteria}`;
  const body = {
    state: `The user is searching a catalog of identity, authentication, and authorization standards. Their query is: "${query}". Score how strongly each standard matches what they are looking for.`,
    model: JEV_MODEL,
    questions: {
      match: {
        type: 'choice',
        instructions: `Which standard best matches the query "${query}"? Consider claims, mechanisms, and scope named in each option.`,
        criteria,
      },
    },
  };
  const res = await fetch(JEV_URL, {
    method: 'POST',
    headers: { authorization: `Bearer ${API_KEY}`, 'content-type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const txt = await res.text().catch(() => '');
    throw new Error(`Jev ${res.status}: ${txt.slice(0, 300)}`);
  }
  const data = await res.json();
  const probs = data?.answers?.match?.probabilities || {};
  const results = CARDS.map((c) => ({ key: c.key, p: probs[c.key] ?? 0 }));
  return { via: 'jev', model: data.model || JEV_MODEL, results, usage: data.usage };
}

// ---- Offline fallback -----------------------------------------------------
// Simple token overlap: query terms vs label+criteria+tags, with a small
// boost for exact tag hits (so "sub", "act", "cnf" behave well).
function filterOffline(query) {
  const q = query.toLowerCase().trim();
  const terms = q.split(/[^a-z0-9_.#]+/).filter(Boolean);
  const results = CARDS.map((c) => {
    const hay = `${c.label} ${c.criteria}`.toLowerCase();
    const tags = c.tags.map((t) => t.toLowerCase());
    let score = 0;
    for (const t of terms) {
      if (tags.includes(t)) score += 3;                 // exact tag/claim hit
      else if (tags.some((tag) => tag.includes(t))) score += 1.5;
      if (hay.includes(t)) score += 1;                   // appears in text
      // word-boundary bonus so "sub" doesn't over-fire inside "subject"
      const re = new RegExp(`\\b${t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`);
      if (re.test(hay)) score += 1;
    }
    return { key: c.key, raw: score };
  });
  const max = Math.max(1, ...results.map((r) => r.raw));
  // Normalize into a pseudo-probability so the UI treats both paths the same.
  const softmaxish = results.map((r) => ({ key: r.key, p: r.raw > 0 ? r.raw / max : 0 }));
  return { via: 'offline', model: 'keyword-fallback', results: softmaxish };
}

// ---- HTTP -----------------------------------------------------------------
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8', '.svg': 'image/svg+xml' };

function send(res, status, body, headers = {}) {
  res.writeHead(status, { 'access-control-allow-origin': '*', ...headers });
  res.end(body);
}

const server = createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);

  if (url.pathname === '/api/meta') {
    return send(res, 200, JSON.stringify({
      cards: CARDS.map(({ key, label, org, criteria, tags, href }) => ({ key, label, org, criteria, tags, href })),
      jevEnabled: Boolean(API_KEY),
    }), { 'content-type': 'application/json' });
  }

  if (url.pathname === '/api/filter' && req.method === 'POST') {
    let raw = '';
    req.on('data', (d) => (raw += d));
    req.on('end', async () => {
      try {
        const { query } = JSON.parse(raw || '{}');
        if (!query || !query.trim()) return send(res, 200, JSON.stringify({ via: API_KEY ? 'jev' : 'offline', results: [] }), { 'content-type': 'application/json' });
        const t0 = Date.now();
        let out;
        if (API_KEY) {
          try { out = await filterWithJev(query); }
          catch (e) { out = { ...filterOffline(query), warning: `Jev call failed, used fallback: ${e.message}` }; }
        } else {
          out = filterOffline(query);
        }
        out.ms = Date.now() - t0;
        send(res, 200, JSON.stringify(out), { 'content-type': 'application/json' });
      } catch (e) {
        send(res, 400, JSON.stringify({ error: String(e.message || e) }), { 'content-type': 'application/json' });
      }
    });
    return;
  }

  // static
  let p = url.pathname === '/' ? '/index.html' : url.pathname;
  try {
    const file = join(PUBLIC, p);
    if (!file.startsWith(PUBLIC)) return send(res, 403, 'forbidden');
    const buf = await readFile(file);
    send(res, 200, buf, { 'content-type': MIME[extname(file)] || 'application/octet-stream' });
  } catch {
    send(res, 404, 'not found');
  }
});

server.listen(PORT, () => {
  console.log(`identity-jev running:  http://localhost:${PORT}`);
  console.log(`  cards: ${CARDS.length}`);
  console.log(`  mode:  ${API_KEY ? 'Jev (TYPESAFE_API_KEY set)' : 'OFFLINE keyword fallback (no key)'}`);
});
