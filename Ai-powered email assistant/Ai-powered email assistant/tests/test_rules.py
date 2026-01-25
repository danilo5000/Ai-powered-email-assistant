import pytest
from app.rules import classify, auto_reply_allowed, next_action

def test_classify_urgent():
    email = {"subject": "ASAP needed", "body": "This is urgent and critical"}
    result = classify(email)
    assert "urgent" in result["tags"]
    assert result["priority"] == "high"

def test_classify_sales():
    email = {"subject": "Pricing request", "body": "Can you send me a quote?"}
    result = classify(email)
    assert "sales" in result["tags"]
    assert result["priority"] == "normal"

def test_classify_support():
    email = {"subject": "Bug report", "body": "There is an error on the page"}
    result = classify(email)
    assert "support" in result["tags"]
    assert result["priority"] == "normal"

def test_classify_general():
    email = {"subject": "Hello", "body": "Just checking in"}
    result = classify(email)
    assert "general" in result["tags"]
    assert result["priority"] == "normal"

def test_auto_reply_allowed_blocks_noreply():
    email = {"from": "no-reply@example.com"}
    assert auto_reply_allowed(email) is False

def test_auto_reply_allowed_allows_normal_sender():
    email = {"from": "user@example.com"}
    assert auto_reply_allowed(email) is True

def test_next_action_urgent():
    email = {"subject": "Deadline ASAP", "body": "This is urgent"}
    assert next_action(email) == "draft_reply"

def test_next_action_support():
    email = {"subject": "Bug found", "body": "Please fix this issue"}
    assert next_action(email) == "create_ticket"

def test_next_action_sales():
    email = {"subject": "Invoice needed", "body": "Send me a quote"}
    assert next_action(email) == "notify_sales"

def test_next_action_general():
    email = {"subject": "Hello", "body": "Just saying hi"}
    assert next_action(email) == "draft_reply"
