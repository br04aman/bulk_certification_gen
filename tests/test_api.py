from app.services.job_processor import process_certificate_job


def test_create_generation_job(client):
    payload = {
        "title": "Backend Engineering Bootcamp",
        "issuer_name": "Tech Corp",
        "issue_date": "2026-10-08",
        "recipients": [
            {"name": "Alice Johnson", "email": "alice@example.com"},
            {"name": "Bob Smith", "email": "bob@example.com"}
        ]
    }
    response = client.post("/api/v1/certificates/generate", json=payload)
    assert response.status_code == 202
    data = response.json()
    assert "id" in data
    assert data["title"] == "Backend Engineering Bootcamp"
    assert data["total_recipients"] == 2
    assert data["status"] == "PENDING"
    assert len(data["records"]) == 2


def test_job_status_and_background_processing(client, db_session):
    payload = {
        "title": "Cloud Computing Summit",
        "issuer_name": "Cloud Org",
        "issue_date": "2026-10-08",
        "recipients": [
            {"name": "Charlie Brown", "email": "charlie@example.com"},
            {"name": "Diana Prince", "email": "diana@example.com"}
        ]
    }
    res = client.post("/api/v1/certificates/generate", json=payload)
    assert res.status_code == 202
    job_id = res.json()["id"]

    # Trigger background worker explicitly with test session for deterministic testing
    process_certificate_job(job_id, db=db_session)

    # Poll status endpoint
    status_res = client.get(f"/api/v1/jobs/{job_id}")
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["status"] == "COMPLETED"
    assert status_data["success_count"] == 2
    assert status_data["failed_count"] == 0
    assert len(status_data["records"]) == 2
    for record in status_data["records"]:
        assert record["status"] == "SUCCESS"
        assert record["file_path"] is not None


def test_handling_individual_certificate_failure(client, db_session):
    payload = {
        "title": "Data Science Fundamentals",
        "issuer_name": "Data Academy",
        "issue_date": "2026-10-08",
        "recipients": [
            {"name": "Eve Adams", "email": "eve@example.com"},
            {"name": "Frank TRIGGER_FAILURE", "email": "frank@example.com"}  # Triggers failure
        ]
    }
    res = client.post("/api/v1/certificates/generate", json=payload)
    assert res.status_code == 202
    job_id = res.json()["id"]

    process_certificate_job(job_id, db=db_session)

    status_res = client.get(f"/api/v1/jobs/{job_id}")
    assert status_res.status_code == 200
    data = status_res.json()

    assert data["status"] == "PARTIALLY_COMPLETED"
    assert data["success_count"] == 1
    assert data["failed_count"] == 1

    records = {r["recipient_name"]: r for r in data["records"]}
    assert records["Eve Adams"]["status"] == "SUCCESS"
    assert records["Frank TRIGGER_FAILURE"]["status"] == "FAILED"
    assert "Simulated certificate generation engine failure" in records["Frank TRIGGER_FAILURE"]["error_message"]


def test_retrieving_generated_certificate_pdf(client, db_session):
    payload = {
        "title": "Cybersecurity Essentials",
        "issuer_name": "Security Labs",
        "issue_date": "2026-10-08",
        "recipients": [
            {"name": "Grace Hopper", "email": "grace@example.com"}
        ]
    }
    res = client.post("/api/v1/certificates/generate", json=payload)
    job_id = res.json()["id"]

    process_certificate_job(job_id, db=db_session)

    status_res = client.get(f"/api/v1/jobs/{job_id}")
    cert_id = status_res.json()["records"][0]["id"]

    # Download single certificate PDF
    dl_res = client.get(f"/api/v1/certificates/{cert_id}/download")
    assert dl_res.status_code == 200
    assert dl_res.headers["content-type"] == "application/pdf"
    assert dl_res.content.startswith(b"%PDF-")


def test_downloading_all_certificates_as_zip(client, db_session):
    payload = {
        "title": "AI Masterclass",
        "issuer_name": "AI Institute",
        "issue_date": "2026-10-08",
        "recipients": [
            {"name": "Hank Pym", "email": "hank@example.com"},
            {"name": "Iris West", "email": "iris@example.com"}
        ]
    }
    res = client.post("/api/v1/certificates/generate", json=payload)
    job_id = res.json()["id"]

    process_certificate_job(job_id, db=db_session)

    zip_res = client.get(f"/api/v1/jobs/{job_id}/download-zip")
    assert zip_res.status_code == 200
    assert zip_res.headers["content-type"] == "application/zip"
    assert len(zip_res.content) > 0


def test_non_existent_job_and_certificate(client):
    res = client.get("/api/v1/jobs/invalid-job-id")
    assert res.status_code == 404

    res = client.get("/api/v1/certificates/invalid-cert-id/download")
    assert res.status_code == 404


def test_serve_dashboard_frontend(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "Certify" in res.text

