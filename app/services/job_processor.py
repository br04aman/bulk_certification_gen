from typing import Optional
import logging
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

from app.config import STORAGE_DIR
from app.database import SessionLocal
from app.models import CertificateJob, CertificateRecord, JobStatus, CertificateStatus
from app.services.pdf_generator import generate_certificate_pdf

logger = logging.getLogger(__name__)


def process_certificate_job(job_id: str, db: Optional[Session] = None) -> None:
    """
    Background worker function that processes all recipient records for a job.
    Provides fault isolation: failures on individual recipients are captured in error_message
    and do not halt processing of other valid recipients.
    """
    should_close_db = False
    if db is None:
        db = SessionLocal()
        should_close_db = True

    try:
        job: CertificateJob = db.query(CertificateJob).filter(CertificateJob.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found for background processing.")
            return

        job.status = JobStatus.PROCESSING.value
        db.commit()

        records = db.query(CertificateRecord).filter(CertificateRecord.job_id == job_id).all()
        job_dir = STORAGE_DIR / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        success_count = 0
        failed_count = 0

        for record in records:
            try:
                # 1. Recipient validation check
                if not record.recipient_name or not record.recipient_name.strip():
                    raise ValueError("Recipient name is blank or missing.")

                if not record.recipient_email or "@" not in record.recipient_email:
                    raise ValueError("Invalid recipient email address format.")

                # Special test hook: force error if recipient name contains 'TRIGGER_FAILURE'
                if "TRIGGER_FAILURE" in record.recipient_name:
                    raise RuntimeError("Simulated certificate generation engine failure.")

                # 2. PDF Generation
                filename = f"{record.id}.pdf"
                output_pdf_path = str(job_dir / filename)

                generated_path = generate_certificate_pdf(
                    output_path=output_pdf_path,
                    recipient_name=record.recipient_name,
                    title=job.title,
                    issuer_name=job.issuer_name,
                    issue_date=job.issue_date,
                    certificate_code=record.certificate_code
                )

                # 3. Update Record Success
                record.status = CertificateStatus.SUCCESS.value
                record.file_path = generated_path
                record.error_message = None
                record.generated_at = datetime.utcnow()
                success_count += 1

            except Exception as e:
                logger.warning(f"Failed to generate certificate for record {record.id}: {str(e)}")
                record.status = CertificateStatus.FAILED.value
                record.error_message = str(e)
                record.file_path = None
                failed_count += 1

            db.commit()

        # Update Final Job Status
        job.success_count = success_count
        job.failed_count = failed_count
        job.completed_at = datetime.utcnow()

        if success_count == job.total_recipients:
            job.status = JobStatus.COMPLETED.value
        elif failed_count == job.total_recipients:
            job.status = JobStatus.FAILED.value
        else:
            job.status = JobStatus.PARTIALLY_COMPLETED.value

        db.commit()
        logger.info(f"Finished job {job_id}: {success_count} succeeded, {failed_count} failed.")

    except Exception as exc:
        logger.error(f"Error executing bulk job processing for job {job_id}: {exc}")
        if 'job' in locals() and job:
            job.status = JobStatus.FAILED.value
            db.commit()
    finally:
        if should_close_db:
            db.close()

