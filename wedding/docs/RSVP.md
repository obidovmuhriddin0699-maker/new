# Connecting the RSVP form

The form posts one JSON object per reply to `config.rsvp.rsvpEndpoint`:

```json
{
  "submissionId": "6f1c…",          // stable per reply: use it to ignore duplicates
  "name": "Aziza Karimova",
  "attendance": "yes",              // "yes" | "no"
  "guests": 3,                      // 0 when attendance is "no"
  "message": "Baxtli bo‘linglar!",
  "event": "Muxriddin & Umida · 2026-10-06",
  "submittedAt": "2026-09-20T07:12:44.120Z",
  "page": "https://…/"
}
```

The guest sees a success message only when the endpoint answers with HTTP 2xx and the
body isn't `{"ok": false}`, `{"success": false}` or `{"result": "error"}`. Errors and
timeouts (15s) leave the form filled in, so the guest can retry.

---

## Option A: Google Sheets (free, about 10 minutes)

1. Create a Google Sheet, for example "To‘y javoblari".
2. **Extensions → Apps Script**, replace the code with the script below, and save.
3. **Deploy → New deployment → Web app**: *Execute as:* **Me**; *Who has access:* **Anyone**.
   Authorise, then copy the **Web app URL** (`https://script.google.com/macros/s/…/exec`).
4. In `config.js`:
   ```js
   rsvp: {
     rsvpEndpoint: "https://script.google.com/macros/s/XXXX/exec",
     format: "text",   // required for Apps Script (avoids the CORS preflight it can't answer)
     ...
   }
   ```
5. Send one test reply from the live site and check that a row appears.

```js
// Apps Script — paste into Extensions → Apps Script
const SHEET_NAME = "Javoblar";

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const data = JSON.parse(e.postData.contents);
    const book = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = book.getSheetByName(SHEET_NAME) || book.insertSheet(SHEET_NAME);
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(["Vaqt", "Ism", "Ishtirok", "Mehmonlar", "Tilak", "submissionId"]);
    }
    // Ignore repeats of the same reply (retries, double taps).
    const last = sheet.getLastRow();
    const ids = last > 1 ? sheet.getRange(2, 6, last - 1, 1).getValues().flat() : [];
    if (!ids.includes(data.submissionId)) {
      // Prefix values a spreadsheet would treat as formulas.
      const safe = (v) => /^[=+\-@]/.test(String(v)) ? "'" + v : v;
      sheet.appendRow([
        new Date(),
        safe(String(data.name || "").slice(0, 80)),
        data.attendance === "yes" ? "Ha" : "Yo‘q",
        Number(data.guests) || 0,
        safe(String(data.message || "").slice(0, 500)),
        String(data.submissionId || "")
      ]);
    }
    return json({ ok: true });
  } catch (err) {
    return json({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
```

After editing the script later, use **Deploy → Manage deployments → Edit → New version**,
or the URL keeps running the old code.

## Option B: Formspree (hosted form service)

1. Create a form at formspree.io and copy its endpoint (`https://formspree.io/f/xxxxxxx`).
2. Set `rsvpEndpoint` to that URL and keep `format: "json"`.
3. Replies arrive by e-mail and in the Formspree dashboard.

## Option C: your own API

Accept `POST` with `Content-Type: application/json` (or `text/plain` when `format: "text"`),
allow the site's origin via CORS (`Access-Control-Allow-Origin`), return 2xx with
`{"ok": true}`, and de-duplicate on `submissionId`.

---

**Verification status:** the form's behaviour (validation, loading state, single
submission, success, errors, retry) is covered by the automated tests against a mocked
endpoint. Google Sheets and Formspree can't be tested from this repository. Send one real
test reply after connecting either of them.
