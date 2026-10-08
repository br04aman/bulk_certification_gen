# Bulk Certificate Generator Backend API & Web Dashboard

A high-performance, resilient, and scalable backend service and interactive web dashboard built in Python (FastAPI & SQLAlchemy) for generating event/course certificates in bulk from recipient lists using predefined ReportLab PDF templates.

---

## 🌟 Key Features

- **Interactive Web Dashboard**: Accessible at `http://127.0.0.1:8000/` featuring a modern glassmorphism dark theme, live template preview, demo data loader, realtime progress tracking bar, and download center.
- **Bulk Generation API**: Accepts batch requests containing event metadata and recipient lists.
- **Asynchronous Background Processing**: Returns immediate `202 Accepted` response with non-blocking background PDF generation.
- **Fault-Isolated Execution**: Failures on individual recipients (e.g. invalid name/email or generator errors) log error details and do not halt processing for valid recipients.
- **Progress Tracking**: Realtime metrics (`PENDING`, `PROCESSING`, `COMPLETED`, `PARTIALLY_COMPLETED`, `FAILED`) with detailed error logs per recipient.
- **PDF Certificate & Bulk ZIP Export**: Download individual certificates by ID or download all successfully generated certificates in a single `.zip` archive.
- **Vector PDF Generator**: High-resolution, professionally styled landscape certificates generated via ReportLab with unique Certificate Verification Codes (`CERT-2026-XXXXXX`).

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **FastAPI**: Modern, fast web framework with built-in OpenAPI & Swagger documentation.
- **SQLAlchemy 2.0**: Relational ORM (default: SQLite file/in-memory, configurable to PostgreSQL/MySQL via `DATABASE_URL`).
- **Pydantic V2**: Strict data validation & schema serialization.
- **ReportLab**: Vector PDF canvas rendering engine.
- **HTML5 / CSS3 / Vanilla JS**: Frontend web dashboard.
- **Pytest & HTTPX**: Comprehensive automated testing.

---

## 📁 Project Structure

```
bulk_certf_gen/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application factory & static file mounting
│   ├── config.py               # App configuration & storage paths
│   ├── database.py             # SQLAlchemy engine & session setup
│   ├── models.py               # ORM Database Models (CertificateJob, CertificateRecord)
│   ├── schemas.py              # Pydantic schemas for request & response validation
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pdf_generator.py    # ReportLab PDF template generator
│   │   └── job_processor.py    # Asynchronous worker with fault-isolation loop
│   ├── api/
│   │   └── routes.py           # API routes (Generate job, Check status, Download PDF/ZIP)
│   └── static/
│       ├── index.html          # Interactive Web Dashboard UI
│       ├── style.css           # Glassmorphism dark mode stylesheet
│       ├── app.js              # Frontend client & polling controller
│       └── img/                # Dashboard graphics & logo assets
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures & isolated DB setup
│   ├── test_api.py             # Integration tests for API endpoints & Web UI
│   ├── test_validation.py      # Input schema validation unit tests
│   └── test_pdf_generator.py   # PDF rendering unit tests
├── storage/                    # Output directory for generated PDF files & database
├── requirements.txt            # Project dependencies
└── README.md                   # Setup, execution & API documentation
```

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
- Python 3.10 or higher installed on your system.
- `pip` package manager.

### 2. Installation & Environment Setup

Navigate to the project root directory and install dependencies:

```bash
pip install -r requirements.txt
```

---

## 💻 How to Run the Application

Start the development server using **Uvicorn**:

```bash
uvicorn app.main:app --reload --port 8000
```

Once running, access the following URLs in your browser:

| Interface / Endpoint | URL | Description |
| :--- | :--- | :--- |
| 🎨 **Web Dashboard UI** | **`http://127.0.0.1:8000/`** | Interactive UI to create jobs, load demo data, track progress & download certificates |
| 📖 **Interactive Swagger Docs** | **`http://127.0.0.1:8000/docs`** | Test API endpoints directly in browser |
| 📚 **ReDoc API Documentation** | **`http://127.0.0.1:8000/redoc`** | Alternative structured API reference |
| 💚 **Health Check** | **`http://127.0.0.1:8000/health`** | Server health status endpoint |

---

## 🧪 How to Run Tests

Run the complete automated test suite using `pytest`:

```bash
pytest -v
```

