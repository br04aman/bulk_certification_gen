import pytest
from pydantic import ValidationError
from app.schemas import RecipientInput, JobCreateRequest


def test_valid_recipient_input():
    recipient = RecipientInput(
        name="Alice Smith",
        email="alice@example.com",
        custom_attributes={"grade": "A+"}
    )
    assert recipient.name == "Alice Smith"
    assert recipient.email == "alice@example.com"
    assert recipient.custom_attributes == {"grade": "A+"}


def test_invalid_recipient_empty_name():
    with pytest.raises(ValidationError):
        RecipientInput(name="   ", email="test@example.com")


def test_invalid_recipient_email_format():
    with pytest.raises(ValidationError):
        RecipientInput(name="Bob", email="invalid-email-string")


def test_valid_job_create_request():
    payload = JobCreateRequest(
        title="Python Mastery Workshop",
        issuer_name="Global Tech Institute",
        issue_date="2026-10-08",
        recipients=[
            {"name": "Carol Danvers", "email": "carol@example.com"}
        ]
    )
    assert payload.title == "Python Mastery Workshop"
    assert len(payload.recipients) == 1


def test_invalid_job_create_empty_recipients():
    with pytest.raises(ValidationError):
        JobCreateRequest(
            title="Workshop",
            issuer_name="Tech Institute",
            issue_date="2026-10-08",
            recipients=[]
        )


def test_invalid_job_create_blank_fields():
    with pytest.raises(ValidationError):
        JobCreateRequest(
            title="  ",
            issuer_name="Issuer",
            issue_date="2026-10-08",
            recipients=[{"name": "User", "email": "user@example.com"}]
        )
