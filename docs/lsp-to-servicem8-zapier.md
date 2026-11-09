# Website → LSP → ServiceM8 (via Zapier)

Every quote request now lands in LSP first. The team pre-qualifies it there, and only then does it go to
ServiceM8 as a Quote job, through Zapier. The website no longer talks to ServiceM8 at all.

```
Website form ──(LSP tracking script)──▶ LSP contact + opportunity
                                           │  team pre-qualifies
                                           ▼
                     Client Management pipeline → stage "Auto Sync to Servicem8"
                                           │  LSP workflow: Webhook action
                                           ▼
                     Zapier: Catch Hook → ServiceM8 "Create Job" (status Quote)
```

Photos are uploaded by the website to Vercel Blob storage when the visitor picks them. The form sends the
links to LSP in the `photo_links` field, and the Zap puts them in the ServiceM8 job description.

---

## 1. Fields the website sends to LSP

Checked against what the LSP tracking script actually sends (a recorded test submission). The tracking
script matches each form field to an LSP field **by its key**, so each custom field below must exist with
exactly this key. In LSP, a custom field named "Photo Links" gets the key `photo_links`, and so on.

### Step 1: quote form (every visitor)

| Form field (key) | Question on the website | LSP field | Action in LSP |
|---|---|---|---|
| `full_name` | Full name | Standard: name (split into first and last) | None |
| `email` | Email | Standard: Email | None |
| `phone` | Phone | Standard: Phone | None |
| `property_address` | Property address | Standard: Street Address | Map it manually (see step 2b) |
| `postal_code` | Postcode | Standard: Postal Code | None |
| `property_size` | Property size | Custom: **Property Size** | Create (single line text) |
| `service_needed` | Service needed (several allowed, comma separated) | Custom: **Service Needed** `service_needed` | Already exists. Use this one, not the dropdown "Service Needed" (`service_needs`) |
| `job_notes` | Job notes | Custom: **Job Notes** `job_notes` | Already exists |
| `photo_links` | (photos, sent automatically) | Custom: **Photo Links** | Create (multi line text). One link per line |
| `returning_customer` | Have you used us before? Yes or No | Custom: **Returning Customer** | Create (single line text) |
| `source_page` | (sent automatically) | Custom: **Source Page** | Create (single line text) |
| `form_step` | (sent automatically: "Quote request") | Custom: **Form Step** | Create (single line text) |
| `qf_extra` | (spam trap, always empty) | none | Set to **Do not track** |

### Step 2: quick questions (new customers only)

Sent as a second submission with the same name, email and phone, so LSP adds the answers to the same contact.

| Form field (key) | Question | LSP field | Action in LSP |
|---|---|---|---|
| `service_frequency` | How often do you need the service? | Custom: **Service Frequency** | Create (single line text) |
| `start_timeframe` | When would you like the work done? | Custom: **Start Timeframe** | Create |
| `property_type` | What type of property is it? | Custom: **Property Type** | Create |
| `customer_role` | What is your connection to the property? | Custom: **Customer Role** | Create |
| `yard_condition` | What condition is the lawn or garden in now? | Custom: **Yard Condition** | Create |
| `dva_card_holder` | Are you a DVA card holder? | Custom: **DVA Card Holder** | Create |
| `lead_source` | How did you hear about us? | Custom: **Lead Source** | Create |
| `form_step` | (sent automatically: "Qualifying questions") | Custom: **Form Step** | Same field as step 1 |

Single line text is the safe type for all of these. A dropdown only works if its options match the website's
answers exactly. The options are listed in `QUALIFY_QUESTIONS` and `SIZE_OPTIONS` in `tools/build.py`.

The account already has older fields that look similar, such as "2. Is this a one-time job or ongoing
maintenance?". Their keys are different, so the website cannot fill them. Leave them alone or delete them.

---

## 2. LSP setup

**a. Custom fields.** Settings → Custom Fields. Create the fields marked "Create" above, as contact fields.
After creating each one, check its key reads exactly as listed (for example `contact.photo_links`).

**b. External Tracking mapping.** Settings → External Tracking → Settings → open
`downtherabbitholeaust.com`. Make sure the quote form (`q-form`), the pop-up form (`m-form`) and the
quick-questions form (`qd-form`) have **Track** on. Then click **Map fields** on `q-form` and `m-form`:
- `property_address` → Street Address
- `qf_extra` → Do not track

Manual mapping only covers standard fields. Custom fields are matched automatically by key, which is why
step a has to come first. Mapping changes apply to new submissions only.

**c. Send a test** from the live site, with one photo. Open the contact in LSP and check every field above,
including Photo Links. If a field shows as "unmapped", its key does not match.

**d. Workflow.** Automation → Workflows → new workflow "Send to ServiceM8".
- Trigger: **Pipeline Stage Changed**. Pipeline: Client Management. Stage: **Auto Sync to Servicem8**.
- Action: **Webhook** (the standard one, not the paid Custom Webhook). Method POST. URL: the Zapier
  Catch Hook URL from section 3. Under **Custom Data**, add these keys and values:

