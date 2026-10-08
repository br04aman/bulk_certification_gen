from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict


class RecipientInput(BaseModel):
    name: str = Field(..., description="Recipient's full name", min_length=1)
    email: EmailStr = Field(..., description="Recipient's email address")
    custom_attributes: Optional[Dict[str, Any]] = Field(default=None, description="Additional custom metadata")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Recipient name cannot be empty or whitespace only.")
        return stripped


class JobCreateRequest(BaseModel):
    title: str = Field(..., description="Event or Course Title", min_length=1, max_length=250)
    issuer_name: str = Field(..., description="Organization or Issuer Name", min_length=1, max_length=250)
    issue_date: str = Field(..., description="Issue date (e.g. YYYY-MM-DD or October 8, 2026)")
    recipients: List[RecipientInput] = Field(..., description="List of recipient information", min_length=1)

    @field_validator("title", "issuer_name", "issue_date")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Field cannot be empty or whitespace only.")
        return stripped


class CertificateRecordResponse(BaseModel):
    id: str
    job_id: str
    recipient_name: str
    recipient_email: str
    custom_attributes: Optional[Dict[str, Any]] = None
    status: str
    certificate_code: str
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    generated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class JobResponse(BaseModel):
    id: str
    title: str
    issuer_name: str
    issue_date: str
    status: str
    total_recipients: int
    success_count: int
    failed_count: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    records: Optional[List[CertificateRecordResponse]] = None

    model_config = ConfigDict(from_attributes=True)

