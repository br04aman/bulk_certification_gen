document.addEventListener("DOMContentLoaded", () => {
    // --- State Variables ---
    let recipientRows = [
        { name: "Alice Johnson", email: "alice@example.com" },
        { name: "Bob Smith", email: "bob@example.com" }
    ];
    let currentJobId = null;
    let pollInterval = null;

    // --- DOM Elements ---
    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");
    const tbodyRecipients = document.getElementById("recipients-tbody");
    const btnAddRow = document.getElementById("btn-add-row");
    const btnDemoData = document.getElementById("btn-demo-data");
    const recipientBadge = document.getElementById("recipient-count-badge");
    const btnModeTable = document.getElementById("btn-mode-table");
    const btnModeCsv = document.getElementById("btn-mode-csv");
    const modeTableContainer = document.getElementById("mode-table-container");
    const modeCsvContainer = document.getElementById("mode-csv-container");
    const jobForm = document.getElementById("job-form");
    
    // Live Preview elements
    const inputTitle = document.getElementById("title");
    const inputIssuer = document.getElementById("issuer_name");
    const previewTitle = document.getElementById("preview-title");
    const previewIssuer = document.getElementById("preview-issuer");
    const previewName = document.getElementById("preview-name");

    // Tracker elements
    const trackerJobInput = document.getElementById("tracker-job-id-input");
    const btnFetchJob = document.getElementById("btn-fetch-job");
    const trackerEmptyState = document.getElementById("tracker-empty-state");
    const trackerDetails = document.getElementById("tracker-details");
    const jobDetailId = document.getElementById("job-detail-id");
    const jobDetailTitle = document.getElementById("job-detail-title");
    const jobDetailStatusBadge = document.getElementById("job-detail-status-badge");
    const jobDetailProgressText = document.getElementById("job-detail-progress-text");
    const jobProgressBar = document.getElementById("job-progress-bar");
    const btnDownloadZip = document.getElementById("btn-download-zip");
    const trackerRecordsTbody = document.getElementById("tracker-records-tbody");

    // History elements
    const historyJobsTbody = document.getElementById("history-jobs-tbody");
    const btnRefreshHistory = document.getElementById("btn-refresh-history");

    // --- Tab Switching ---
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTab = btn.getAttribute("data-tab");
            tabBtns.forEach(b => b.classList.remove("active"));
            tabContents.forEach(c => c.classList.remove("active"));
            btn.classList.add("active");
            document.getElementById(targetTab).classList.add("active");

            if (targetTab === "job-history") {
                loadJobHistory();
            }
        });
    });

    // --- Dynamic Recipient Table Rendering ---
    function renderRecipientRows() {
        tbodyRecipients.innerHTML = "";
        recipientRows.forEach((rec, index) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>
                    <input type="text" class="form-input rec-name" value="${escapeHtml(rec.name)}" placeholder="Recipient Name" data-index="${index}">
                </td>
                <td>
                    <input type="email" class="form-input rec-email" value="${escapeHtml(rec.email)}" placeholder="email@example.com" data-index="${index}">
                </td>
                <td style="text-align: center;">
                    <button type="button" class="btn btn-danger-ghost btn-remove-row" data-index="${index}">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                    </button>
                </td>
            `;
            tbodyRecipients.appendChild(tr);
        });

        recipientBadge.textContent = `${recipientRows.length} Recipient${recipientRows.length === 1 ? '' : 's'}`;
        if (recipientRows.length > 0) {
            previewName.textContent = recipientRows[0].name.toUpperCase() || "RECIPIENT NAME";
        }
        attachRowInputListeners();
    }

    function attachRowInputListeners() {
        document.querySelectorAll(".rec-name").forEach(input => {
            input.addEventListener("input", (e) => {
                const idx = e.target.getAttribute("data-index");
                recipientRows[idx].name = e.target.value;
                if (idx == 0) {
                    previewName.textContent = e.target.value.toUpperCase() || "RECIPIENT NAME";
                }
            });
        });

        document.querySelectorAll(".rec-email").forEach(input => {
            input.addEventListener("input", (e) => {
                const idx = e.target.getAttribute("data-index");
                recipientRows[idx].email = e.target.value;
            });
        });

        document.querySelectorAll(".btn-remove-row").forEach(btn => {
            btn.addEventListener("click", (e) => {
                const idx = btn.getAttribute("data-index");
                if (recipientRows.length <= 1) {
                    showToast("Must have at least 1 recipient.", "error");
                    return;
                }
                recipientRows.splice(idx, 1);
                renderRecipientRows();
            });
        });
    }

    btnAddRow.addEventListener("click", () => {
        recipientRows.push({ name: "", email: "" });
        renderRecipientRows();
    });

    btnDemoData.addEventListener("click", () => {
        recipientRows = [
            { name: "Alice Johnson", email: "alice@example.com" },
            { name: "Bob Smith", email: "bob@example.com" },
            { name: "Carol Danvers", email: "carol@example.com" },
            { name: "David Miller", email: "david@example.com" }
        ];
        inputTitle.value = "Full Stack Web Development Mastery 2026";
        inputIssuer.value = "Global Tech Institute";
        document.getElementById("issue_date").value = "October 8, 2026";
        
        previewTitle.textContent = inputTitle.value;
        previewIssuer.textContent = inputIssuer.value.toUpperCase();
        renderRecipientRows();
        showToast("Demo data loaded into form!", "success");
    });

    // Toggle Input Modes
    btnModeTable.addEventListener("click", () => {
        btnModeTable.classList.add("active");
        btnModeCsv.classList.remove("active");
        modeTableContainer.classList.remove("hidden");
        modeCsvContainer.classList.add("hidden");
    });

    btnModeCsv.addEventListener("click", () => {
        btnModeCsv.classList.add("active");
        btnModeTable.classList.remove("active");
        modeCsvContainer.classList.remove("hidden");
        modeTableContainer.classList.add("hidden");
    });

    // Live Certificate Mockup updates
    inputTitle.addEventListener("input", (e) => {
        previewTitle.textContent = e.target.value || "Full Stack Web Development Workshop";
    });

    inputIssuer.addEventListener("input", (e) => {
        previewIssuer.textContent = (e.target.value || "Global Tech Institute").toUpperCase();
    });

    // --- Submit Bulk Job ---
    jobForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        let recipients = [];
        if (btnModeTable.classList.contains("active")) {
            recipients = recipientRows.filter(r => r.name.trim() !== "" && r.email.trim() !== "");
        } else {
            const rawCsv = document.getElementById("raw-csv-input").value.trim();
            if (!rawCsv) {
                showToast("Please enter CSV or JSON text.", "error");
                return;
            }
            try {
                if (rawCsv.startsWith("[")) {
                    recipients = JSON.parse(rawCsv);
                } else {
                    const lines = rawCsv.split("\n");
                    lines.forEach(line => {
                        const parts = line.split(",");
                        if (parts.length >= 2) {
                            recipients.push({ name: parts[0].trim(), email: parts[1].trim() });
                        }
                    });
                }
            } catch (err) {
                showToast("Failed to parse CSV/JSON input.", "error");
                return;
            }
        }

        if (recipients.length === 0) {
            showToast("Please provide at least 1 valid recipient.", "error");
            return;
        }

        const payload = {
            title: inputTitle.value.trim(),
            issuer_name: inputIssuer.value.trim(),
            issue_date: document.getElementById("issue_date").value.trim(),
            recipients: recipients
        };

        const submitBtn = document.getElementById("submit-job-btn");
        submitBtn.disabled = true;
        submitBtn.innerHTML = `Generating...`;

        try {
            const res = await fetch("/api/v1/certificates/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || "Job creation failed.");
            }

            const job = await res.json();
            showToast(`Bulk job created! Job ID: ${job.id}`, "success");

            // Switch to tracker tab
            currentJobId = job.id;
            trackerJobInput.value = job.id;
            document.querySelector('[data-tab="job-tracker"]').click();
            startJobPolling(job.id);

        } catch (err) {
            showToast(err.message, "error");
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
                Generate Bulk Certificates
            `;
        }
    });

    // --- Job Tracker & Status Polling ---
    btnFetchJob.addEventListener("click", () => {
        const jobId = trackerJobInput.value.trim();
        if (!jobId) {
            showToast("Please enter a Job ID.", "error");
            return;
        }
        currentJobId = jobId;
        startJobPolling(jobId);
    });

    function startJobPolling(jobId) {
        if (pollInterval) clearInterval(pollInterval);
        fetchJobDetails(jobId);
        pollInterval = setInterval(() => {
            fetchJobDetails(jobId);
        }, 2000);
    }

    async function fetchJobDetails(jobId) {
        try {
            const res = await fetch(`/api/v1/jobs/${jobId}`);
            if (!res.ok) {
                throw new Error("Job not found.");
            }
            const job = await res.json();
            renderJobTracker(job);

            if (job.status === "COMPLETED" || job.status === "PARTIALLY_COMPLETED" || job.status === "FAILED") {
                if (pollInterval) clearInterval(pollInterval);
            }
        } catch (err) {
            if (pollInterval) clearInterval(pollInterval);
            showToast(err.message, "error");
        }
    }

    function renderJobTracker(job) {
        trackerEmptyState.classList.add("hidden");
        trackerDetails.classList.remove("hidden");

        jobDetailId.textContent = job.id.substring(0, 18) + "...";
        jobDetailTitle.textContent = job.title;

        // Status Badge
        jobDetailStatusBadge.className = "badge " + getStatusBadgeClass(job.status);
        jobDetailStatusBadge.textContent = job.status;

        // Progress Calculations
        const processed = job.success_count + job.failed_count;
        const total = job.total_recipients;
        const percent = total > 0 ? Math.round((processed / total) * 100) : 0;

        jobDetailProgressText.textContent = `${processed} / ${total} (${percent}%)`;
        jobProgressBar.style.width = `${percent}%`;

        // ZIP Download button state
        if (job.success_count > 0) {
            btnDownloadZip.disabled = false;
            btnDownloadZip.onclick = () => {
                window.open(`/api/v1/jobs/${job.id}/download-zip`, "_blank");
            };
        } else {
            btnDownloadZip.disabled = true;
        }

        // Render Record Rows
        trackerRecordsTbody.innerHTML = "";
        job.records.forEach(rec => {
            const tr = document.createElement("tr");
            const statusBadge = `<span class="badge ${getStatusBadgeClass(rec.status)}">${rec.status}</span>`;
            
            let actionBtn = "";
            if (rec.status === "SUCCESS") {
                actionBtn = `
                    <a href="/api/v1/certificates/${rec.id}/download" target="_blank" class="btn btn-outline btn-sm">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                        Download PDF
                    </a>
                `;
            } else if (rec.status === "FAILED") {
                actionBtn = `<span class="form-help" style="color: var(--status-danger);">${escapeHtml(rec.error_message || 'Failed')}</span>`;
            } else {
                actionBtn = `<span class="form-help">Processing...</span>`;
            }

            tr.innerHTML = `
                <td style="font-weight: 600;">${escapeHtml(rec.recipient_name)}</td>
                <td>${escapeHtml(rec.recipient_email)}</td>
                <td class="font-mono">${rec.certificate_code}</td>
                <td>${statusBadge}</td>
                <td>${actionBtn}</td>
            `;
            trackerRecordsTbody.appendChild(tr);
        });
    }

    // --- Job History ---
    btnRefreshHistory.addEventListener("click", loadJobHistory);

    async function loadJobHistory() {
        try {
            const res = await fetch("/api/v1/jobs?limit=20");
            if (!res.ok) return;
            const jobs = await res.json();

            historyJobsTbody.innerHTML = "";
            if (jobs.length === 0) {
                historyJobsTbody.innerHTML = `<tr><td colspan="9" style="text-align: center; color: var(--text-muted);">No jobs submitted yet.</td></tr>`;
                return;
            }

            jobs.forEach(j => {
                const tr = document.createElement("tr");
                const createdDate = new Date(j.created_at).toLocaleString();
                tr.innerHTML = `
                    <td class="font-mono">${j.id.substring(0, 8)}...</td>
                    <td style="font-weight: 600;">${escapeHtml(j.title)}</td>
                    <td>${escapeHtml(j.issuer_name)}</td>
                    <td>${j.total_recipients}</td>
                    <td style="color: var(--status-success); font-weight: 600;">${j.success_count}</td>
                    <td style="color: var(--status-danger); font-weight: 600;">${j.failed_count}</td>
                    <td><span class="badge ${getStatusBadgeClass(j.status)}">${j.status}</span></td>
                    <td style="font-size: 0.8rem; color: var(--text-muted);">${createdDate}</td>
                    <td>
                        <button class="btn btn-outline btn-sm btn-inspect-job" data-id="${j.id}">Inspect</button>
                    </td>
                `;
                historyJobsTbody.appendChild(tr);
            });

            document.querySelectorAll(".btn-inspect-job").forEach(b => {
                b.addEventListener("click", (e) => {
                    const id = b.getAttribute("data-id");
                    trackerJobInput.value = id;
                    document.querySelector('[data-tab="job-tracker"]').click();
                    startJobPolling(id);
                });
            });

        } catch (err) {
            console.error("Failed to load job history", err);
        }
    }

    // --- Helper Utilities ---
    function getStatusBadgeClass(status) {
        switch (status) {
            case "COMPLETED": case "SUCCESS": return "badge-success";
            case "PARTIALLY_COMPLETED": case "WARNING": return "badge-warning";
            case "FAILED": return "badge-danger";
            default: return "badge-pending";
        }
    }

    function showToast(message, type = "info") {
        const toast = document.getElementById("toast");
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.classList.remove("hidden");
        setTimeout(() => {
            toast.classList.add("hidden");
        }, 4000);
    }

    function escapeHtml(str) {
        if (!str) return "";
        return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
    }

    // Initialize initial render
    renderRecipientRows();
});