| Key | Value |
|---|---|
| `first_name` | `{{contact.first_name}}` |
| `last_name` | `{{contact.last_name}}` |
| `email` | `{{contact.email}}` |
| `phone` | `{{contact.phone}}` |
| `address` | `{{contact.address1}}` |
| `postcode` | `{{contact.postal_code}}` |
| `service_needed` | `{{contact.service_needed}}` |
| `property_size` | `{{contact.property_size}}` |
| `job_notes` | `{{contact.job_notes}}` |
| `photo_links` | `{{contact.photo_links}}` |
| `returning_customer` | `{{contact.returning_customer}}` |
| `service_frequency` | `{{contact.service_frequency}}` |
| `start_timeframe` | `{{contact.start_timeframe}}` |
| `property_type` | `{{contact.property_type}}` |
| `customer_role` | `{{contact.customer_role}}` |
| `yard_condition` | `{{contact.yard_condition}}` |
| `dva_card_holder` | `{{contact.dva_card_holder}}` |
| `lead_source` | `{{contact.lead_source}}` |
| `contact_id` | `{{contact.id}}` |

  Pick each value from the merge-field picker rather than typing it, so the keys match the account.
- Optional last action: **Update Opportunity** → move it to the **New Job** stage, so it is clear the job
  has been sent.

**Why a webhook instead of the LeadConnector trigger in Zapier.** Zapier's LeadConnector "Pipeline Stage
Changed" trigger sends only standard contact fields (name, email, phone, address, tags, stage). It does not
include custom fields, so service needed, notes, photo links and the quick-question answers would be lost.

---

## 3. Zapier setup

Connect ServiceM8 in Zapier first (My Apps → ServiceM8). It is not connected in the Zapier account yet.

**Step 1. Trigger: Webhooks by Zapier → Catch Hook.** Copy the hook URL into the LSP workflow (section 2d).
Move a test opportunity to "Auto Sync to Servicem8" so Zapier receives a sample. The fields appear as
"Custom Data First Name", "Custom Data Service Needed" and so on.

**Step 2. Action: ServiceM8 → Create Job.** The Zapier ServiceM8 app offers Create Job and Create Client
only. It has no note or attachment actions, so everything goes in the job description.

| ServiceM8 field | Value from the Catch Hook |
|---|---|
| Customer Name | Leave blank. ServiceM8 creates the customer from the job contact details |
| Job Status | `Quote` |
| Job Address | `address` `postcode` |
| Billing Address | `address` `postcode` |
| Job Description | The template below |
| Job Contact First Name | `first_name` |
| Job Contact Last Name | `last_name` |
| Job Contact Mobile | `phone` |
| Job Contact E-Mail Address | `email` |
| Billing Contact First Name, Last Name, Mobile, E-Mail | Same as the job contact |

Job Description template (type the labels, insert the fields):

```
Website quote request (pre-qualified in LSP)
Service needed: {service_needed}
Property size: {property_size}
Used us before: {returning_customer}
How often: {service_frequency}
When: {start_timeframe}
Property type: {property_type}
Connection to property: {customer_role}
Lawn/garden condition: {yard_condition}
DVA card holder: {dva_card_holder}
Heard about us via: {lead_source}

Job notes:
{job_notes}

Photos:
{photo_links}
```

**Step 3 (optional).** LeadConnector → Add/Update Contact, matched on the `email` from the hook, to add the
tag `servicem8-synced`. Useful for reporting and for spotting a failed sync.

Turn the Zap on, then move a real test opportunity to "Auto Sync to Servicem8" and check the ServiceM8 job.

---

## 4. Things to know

- **Returning customers.** With Customer Name blank, ServiceM8 creates a new customer each time, so a
  returning customer gets a duplicate client record. Two ways to handle it: merge duplicates in ServiceM8,
  or move returning customers ("Returning Customer" = Yes) to the existing **Manual Sync Servm8** stage
  instead, so staff create the job against the existing client.
- **Photos are links, not attachments.** The links open the photo in a browser. They are public but
  unguessable (random file names). Attaching the actual files to the ServiceM8 job would need a
  Code by Zapier step that downloads each link and posts it to ServiceM8's attachment API.
- **Photo storage.** Photos live in the project's Vercel Blob store under `quote-photos/YYYY-MM/`. Removing
  a photo on the form before sending does not delete the uploaded file. Old months can be cleared from the
  Vercel dashboard once the jobs are done.
- **If photo storage is not set up**, the form still sends. The photo shows as failed and the visitor is
  asked to text it instead.
- **The old direct integration is gone.** `api/quote.js` was removed, so the `SERVICEM8_API_KEY`
  environment variable in Vercel is no longer used and can be deleted.
