from typing import Dict
from openai import OpenAI
from .config import settings
from .utils import clamp

SYSTEM_PROMPT = """You are an AI email assistant. Draft clear, concise, and polite emails.
- Keep to 150-250 words unless asked otherwise.
- Reflect sender's tone: professional, friendly, or neutral.
- Include a descriptive subject if creating a new email.
- Use bullet points where clarity helps.
- Avoid oversharing. Confirm facts if uncertain."""

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def draft_reply(email_item: Dict, style: str = "professional") -> Dict:
    body = clamp(email_item.get("body", ""), 4500)
    subject = email_item.get("subject", "")
    sender = email_item.get("from", "")

    user_prompt = f"""Draft a reply.

Incoming email:
From: {sender}
Subject: {subject}
Body:
{body}

Reply requirements:
- Style: {style}
- Acknowledge key points.
- Propose next steps or ask clarifying questions.
- Keep it actionable."""

    resp = client.chat.completions.create(
        model=settings.MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
    )

    content = resp.choices[0].message.content.strip()
    # Simple subject extraction if model proposes one on first line
    lines = content.splitlines()
    proposed_subject = subject
    if lines and lines[0].lower().startswith("subject:"):
        proposed_subject = lines[0].split(":", 1)[1].strip()
        content = "\n".join(lines[1:]).strip()

    return {
        "subject": proposed_subject,
        "body": content,
    }

def draft_new(to: str, brief: str, style: str = "professional") -> Dict:
    user_prompt = f"""Write a new email to {to}.
Goal: {brief}
Style: {style}.
Include a concise subject line on the first line as 'Subject: ...'."""

    resp = client.chat.completions.create(
        model=settings.MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.5,
    )
    content = resp.choices[0].message.content.strip()
    lines = content.splitlines()
    subject = "Re: "
    if lines and lines[0].lower().startswith("subject:"):
        subject = lines[0].split(":", 1)[1].strip()
        content = "\n".join(lines[1:]).strip()
    return {"subject": subject, "body": content}
