import os
from pathlib import Path
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas


def generate_certificate_pdf(
    output_path: str,
    recipient_name: str,
    title: str,
    issuer_name: str,
    issue_date: str,
    certificate_code: str
) -> str:
    """
    Generates a professional PDF certificate using ReportLab canvas.
    Returns the absolute path to the generated PDF.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Landscape Letter size: 11 x 8.5 inches (792 x 612 points)
    page_width, page_height = landscape(letter)

    c = canvas.Canvas(str(path), pagesize=landscape(letter))
    c.setTitle(f"Certificate - {recipient_name}")

    # 1. Background Fill (Very light cream/off-white)
    c.setFillColor(colors.HexColor("#FAFAFC"))
    c.rect(0, 0, page_width, page_height, fill=1, stroke=0)

    # 2. Outer Decorative Frame (Navy Blue)
    c.setStrokeColor(colors.HexColor("#1E293B"))  # Slate navy
    c.setLineWidth(6)
    c.rect(20, 20, page_width - 40, page_height - 40)

    # 3. Inner Gold Accent Border
    c.setStrokeColor(colors.HexColor("#D97706"))  # Amber gold
    c.setLineWidth(2)
    c.rect(28, 28, page_width - 56, page_height - 56)

    # Corner Accents (Gold Rectangles)
    corner_size = 12
    c.setFillColor(colors.HexColor("#D97706"))
    c.rect(28, 28, corner_size, corner_size, fill=1, stroke=0)
    c.rect(page_width - 28 - corner_size, 28, corner_size, corner_size, fill=1, stroke=0)
    c.rect(28, page_height - 28 - corner_size, corner_size, corner_size, fill=1, stroke=0)
    c.rect(page_width - 28 - corner_size, page_height - 28 - corner_size, corner_size, corner_size, fill=1, stroke=0)

    # 4. Header: Issuer Organization
    c.setFillColor(colors.HexColor("#475569"))
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(page_width / 2.0, page_height - 80, issuer_name.upper())

    # 5. Main Certificate Title
    c.setFillColor(colors.HexColor("#0F172A"))
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(page_width / 2.0, page_height - 135, "CERTIFICATE OF ACHIEVEMENT")

    # Decorative Line Under Title
    c.setStrokeColor(colors.HexColor("#CBD5E1"))
    c.setLineWidth(1)
    c.line(page_width / 2.0 - 150, page_height - 150, page_width / 2.0 + 150, page_height - 150)

    # 6. Presentation Text
    c.setFillColor(colors.HexColor("#64748B"))
    c.setFont("Helvetica-Oblique", 14)
    c.drawCentredString(page_width / 2.0, page_height - 190, "This is proudly presented to")

    # 7. Recipient Name
    c.setFillColor(colors.HexColor("#1E3A8A"))  # Deep Royal Blue
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(page_width / 2.0, page_height - 240, recipient_name)

    # Line under recipient name
    c.setStrokeColor(colors.HexColor("#D97706"))
    c.setLineWidth(2)
    c.line(page_width / 2.0 - 180, page_height - 250, page_width / 2.0 + 180, page_height - 250)

    # 8. Course / Achievement Text
    c.setFillColor(colors.HexColor("#475569"))
    c.setFont("Helvetica", 14)
    c.drawCentredString(page_width / 2.0, page_height - 290, "for successfully completing")

    c.setFillColor(colors.HexColor("#0F172A"))
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(page_width / 2.0, page_height - 325, title)

    # 9. Date and Signature Footer
    # Date Block (Left)
    c.setFillColor(colors.HexColor("#475569"))
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(180, 110, issue_date)
    c.setStrokeColor(colors.HexColor("#94A3B8"))
    c.setLineWidth(1)
    c.line(100, 125, 260, 125)
    c.setFont("Helvetica", 10)
    c.drawCentredString(180, 95, "Date of Issuance")

    # Badge / Seal in Center
    c.setFillColor(colors.HexColor("#F59E0B"))
    c.circle(page_width / 2.0, 120, 30, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#FFFFFF"))
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(page_width / 2.0, 123, "VERIFIED")
    c.drawCentredString(page_width / 2.0, 111, "OFFICIAL")

    # Signature Block (Right)
    c.setFillColor(colors.HexColor("#1E3A8A"))
    c.setFont("Helvetica-BoldOblique", 16)
    c.drawCentredString(page_width - 180, 135, issuer_name)
    c.setStrokeColor(colors.HexColor("#94A3B8"))
    c.setLineWidth(1)
    c.line(page_width - 260, 125, page_width - 100, 125)
    c.setFillColor(colors.HexColor("#475569"))
    c.setFont("Helvetica", 10)
    c.drawCentredString(page_width - 180, 95, "Authorized Signature")

    # 10. Bottom Certificate Verification Code
    c.setFillColor(colors.HexColor("#94A3B8"))
    c.setFont("Helvetica", 9)
    c.drawCentredString(page_width / 2.0, 45, f"Certificate ID: {certificate_code}")

    c.showPage()
    c.save()

    return str(path.resolve())
