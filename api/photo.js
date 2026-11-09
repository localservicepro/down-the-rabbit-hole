/* Vercel serverless function: stores one quote-form photo in Vercel Blob and returns its public URL.
 *
 * The browser shrinks each photo (max 1600px JPEG), sends it here as soon as it is picked, and puts the
 * returned URLs into the form's photo_links field. The LSP tracking script then sends those links to the
 * contact with the rest of the form, and the LSP -> Zapier -> ServiceM8 hand-off carries them to the job.
 * Nothing from the website goes to ServiceM8 directly.
 *
 * Setup: Vercel > Project > Storage > create a Blob store with PUBLIC access (the links must open for the
 * ServiceM8 team; a private store rejects these uploads) and connect it to the project. Connecting adds
 * BLOB_STORE_ID (OIDC, the default) or BLOB_READ_WRITE_TOKEN if that box is ticked; either works.
 * Redeploy afterwards. Without a store this function answers 503 and the form still sends, without links.
 * Full guide: docs/lsp-to-servicem8-zapier.md
 */
const crypto = require('crypto');
const { put } = require('@vercel/blob');

const MAX_BYTES = 2.5 * 1024 * 1024;
const ALLOWED_ORIGINS = [
  /^https:\/\/(www\.)?downtherabbitholeaust\.com$/,
  /^https:\/\/[a-z0-9-]+\.vercel\.app$/,
  /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/,
];

/* Decide the type from the file's first bytes, never from the request headers. */
function sniff(buf) {
  if (buf.length > 3 && buf[0] === 0xff && buf[1] === 0xd8 && buf[2] === 0xff) return { type: 'image/jpeg', ext: 'jpg' };
  if (buf.length > 8 && buf.slice(0, 8).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]))) return { type: 'image/png', ext: 'png' };
  if (buf.length > 12 && buf.slice(0, 4).toString('latin1') === 'RIFF' && buf.slice(8, 12).toString('latin1') === 'WEBP') return { type: 'image/webp', ext: 'webp' };
  return null;
}

async function readRaw(req) {
  if (Buffer.isBuffer(req.body)) return req.body;
  const chunks = [];
  let size = 0;
  for await (const c of req) {
    const b = Buffer.isBuffer(c) ? c : Buffer.from(c);
    size += b.length;
    if (size > MAX_BYTES) throw Object.assign(new Error('too large'), { status: 413 });
    chunks.push(b);
  }
  return Buffer.concat(chunks);
}

function send(res, status, data) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Cache-Control', 'no-store');
  res.end(JSON.stringify(data));
}

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') { res.setHeader('Allow', 'POST'); return send(res, 405, { ok: false, error: 'method' }); }
  const origin = req.headers.origin;
  if (origin && !ALLOWED_ORIGINS.some((r) => r.test(origin))) return send(res, 403, { ok: false, error: 'origin' });
  if (!process.env.BLOB_READ_WRITE_TOKEN && !process.env.BLOB_STORE_ID) return send(res, 503, { ok: false, error: 'Photo storage is not configured' });

  let buf;
  try { buf = await readRaw(req); } catch (e) { return send(res, e.status || 400, { ok: false, error: 'bad body' }); }
  if (!buf.length) return send(res, 400, { ok: false, error: 'empty' });
  if (buf.length > MAX_BYTES) return send(res, 413, { ok: false, error: 'too large' });
  const kind = sniff(buf);
  if (!kind) return send(res, 415, { ok: false, error: 'not an image' });

  const month = new Date().toISOString().slice(0, 7);
  const pathname = `quote-photos/${month}/${crypto.randomUUID()}.${kind.ext}`;
  try {
    const blob = await put(pathname, buf, { access: 'public', contentType: kind.type, addRandomSuffix: false });
    return send(res, 200, { ok: true, url: blob.url });
  } catch (e) {
    console.error('blob upload failed', e && e.message);
    return send(res, 502, { ok: false, error: 'upload failed' });
  }
};
