from bs4 import BeautifulSoup
import html2text

def extract_plain_text(payload: bytes, content_type: str) -> str:
    """
    Convert raw email payload into plain text.
    Handles both HTML and plain text content types.
    """
    if content_type and "html" in content_type.lower():
        html = payload.decode(errors="ignore")
        soup = BeautifulSoup(html, "html.parser")
        # Prefer main body text, fall back to full text
        main = soup.get_text("\n", strip=True)
        return main
    try:
        return payload.decode()
    except Exception:
        return payload.decode(errors="ignore")

def clamp(text: str, max_chars: int = 5000) -> str:
    """
    Truncate text to a maximum number of characters.
    Useful for limiting input size to the LLM.
    """
    return text[:max_chars]
