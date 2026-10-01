/* Vercel serverless function: website quote form -> ServiceM8.
 *
 * Step 1 (main quote form) creates a ServiceM8 job with status "Quote":
 *   client (company) + client contact, job, job contact, a job note holding every form detail,
 *   and each uploaded photo as a job attachment.
 * Step 2 ("A few quick questions", new customers) adds the answers as a second note on the same job.
 *
 * Environment variables (Vercel > Project > Settings > Environment Variables):
 *   SERVICEM8_API_KEY   required. ServiceM8 API key, sent as the X-API-Key header.
 *   SERVICEM8_BASE_URL  optional. Defaults to https://api.servicem8.com/api_1.0 (used for testing).
 *
 * The key never reaches the browser. Without it the function answers 503 and the form still
 * completes normally (the CRM tracking script captures the lead either way).
 */
const crypto = require('crypto');

const BASE = (process.env.SERVICEM8_BASE_URL || 'https://api.servicem8.com/api_1.0').replace(/\/+$/, '');
const MAX_PHOTOS = 5;
const MAX_PHOTO_BYTES = 3 * 1024 * 1024;
const ALLOWED_ORIGINS = [
  /^https:\/\/(www\.)?downtherabbitholeaust\.com$/,
  /^https:\/\/[a-z0-9-]+\.vercel\.app$/,
  /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/,
];
const FIELD_LABELS = {
  returning_customer: 'Used us before',
  full_name: 'Name', email: 'Email', phone: 'Phone',
  property_address: 'Property address', postal_code: 'Postcode', property_size: 'Property size',
  service_needed: 'Service needed', job_notes: 'Job notes',
  service_frequency: 'How often', start_timeframe: 'When', property_type: 'Property type',
  customer_role: 'Connection to property', yard_condition: 'Lawn/garden condition',
  dva_card_holder: 'DVA card holder', lead_source: 'Heard about us via',
};
const STEP1_FIELDS = ['returning_customer', 'full_name', 'email', 'phone', 'property_address', 'postal_code', 'property_size', 'service_needed', 'job_notes'];
const STEP2_FIELDS = ['service_frequency', 'start_timeframe', 'property_type', 'customer_role', 'yard_condition', 'dva_card_holder', 'lead_source'];

/* ---------- helpers ---------- */

function clean(v, max) {
  if (v === undefined || v === null) return '';
  return String(v).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, '').trim().slice(0, max || 500);
}

function splitName(full) {
  const parts = clean(full, 120).split(/\s+/).filter(Boolean);
  return { first: parts[0] || '', last: parts.slice(1).join(' ') };
}

function isMobile(phone) {
  const digits = phone.replace(/[^\d+]/g, '');
  return /^(\+?61|0)4\d{8}$/.test(digits);
}

function sign(jobUuid) {
  return crypto.createHmac('sha256', String(process.env.SERVICEM8_API_KEY)).update('job:' + jobUuid).digest('hex').slice(0, 40);
}

function tokenOk(jobUuid, token) {
  if (!jobUuid || !token || typeof token !== 'string') return false;
  const a = Buffer.from(sign(jobUuid)), b = Buffer.from(token);
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

function authHeaders(extra) {
  return Object.assign({ 'X-API-Key': process.env.SERVICEM8_API_KEY, Accept: 'application/json' }, extra || {});
}

async function smPost(path, body) {
  const r = await fetch(BASE + path, { method: 'POST', headers: authHeaders({ 'Content-Type': 'application/json' }), body: JSON.stringify(body) });
  if (!r.ok) throw new Error(`POST ${path} -> ${r.status} ${(await r.text().catch(() => '')).slice(0, 200)}`);
  return r.headers.get('x-record-uuid');
}

async function smGet(path) {
  const r = await fetch(BASE + path, { headers: authHeaders() });
  if (!r.ok) throw new Error(`GET ${path} -> ${r.status}`);
  return r.json();
}

async function readBody(req) {
  if (req.body && typeof req.body === 'object' && !Buffer.isBuffer(req.body)) return req.body;
  let raw = typeof req.body === 'string' ? req.body : Buffer.isBuffer(req.body) ? req.body.toString('utf8') : '';
  if (!raw) {
    const chunks = [];
    for await (const c of req) chunks.push(Buffer.isBuffer(c) ? c : Buffer.from(c));
    raw = Buffer.concat(chunks).toString('utf8');
  }
  return raw ? JSON.parse(raw) : {};
}

function send(res, status, data) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Cache-Control', 'no-store');
  res.end(JSON.stringify(data));
}

