from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from .email_client import EmailClient
from .ai_writer import draft_reply, draft_new
from .rules import classify, auto_reply_allowed, next_action
from .storage import store
from .config import settings
from rich import print

app = FastAPI(title="AI Email Assistant", version="0.1.0")

class NewEmail(BaseModel):
    to: EmailStr
    brief: str
    style: Optional[str] = "professional"

class SendDraft(BaseModel):
    to: EmailStr
    subject: str
    body: str
    reply_to: Optional[str] = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/inbox/sync")
def sync_inbox():
    ec = EmailClient()
    try:
        ec.connect_imap()
        items = ec.fetch_unseen(settings.MAX_EMAILS)
        for it in items:
            store.add_inbox(it)
        return {"fetched": len(items), "inbox_count": len(store.list_inbox())}
    finally:
        ec.close()

@app.get("/inbox")
def list_inbox():
    return {"inbox": store.list_inbox()}

@app.post("/draft/reply/{idx}")
def create_reply(idx: int, style: Optional[str] = "professional"):
    inbox = store.list_inbox()
    if idx < 0 or idx >= len(inbox):
        raise HTTPException(status_code=404, detail="Email not found")
    email_item = inbox[idx]
    if not auto_reply_allowed(email_item):
        raise HTTPException(status_code=400, detail="Auto-reply not allowed to this sender")
    draft = draft_reply(email_item, style)
    payload = {"to": email_item["from"], **draft, "reply_to": email_item.get("id")}
    store.add_draft(payload)
    return {"draft": payload, "classification": classify(email_item), "action": next_action(email_item)}

@app.post("/draft/new")
def create_new_email(req: NewEmail):
    draft = draft_new(req.to, req.brief, req.style)
    payload = {"to": req.to, **draft}
    store.add_draft(payload)
    return {"draft": payload}

@app.get("/drafts")
def list_drafts():
    return {"drafts": store.list_drafts()}

@app.post("/send")
def send_email(req: SendDraft):
    ec = EmailClient()
    try:
        ec.connect_smtp()
        ec.send_email(req.to, req.subject, req.body, reply_to=req.reply_to)
        return {"status": "sent"}
    finally:
        ec.close()