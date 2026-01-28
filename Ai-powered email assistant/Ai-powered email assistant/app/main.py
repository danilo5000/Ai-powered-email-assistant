from fastapi import FastAPI, HTTPException, Depends, Query, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
import logging

from email_client import EmailClient
from ai_writer import draft_reply, draft_new
from rules import classify, auto_reply_allowed, next_action
from storage import store
from config import settings
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
app = FastAPI(
    title="AI Email Assistant",
    version="1.0.0",
    description="AI-powered email drafting and automation system"
)
class NewEmail(BaseModel):
    to: EmailStr
    brief: str = Field(..., min_length=5)
    style: Optional[str] = Field(default="professional")

class SendDraft(BaseModel):
    to: EmailStr
    subject: str
    body: str
    reply_to: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
def get_email_client() -> EmailClient:
    ec = EmailClient()
    try:
        yield ec
    finally:
        ec.close()
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return {"status": "ok"}

@app.get("/inbox/sync")
async def sync_inbox(ec: EmailClient = Depends(get_email_client)):
    try:
        ec.connect_imap()
        items = ec.fetch_unseen(settings.MAX_EMAILS)

        for item in items:
            store.add_inbox(item)

        logger.info("Inbox synced successfully")
        return {
            "fetched": len(items),
            "total_inbox": len(store.list_inbox())
        }

    except Exception as e:
        logger.error(f"Inbox sync failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Inbox synchronization failed"
        )

@app.get("/inbox")
async def list_inbox():
    return {"inbox": store.list_inbox()}

@app.post("/draft/reply/{idx}")
async def create_reply(
    idx: int,
    style: str = Query(default="professional"),
):
    inbox = store.list_inbox()

    if idx < 0 or idx >= len(inbox):
        raise HTTPException(status_code=404, detail="Email not found")

    email_item = inbox[idx]

    if not auto_reply_allowed(email_item):
        raise HTTPException(
            status_code=400,
            detail="Auto-reply not permitted for this sender"
        )

    try:
        draft = draft_reply(email_item, style)
        payload = {
            "to": email_item["from"],
            **draft,
            "reply_to": email_item.get("id")
        }
        store.add_draft(payload)

        return {
            "draft": payload,
            "classification": classify(email_item),
            "next_action": next_action(email_item)
        }

    except Exception as e:
        logger.error(f"Draft reply failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate reply")

@app.post("/draft/new")
async def create_new_email(req: NewEmail):
    try:
        draft = draft_new(req.to, req.brief, req.style)
        payload = {"to": req.to, **draft}
        store.add_draft(payload)
        return {"draft": payload}

    except Exception as e:
        logger.error(f"Draft creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create draft")

@app.get("/drafts")
async def list_drafts():
    return {"drafts": store.list_drafts()}

@app.post("/send")
async def send_email(
    req: SendDraft,
    ec: EmailClient = Depends(get_email_client)
):
    try:
        ec.connect_smtp()
        ec.send_email(
            to=req.to,
            subject=req.subject,
            body=req.body,
            reply_to=req.reply_to
        )
        logger.info(f"Email sent to {req.to}")
        return {"status": "sent"}

    except Exception as e:
        logger.error(f"Email sending failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email sending failed"
        )
