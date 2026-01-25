import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from typing import List, Dict, Optional
from .config import settings
from .utils import extract_plain_text

class EmailClient:
    def __init__(self):
        self.imap = None
        self.smtp = None

    def connect_imap(self):
        self.imap = imaplib.IMAP4_SSL(settings.IMAP_HOST, settings.IMAP_PORT)
        self.imap.login(settings.EMAIL_ADDRESS, settings.EMAIL_PASSWORD)
        self.imap.select(settings.INBOX_LABEL)

    def connect_smtp(self):
        self.smtp = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        self.smtp.ehlo()
        self.smtp.starttls()
        self.smtp.login(settings.EMAIL_ADDRESS, settings.EMAIL_PASSWORD)

    def fetch_unseen(self, max_emails: int = 25) -> List[Dict]:
        status, data = self.imap.search(None, '(UNSEEN)')
        if status != 'OK':
            return []

        ids = data[0].split()[-max_emails:]
        emails: List[Dict] = []
        for msg_id in ids:
            _, msg_data = self.imap.fetch(msg_id, '(RFC822)')
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)
            subject = email.header.decode_header(msg.get("Subject"))[0]
            subject_text = subject[0]
            if isinstance(subject_text, bytes):
                subject_text = subject_text.decode(errors="ignore")
            from_ = msg.get("From")
            to = msg.get("To")
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    ctype = part.get_content_type()
                    if ctype in ["text/plain", "text/html"]:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = extract_plain_text(payload, ctype)
                            break
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = extract_plain_text(payload, msg.get_content_type())
            emails.append({
                "id": msg_id.decode(),
                "subject": subject_text or "",
                "from": from_ or "",
                "to": to or "",
                "body": body or "",
            })
        return emails

    def send_email(self, to_address: str, subject: str, body: str, reply_to: Optional[str] = None):
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = settings.EMAIL_ADDRESS
        msg["To"] = to_address
        if reply_to:
            msg["In-Reply-To"] = reply_to
            msg["References"] = reply_to
        self.smtp.sendmail(settings.EMAIL_ADDRESS, [to_address], msg.as_string())

    def close(self):
        try:
            if self.imap:
                self.imap.close()
                self.imap.logout()
        except Exception:
            pass
        try:
            if self.smtp:
                self.smtp.quit()
        except Exception:
            pass
