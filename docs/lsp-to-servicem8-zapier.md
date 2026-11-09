# Setup guide: Vercel Blob, GHL (LSP) and Zapier → ServiceM8

How a quote request travels:

```
Website form ── photos ──▶ Vercel Blob (public links)
     │
     └── every answer + photo links ──▶ GHL contact            (LSP tracking script)
                                            │  Workflow 1: opportunity in "Request Quote"
                                            │  team pre-qualifies the lead
                                            ▼
                         stage moved to "Auto Sync to Servicem8"
                                            │  Workflow 2: Webhook
                                            ▼
                         Zapier: Catch Hook ──▶ ServiceM8 job (status Quote)
```

The website never talks to ServiceM8. Nothing reaches ServiceM8 until someone moves the opportunity to
"Auto Sync to Servicem8".

Do the three parts in order: Blob, then GHL, then Zapier. The new site is only on the Vercel preview until
PR #8 is merged and the domain points at Vercel, so test there first.

---

## Part 1. Vercel Blob (photo storage)

1. Vercel → the Down the Rabbit Hole project → **Storage** tab → **Create Storage** → **Blob** → Continue.
2. Set access to **Public**. This matters: the photo links must open for whoever reads the ServiceM8 job.
   A Private store will make every upload fail.
3. Name it `dtrh-quote-photos` and select **Create**. Vercel connects it to Production and Preview.
   Leave "Add a read-write token env var" unticked. The default connection (it adds `BLOB_STORE_ID`)
   is what the site uses. Ticking it does no harm either.
4. **Redeploy** the project (Deployments → latest → Redeploy), so the function picks up the connection.
5. Optional clean-up: delete the `SERVICEM8_API_KEY` environment variable. Nothing uses it any more.

**Check it:** open the preview site, start a quote, add a photo. The thumbnail should finish loading
without a red outline. A red outline plus "A photo could not be uploaded" means the store is missing,
Private, or the project was not redeployed.

Photos are saved under `quote-photos/YYYY-MM/` in the store, with random file names. Anyone with a link
can open that photo, but links cannot be guessed. Old months can be deleted from the store's Browser tab.

---

## Part 2. GHL (LSP)

### 2a. Custom fields

Settings → **Custom Fields** → **Add Field**. Create each field below as a **contact** field, type
**Single Line** unless it says otherwise. Use the exact name shown: GHL turns the name into the key, and
the website's field names must match the keys. After saving, check the key shown under the field.

| Field name | Key it must get | Type | Filled by |
|---|---|---|---|
| Photo Links | `contact.photo_links` | **Multi Line** | Quote form (one link per line) |
| Property Size | `contact.property_size` | Single Line | Quote form |
| Returning Customer | `contact.returning_customer` | Single Line | Quote form (Yes or No) |
| Source Page | `contact.source_page` | Single Line | Quote form and quick questions |
| Form Step | `contact.form_step` | Single Line | "Quote request" or "Qualifying questions" |
| Service Frequency | `contact.service_frequency` | Single Line | Quick questions |
| Start Timeframe | `contact.start_timeframe` | Single Line | Quick questions |
| Property Type | `contact.property_type` | Single Line | Quick questions |
| Customer Role | `contact.customer_role` | Single Line | Quick questions |
| Yard Condition | `contact.yard_condition` | Single Line | Quick questions |
| DVA Card Holder | `contact.dva_card_holder` | Single Line | Quick questions |
| Lead Source | `contact.lead_source` | Single Line | Quick questions |

These already exist, so do not recreate them:

| Field | Key | Note |
|---|---|---|
| Service Needed | `contact.service_needed` | The text one. Not the dropdown also called "Service Needed" (`service_needs`) |
| Job Notes | `contact.job_notes` | |
| Name, Email, Phone, Postal Code | standard fields | Filled automatically |

If a key comes out different (for example `contact.photo_links_1` because the name was used before), tell
the developer, so the website field can be renamed to match.

### 2b. External Tracking

Settings → **External Tracking**.

1. **Installation**: the tracking code is already on the website (tracking ID `tk_6f4c…`). Nothing to add.
2. **Settings**: open the website's domain (the `….vercel.app` preview now, `downtherabbitholeaust.com`
   after launch). Check **Form submissions** is on, and **Track** is on for `q-form` (contact sections),
   `m-form` (pop-up) and `qd-form` (quick questions). Forms appear after their first test submission.
3. **Map fields** on `q-form` and on `m-form`:
   - `property_address` → **Street Address**
   - `qf_extra` → **Do not track** (spam trap, always empty)
   - Leave everything else on automatic.

Map fields is part of the newer External Tracking screen. If it is missing, turn it on under **Labs** in the
sub-account settings. Without it, the address lands in the submission but not on the contact's address.

**Check it:** send a test quote with a photo from the preview site. Open the contact. Every field in 2a
should be filled, and Photo Links should hold a link that opens the photo. A value shown as "unmapped"
means the field's key does not match.

### 2c. Workflow 1: new website lead → opportunity

Automation → Workflows → Create → "Website quote → Request Quote".

- **Trigger:** **External Tracking Event**, event **Form submission**. If it offers a form or page
  filter, limit it to `q-form` and `m-form`.