function noteText(title, data, fields, extra) {
  const lines = [title, ''];
  for (const k of fields) {
    const v = clean(data[k], 2000);
    if (v) lines.push(`${FIELD_LABELS[k] || k}: ${v}`);
  }
  if (extra && extra.length) lines.push('', ...extra);
  return lines.join('\n');
}

/* ---------- ServiceM8 steps ---------- */

async function findOrCreateClient(d, warnings) {
  const { first, last } = splitName(d.full_name);
  const email = clean(d.email, 200).toLowerCase();
  const phone = clean(d.phone, 40);
  if (email) {
    try {
      const q = encodeURIComponent(`email eq '${email.replace(/'/g, "''")}'`);
      const found = await smGet(`/companycontact.json?%24filter=${q}`);
      const hit = Array.isArray(found) && found.find((c) => c && c.company_uuid && String(c.active) !== '0');
      if (hit) return hit.company_uuid;
    } catch (e) { warnings.push('client lookup: ' + e.message); }
  }
  const companyUuid = await smPost('/company.json', { name: clean(d.full_name, 120) || email || phone || 'Website enquiry', active: 1 });
  try {
    await smPost('/companycontact.json', Object.assign(
      { company_uuid: companyUuid, first, last, email, is_primary_contact: 1, active: 1 },
      phone ? (isMobile(phone) ? { mobile: phone } : { phone }) : {}));
  } catch (e) { warnings.push('client contact: ' + e.message); }
  return companyUuid;
}

async function createJob(d, warnings) {
  const companyUuid = await findOrCreateClient(d, warnings);
  const address = [clean(d.property_address, 200), clean(d.postal_code, 10)].filter(Boolean).join(' ');
  const summary = ['Website quote request', d.service_needed && `Service: ${clean(d.service_needed, 300)}`, d.property_size && `Property size: ${clean(d.property_size, 80)}`]
    .filter(Boolean).join('\n');
  const jobUuid = await smPost('/job.json', Object.assign(
    { status: 'Quote', company_uuid: companyUuid, job_description: summary, active: 1 },
    address ? { job_address: address } : {}));
  if (!jobUuid) throw new Error('job created but no x-record-uuid returned');

  const { first, last } = splitName(d.full_name);
  const phone = clean(d.phone, 40);
  try {
    await smPost('/jobcontact.json', Object.assign(
      { job_uuid: jobUuid, type: 'JOB', first, last, email: clean(d.email, 200), active: 1 },
      phone ? (isMobile(phone) ? { mobile: phone } : { phone }) : {}));
  } catch (e) { warnings.push('job contact: ' + e.message); }
  return jobUuid;
}

async function addNote(jobUuid, text, warnings) {
  try {
    await smPost('/note.json', { related_object: 'job', related_object_uuid: jobUuid, note: text, active: 1 });
    return true;
  } catch (e) { warnings.push('note: ' + e.message); return false; }
}

