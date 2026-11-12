// cccops.com contact form -> consultingbytriplec@gmail.com + "CCC Website Leads" sheet.
// Deploy: Apps Script project owned by consultingbytriplec@gmail.com,
//   Deploy > New deployment > Web app, Execute as: Me, Who has access: Anyone.
// The site POSTs JSON as text/plain (no CORS preflight).

const NOTIFY_TO = 'consultingbytriplec@gmail.com';
const SHEET_NAME = 'CCC Website Leads';

function doPost(e) {
  let d;
  try {
    d = JSON.parse(e.postData.contents);
  } catch (err) {
    return out_({ success: false, error: 'Bad request.' });
  }
  if (d.honeypot) return out_({ success: true }); // bot filled the hidden field

  const clip = (v, n) => String(v || '').trim().slice(0, n);
  const name = clip(d.name, 200);
  const email = clip(d.email, 200);
  const org = clip(d.organization, 200);
  const msg = clip(d.message, 5000);

  if (!name || !msg || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return out_({ success: false, error: 'Please fill in your name, a valid email and a message.' });
  }

  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    sheet_().appendRow([new Date(), name, email, org, msg]);
  } finally {
    lock.releaseLock();
  }

  MailApp.sendEmail({
    to: NOTIFY_TO,
    replyTo: email,
    subject: 'cccops.com lead: ' + name + (org ? ' (' + org + ')' : ''),
    body: 'Name: ' + name + '\nEmail: ' + email + '\nOrganization: ' + org +
          '\n\n' + msg + '\n\nHit reply to answer them directly.'
  });

  return out_({ success: true, message: 'Thanks. You will hear back within one business day.' });
}

function doGet() {
  return out_({ ok: true, service: 'cccops-contact' });
}

function sheet_() {
  const props = PropertiesService.getScriptProperties();
  const id = props.getProperty('SHEET_ID');
  if (id) return SpreadsheetApp.openById(id).getSheets()[0];
  const ss = SpreadsheetApp.create(SHEET_NAME);
  ss.getSheets()[0].appendRow(['Received', 'Name', 'Email', 'Organization', 'Message']);
  props.setProperty('SHEET_ID', ss.getId());
  return ss.getSheets()[0];
}

function out_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