### Test Coverage Highlights:
- `test_create_generation_job`: Validates bulk job creation, HTTP 202 status, and database entry.
- `test_input_validation`: Tests field validation rules for empty lists, invalid emails, and blank inputs.
- `test_generate_certificate_pdf_success`: Tests PDF vector canvas generation on disk.
- `test_job_status_and_background_processing`: Verifies background worker status progression from `PENDING` to `COMPLETED`.
- `test_handling_individual_certificate_failure`: Confirms isolated failure handling (`PARTIALLY_COMPLETED`) where failing recipients record error traces without affecting valid ones.
- `test_retrieving_generated_certificate_pdf`: Verifies single PDF downloading.
- `test_downloading_all_certificates_as_zip`: Verifies downloading all certificates in a ZIP archive.
- `test_serve_dashboard_frontend`: Verifies serving the HTML web dashboard on root route `GET /`.

---

## 📡 API Usage Examples

### 1. Submit a Bulk Certificate Generation Request

**`POST /api/v1/certificates/generate`**

**cURL Command:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/certificates/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Full Stack Web Development Workshop",
    "issuer_name": "Tech Academy Org",
    "issue_date": "October 8, 2026",
    "recipients": [
      { "name": "Alice Johnson", "email": "alice@example.com" },
      { "name": "Bob Smith", "email": "bob@example.com" }
    ]
  }'
```

**Response (HTTP 202 Accepted):**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
  "title": "Full Stack Web Development Workshop",
  "issuer_name": "Tech Academy Org",
  "issue_date": "October 8, 2026",
  "status": "PENDING",
  "total_recipients": 2,
  "success_count": 0,
  "failed_count": 0,
  "created_at": "2026-10-08T22:15:00.000000",
  "completed_at": null,
  "records": [
    {
      "id": "rec-111",
      "job_id": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
      "recipient_name": "Alice Johnson",
      "recipient_email": "alice@example.com",
      "status": "PENDING",
      "certificate_code": "CERT-2026-A1B2C3D4",
      "file_path": null,
      "error_message": null,
      "created_at": "2026-10-08T22:15:00.000000"
    }
  ]
}
```

---

### 2. Check Job Progress & Status

**`GET /api/v1/jobs/{job_id}`**

**cURL Command:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/jobs/a1b2c3d4-e5f6-7890-abcd-1234567890ab"
```

**Response:**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
  "title": "Full Stack Web Development Workshop",
  "issuer_name": "Tech Academy Org",
  "issue_date": "October 8, 2026",
  "status": "COMPLETED",
  "total_recipients": 2,
  "success_count": 2,
  "failed_count": 0,
  "created_at": "2026-10-08T22:15:00.000000",
  "completed_at": "2026-10-08T22:15:02.000000",
  "records": [
    {
      "id": "rec-111",
      "recipient_name": "Alice Johnson",
      "recipient_email": "alice@example.com",
      "status": "SUCCESS",
      "certificate_code": "CERT-2026-A1B2C3D4",
      "file_path": ".../storage/certificates/a1b2c3d4.../rec-111.pdf"
    }
  ]
}
```

---

### 3. Retrieve & Download Certificates

#### Download Single Certificate PDF:
**`GET /api/v1/certificates/{certificate_id}/download`**
```bash
curl -O -J "http://127.0.0.1:8000/api/v1/certificates/rec-111/download"
```

#### Download All Job Certificates as a ZIP Archive:
**`GET /api/v1/jobs/{job_id}/download-zip`**
```bash
curl -O -J "http://127.0.0.1:8000/api/v1/jobs/a1b2c3d4-e5f6-7890-abcd-1234567890ab/download-zip"
```

---

## 🏛️ Architectural & Design Rationale

1. **Async Background Processing**:
   - Immediate HTTP 202 response prevents client HTTP timeout issues when requesting bulk certificate generation for large recipient lists.
   - FastAPI `BackgroundTasks` executes processing asynchronously out-of-the-box without requiring external message brokers (such as Redis or RabbitMQ) for setup and testing, while maintaining a clean architecture that can easily scale out to Celery if needed.

2. **Fault Isolation**:
   - Each recipient record is processed inside an isolated `try...except` block.
   - If rendering or validation fails for an individual recipient, the error detail is recorded under `error_message` for that record while execution immediately proceeds to generate certificates for all remaining valid recipients in the job.

3. **ReportLab PDF Generator**:
   - ReportLab generates crisp vector PDF documents directly in pure Python without depending on external C binary libraries (like Chromium, wkhtmltopdf, or GTK).
"# bulk_certification_gen"  