async function attachPhoto(jobUuid, photo, i, warnings) {
  try {
    const m = /^(?:data:(image\/(?:jpeg|png|webp));base64,)?([A-Za-z0-9+/=\s]+)$/.exec(String(photo.data || ''));
    if (!m) throw new Error('not an image');
    const type = m[1] || 'image/jpeg';
    const buf = Buffer.from(m[2], 'base64');
    if (!buf.length || buf.length > MAX_PHOTO_BYTES) throw new Error('empty or too large');
    const ext = type === 'image/png' ? '.png' : type === 'image/webp' ? '.webp' : '.jpg';
    const name = `Website photo ${i + 1}${ext}`;
    const attUuid = await smPost('/attachment.json', {
      related_object: 'job', related_object_uuid: jobUuid, attachment_name: name, file_type: ext, active: 1,
    });
    const fd = new FormData();
    fd.append('file', new Blob([buf], { type }), name);
    const r = await fetch(`${BASE}/Attachment/${attUuid}.file`, { method: 'POST', headers: authHeaders(), body: fd });
    if (!r.ok) throw new Error(`file upload -> ${r.status}`);
    return true;
  } catch (e) { warnings.push(`photo ${i + 1}: ${e.message}`); return false; }
}

/* ---------- handler ---------- */

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') { res.setHeader('Allow', 'POST'); return send(res, 405, { ok: false, error: 'method' }); }
  const origin = req.headers.origin;
  if (origin && !ALLOWED_ORIGINS.some((r) => r.test(origin))) return send(res, 403, { ok: false, error: 'origin' });
  if (!process.env.SERVICEM8_API_KEY) return send(res, 503, { ok: false, error: 'ServiceM8 is not configured' });

  let body;
  try { body = await readBody(req); } catch (e) { return send(res, 400, { ok: false, error: 'bad json' }); }
  const d = body && typeof body.fields === 'object' && body.fields ? body.fields : {};
  if (clean(d.qf_extra)) return send(res, 200, { ok: true }); /* honeypot: pretend success */

  const warnings = [];
  try {
    if (body.step === 'qualify') {
      const answers = noteText('Website quote: qualifying answers (new customer)', d, STEP2_FIELDS);
      if (tokenOk(clean(body.job, 64), body.token)) {
        await addNote(clean(body.job, 64), answers, warnings);
        return send(res, 200, { ok: true, job: body.job, warnings: warnings.length });
      }
      /* Step 2 opened without step 1: create the job from the contact details given on this page. */
      if (!clean(d.full_name) || !(clean(d.email) || clean(d.phone))) return send(res, 422, { ok: false, error: 'missing contact details' });
      const jobUuid = await createJob(d, warnings);
      await addNote(jobUuid, noteText('Website quote request', d, ['full_name', 'email', 'phone'], [answers]), warnings);
      return send(res, 200, { ok: true, job: jobUuid, token: sign(jobUuid), warnings: warnings.length });
    }

    if (!clean(d.full_name) || !(clean(d.email) || clean(d.phone))) return send(res, 422, { ok: false, error: 'missing contact details' });
    const photos = Array.isArray(body.photos) ? body.photos.slice(0, MAX_PHOTOS) : [];
    const jobUuid = await createJob(d, warnings);
    const meta = [
      `Photos attached: ${photos.length}`,
      clean(body.page, 300) && `Sent from: ${clean(body.page, 300)}`,
      `Received: ${new Date().toLocaleString('en-AU', { timeZone: 'Australia/Sydney' })}`,
    ].filter(Boolean);
    await addNote(jobUuid, noteText('Website quote request', d, STEP1_FIELDS, meta), warnings);
    let attached = 0;
    for (let i = 0; i < photos.length; i++) if (await attachPhoto(jobUuid, photos[i], i, warnings)) attached++;
    if (warnings.length) console.warn('servicem8 warnings', jobUuid, warnings);
    return send(res, 200, { ok: true, job: jobUuid, token: sign(jobUuid), photos: attached, warnings: warnings.length });
  } catch (e) {
    console.error('servicem8 error', e.message, warnings);
    return send(res, 502, { ok: false, error: 'ServiceM8 request failed' });
  }
};

