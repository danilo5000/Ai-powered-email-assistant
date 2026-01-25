\# AI-Powered Email Assistant



A lightweight backend that reads emails from IMAP, drafts replies with an LLM, applies simple rules, and sends via SMTP.



\## Features

\- \*\*Inbox sync:\*\* Fetch unseen emails from IMAP.

\- \*\*AI drafting:\*\* Generate replies and new emails with configurable style.

\- \*\*Rules engine:\*\* Tag emails and suggest actions (urgent/support/sales).

\- \*\*Send mail:\*\* SMTP with TLS.

\- \*\*REST API:\*\* FastAPI endpoints for integration.



\## Setup



\### 1) Install

```bash

python -m venv .venv

source .venv/bin/activate  # Windows: .venv\\Scripts\\activate

pip install -r requirements.txt