- **Action: If/Else.** Continue only when Form Step is `Quote request`. This stops the quick-questions
  submission from running it a second time.
- **Action: Create Opportunity.** Pipeline **Client Management**, stage **Request Quote**, name
  `{{contact.name}} – website quote`, source `Website`. Leave "Allow duplicate opportunities" off.
- Add the team's usual notification (internal SMS or email) if wanted. Publish.

### 2d. Workflow 2: pre-qualified → ServiceM8

Create Workflow 2 after the Zapier hook exists (Part 3, step 1), because it needs the hook URL.

Automation → Workflows → Create → "Send to ServiceM8".

- **Trigger:** **Pipeline Stage Changed**. Pipeline **Client Management**, moved to stage
  **Auto Sync to Servicem8**.
- **Action: Webhook** (the standard one, not the paid "Custom Webhook"). Method **POST**. URL: the Zapier
  Catch Hook URL. Under **Custom Data**, click **+ Add item** for each row below. Type the key, and insert
  the value with the merge-field picker so it matches the account.

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
| `old_form_service` | `{{contact.service_interest}}` |
| `old_form_notes` | `{{contact.any_notes}}` (pick "Additional Information" in the picker) |

  The two `old_form_` rows cover leads that still arrive through the old site's form until launch day.
  Remove them once the new site is live.
- **Action (optional): Update Opportunity** → stage **New Job**, so the board shows it was sent.
- Publish.

The standard Webhook also sends every contact field on its own, but under their display names. The Custom
Data rows give Zapier short, predictable names.

---

## Part 3. Zapier

Needs a paid Zapier plan (Webhooks by Zapier is a premium app).

**Before starting:** Zapier → **Apps** → add **ServiceM8** and log in to the client's ServiceM8 account.
It is not connected yet.

### Step 1. Trigger: Webhooks by Zapier → Catch Hook

- Create a Zap, choose **Webhooks by Zapier**, event **Catch Hook**, then Continue (no options needed).
- Copy the hook URL into Workflow 2's Webhook action (Part 2d) and publish that workflow.
- In GHL, move a test opportunity to **Auto Sync to Servicem8**. Back in Zapier, **Test trigger**. The
  fields show up as "Custom Data First Name", "Custom Data Photo Links" and so on.

### Step 2. Action: ServiceM8 → Create Job

The ServiceM8 app in Zapier only has Create Job and Create Client. It cannot add notes or attach files, so
all the details go into the job description and the photos go in as links.

| ServiceM8 field | Set to |
|---|---|
| Customer Name | Leave blank. ServiceM8 creates the client from the job contact |
| Job Status | `Quote` |
| Job Address | Custom Data Address, a space, Custom Data Postcode |
| Billing Address | Same as Job Address |
| Job Description | The template below |
| Job Contact First Name | Custom Data First Name |
| Job Contact Last Name | Custom Data Last Name |
| Job Contact Mobile | Custom Data Phone |
| Job Contact E-Mail Address | Custom Data Email |
| Billing Contact First Name, Last Name, Mobile, E-Mail | Same as the job contact |
| Everything else | Leave blank |

Job Description: type the labels and insert the matching Custom Data field after each one.

```
Website quote request (pre-qualified in LSP)
Service needed: [Service Needed]
Property size: [Property Size]
Used us before: [Returning Customer]
How often: [Service Frequency]
When: [Start Timeframe]
Property type: [Property Type]
Connection to property: [Customer Role]
Lawn/garden condition: [Yard Condition]
DVA card holder: [DVA Card Holder]
Heard about us via: [Lead Source]

Job notes:
[Job Notes]

Photos (open in a browser):
[Photo Links]

Old site form (until launch): [Old Form Service] [Old Form Notes]
```

**Test step**, check the new Quote job in ServiceM8, then delete the test job.

### Step 3 (optional). LeadConnector → Add/Update Contact

Match on Custom Data Email and add the tag `servicem8-synced`. Handy for spotting a lead that never synced.

Name the Zap "DTRH: LSP → ServiceM8 quote" and turn it on.

---

## Final test (end to end)

1. On the preview site, send a quote as a new customer, with two photos, then answer the quick questions.
2. In GHL: the contact has every field filled, and an opportunity sits in **Request Quote**.
3. Move it to **Auto Sync to Servicem8**.
4. In ServiceM8: a Quote job with the address, the contact, the full description and two photo links
   that open.
5. In Zapier: the run shows as successful under Zap history.

## If something is missing

| Symptom | Likely cause |
|---|---|
| Photo thumbnail turns red on the website | Blob store missing or Private, or no redeploy after connecting it |
| Field empty on the GHL contact | Custom field key does not match (check 2a), or the form's Track switch is off (2b) |
| Address empty on the GHL contact | `property_address` not mapped to Street Address (2b) |
| Two opportunities for one lead | Workflow 1 is missing the Form Step check (2c) |
| Nothing in Zapier | Workflow 2 not published, wrong hook URL, or the stage name differs |
| Zap fails at ServiceM8 | ServiceM8 connection expired, or Job Status not set to `Quote` |
| Returning customer appears twice in ServiceM8 | Expected with Customer Name blank. Merge in ServiceM8, or move returning customers to **Manual Sync Servm8** instead so staff attach the job to the existing client |
