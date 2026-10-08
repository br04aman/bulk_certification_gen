import os
import tempfile
from app.services.pdf_generator import generate_certificate_pdf


def test_generate_certificate_pdf_success():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_file = os.path.join(tmp_dir, "test_certificate.pdf")
        
        pdf_path = generate_certificate_pdf(
            output_path=output_file,
            recipient_name="John Doe",
            title="Advanced Machine Learning",
            issuer_name="AI Research Academy",
            issue_date="2026-10-08",
            certificate_code="CERT-2026-TEST1234"
        )

        assert os.path.exists(pdf_path)
        assert os.path.getsize(pdf_path) > 0

        # Read header bytes to confirm valid PDF format
        with open(pdf_path, "rb") as f:
            header = f.read(5)
            assert header == b"%PDF-"
