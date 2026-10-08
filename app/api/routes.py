import os
import uuid
import zipfile
from io import BytesIO
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status, Query
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CertificateJob, CertificateRecord, JobStatus, CertificateStatus
from app.schemas import JobCreateRequest, JobResponse, CertificateRecordResponse
from app.services.job_processor import process_certificate_job

router = APIRouter(prefix="/api/v1", tags=["Certificates"])


def generate_unique_code() -> str:
    """Generates a human-friendly unique certificate verification code."""
    return f"CERT-{uuid.uuid4().hex[:8].upper()}"


@router.post(
    "/certificates/generate",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit a bulk certificate generation job",
    description="Accepts certificate metadata and recipient list, creates job records, and triggers background bulk generation."
)
def create_certificate_job(
    request: JobCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # 1. Create Job Entry
    job_id = str(uuid.uuid4())
    job = CertificateJob(
        id=job_id,
        title=request.title,
        issuer_name=request.issuer_name,
        issue_date=request.issue_date,
        status=JobStatus.PENDING.value,
        total_recipients=len(request.recipients),
        success_count=0,
        failed_count=0
    )
    db.add(job)

    # 2. Create Certificate Records for each recipient
    records = []
    for recipient in request.recipients:
        record = CertificateRecord(
            id=str(uuid.uuid4()),
            job_id=job_id,
            recipient_name=recipient.name,
            recipient_email=str(recipient.email),
            custom_attributes=recipient.custom_attributes,
            status=CertificateStatus.PENDING.value,
            certificate_code=generate_unique_code()
        )
        db.add(record)
        records.append(record)

    db.commit()
    db.refresh(job)

    # 3. Trigger Async Background Worker
    background_tasks.add_task(process_certificate_job, job_id)

    return job


@router.get(
    "/jobs/{job_id}",
    response_model=JobResponse,
    summary="Get job status and progress",
    description="Retrieves job metrics, current status, and full breakdown of recipient certificate statuses."
)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(CertificateJob).filter(CertificateJob.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Certificate job with ID '{job_id}' not found."
        )
    return job


@router.get(
    "/jobs",
    response_model=List[JobResponse],
    summary="List all certificate generation jobs",
    description="Returns a paginated list of certificate generation jobs."
)
def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    jobs = db.query(CertificateJob).order_by(CertificateJob.created_at.desc()).offset(skip).limit(limit).all()
    return jobs


@router.get(
    "/certificates/{certificate_id}",
    response_model=CertificateRecordResponse,
    summary="Get single certificate details",
    description="Retrieves metadata for a specific recipient certificate record."
)
def get_certificate_details(certificate_id: str, db: Session = Depends(get_db)):
    record = db.query(CertificateRecord).filter(CertificateRecord.id == certificate_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Certificate record with ID '{certificate_id}' not found."
        )
    return record


@router.get(
    "/certificates/{certificate_id}/download",
    summary="Download individual certificate PDF",
    description="Downloads the generated PDF file for a specific certificate record."
)
def download_certificate(certificate_id: str, db: Session = Depends(get_db)):
    record = db.query(CertificateRecord).filter(CertificateRecord.id == certificate_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Certificate record with ID '{certificate_id}' not found."
        )

    if record.status == CertificateStatus.FAILED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Certificate generation failed for this recipient: {record.error_message}"
        )

    if not record.file_path or not os.path.exists(record.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate PDF file is not available on disk."
        )

    safe_recipient_filename = f"Certificate_{record.recipient_name.replace(' ', '_')}_{record.certificate_code}.pdf"
    return FileResponse(
        path=record.file_path,
        media_type="application/pdf",
        filename=safe_recipient_filename
    )


@router.get(
    "/jobs/{job_id}/download-zip",
    summary="Download all job certificates as ZIP archive",
    description="Packages all successfully generated PDF certificates for a job into a downloadable ZIP archive."
)
def download_job_zip(job_id: str, db: Session = Depends(get_db)):
    job = db.query(CertificateJob).filter(CertificateJob.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{job_id}' not found."
        )

    successful_records = db.query(CertificateRecord).filter(
        CertificateRecord.job_id == job_id,
        CertificateRecord.status == CertificateStatus.SUCCESS.value
    ).all()

    if not successful_records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No successfully generated certificates found for this job."
        )

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rec in successful_records:
            if rec.file_path and os.path.exists(rec.file_path):
                filename = f"{rec.recipient_name.replace(' ', '_')}_{rec.certificate_code}.pdf"
                zf.write(rec.file_path, arcname=filename)

    zip_buffer.seek(0)
    zip_filename = f"Certificates_Job_{job_id[:8]}.zip"

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={zip_filename}"}
    )
