// Maximo Risk Assessment Generator — Frontend JS

const API_BASE = '/api';

let currentReportId = null;
let allReports      = [];
let lastWorkOrderId = null;
let previewModal;

// Translation dictionaries
const translations = {
    en: {
        report_id: "Report ID",
        work_order: "Work Order",
        generated: "Generated",
        wo_status: "WO Status",
        work_order_details: "Work Order Details",
        work_order_number: "Work Order #",
        description: "Description",
        location: "Location",
        equipment: "Equipment",
        priority: "Priority",
        status: "Status",
        assigned_to: "Assigned To",
        identified_hazards: "Identified Hazards",
        hazard: "Hazard",
        controls: "Controls",
        required_ppe: "Required PPE",
        emergency_contacts: "Emergency Contacts",
        supervisor: "Supervisor",
        safety_officer: "Safety Officer",
        emergency_services: "Emergency Services",
        additional_notes: "Additional Notes",
        field: "Field",
        value: "Value"
    },
    fr: {
        report_id: "ID du Rapport",
        work_order: "Ordre de Travail",
        generated: "Généré",
        wo_status: "Statut OT",
        work_order_details: "Détails de l'Ordre de Travail",
        work_order_number: "N° d'Ordre de Travail",
        description: "Description",
        location: "Lieu",
        equipment: "Équipement",
        priority: "Priorité",
        status: "Statut",
        assigned_to: "Assigné à",
        identified_hazards: "Dangers Identifiés",
        hazard: "Danger",
        controls: "Mesures de Contrôle",
        required_ppe: "EPI Requis",
        emergency_contacts: "Contacts d'Urgence",
        supervisor: "Superviseur",
        safety_officer: "Responsable Sécurité",
        emergency_services: "Services d'Urgence",
        additional_notes: "Notes Supplémentaires",
        field: "Champ",
        value: "Valeur"
    },
    hi: {
        report_id: "रिपोर्ट आईडी",
        work_order: "वर्क ऑर्डर",
        generated: "उत्पन्न",
        wo_status: "WO स्थिति",
        work_order_details: "वर्क ऑर्डर विवरण",
        work_order_number: "वर्क ऑर्डर नंबर",
        description: "विवरण",
        location: "स्थान",
        equipment: "उपकरण",
        priority: "प्राथमिकता",
        status: "स्थिति",
        assigned_to: "को सौंपा गया",
        identified_hazards: "पहचाने गए खतरे",
        hazard: "खतरा",
        controls: "नियंत्रण उपाय",
        required_ppe: "आवश्यक PPE",
        emergency_contacts: "आपातकालीन संपर्क",
        supervisor: "पर्यवेक्षक",
        safety_officer: "सुरक्षा अधिकारी",
        emergency_services: "आपातकालीन सेवाएं",
        additional_notes: "अतिरिक्त नोट्स",
        field: "फील्ड",
        value: "मान"
    }
};

function t(key, lang = 'en') {
    return translations[lang]?.[key] || translations.en[key] || key;
}

// ── Boot ─────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    previewModal = new bootstrap.Modal(document.getElementById('reportPreviewModal'));

    // Nav links
    document.querySelectorAll('.sidebar-link').forEach(link => {
        link.addEventListener('click', e => { e.preventDefault(); switchView(link.dataset.view); });
    });

    // Mobile sidebar
    const sidebar  = document.getElementById('sidebar');
    const overlay  = document.getElementById('sidebarOverlay');
    document.getElementById('sidebarToggle')?.addEventListener('click', () => {
        sidebar.classList.toggle('open');
        overlay?.classList.toggle('visible');
    });
    overlay?.addEventListener('click', () => {
        sidebar.classList.remove('open');
        overlay.classList.remove('visible');
    });

    // Form
    document.getElementById('jhaForm').addEventListener('submit', onFormSubmit);

    // Result card buttons
    document.getElementById('downloadPdfBtn').addEventListener('click', () => downloadReport(currentReportId));
    document.getElementById('viewReportBtn').addEventListener('click',  () => previewReport(currentReportId));

    // History
    document.getElementById('searchHistory').addEventListener('input', filterHistory);
    document.getElementById('refreshHistoryBtn').addEventListener('click', loadHistory);

    // Modal download
    document.getElementById('modalDownloadPdfBtn').addEventListener('click', () => downloadReport(currentReportId));

    // Keyboard: Ctrl/Cmd+Enter submits
    document.addEventListener('keydown', e => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            const btn = document.getElementById('generateBtn');
            if (!btn.disabled) document.getElementById('jhaForm').dispatchEvent(new Event('submit'));
        }
    });

    // Load badge count silently
    loadHistory(true);
});

// ── View switching ────────────────────────────────────────
function switchView(view) {
    document.querySelectorAll('.sidebar-link').forEach(l =>
        l.classList.toggle('active', l.dataset.view === view));

    document.getElementById('panelGenerate').classList.toggle('d-none', view !== 'generate');
    document.getElementById('panelHistory').classList.toggle('d-none',  view !== 'history');

    // Close mobile sidebar
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('sidebarOverlay')?.classList.remove('visible');

    if (view === 'history') loadHistory();
}

// ── Form ─────────────────────────────────────────────────
async function onFormSubmit(e) {
    e.preventDefault();
    const wo = document.getElementById('workOrderId').value.trim();
    const lang = document.getElementById('reportLanguage').value;
    if (!wo) { notify('Please enter a work order number.', 'warning'); return; }
    if (!/^[A-Z0-9\-_]{1,50}$/i.test(wo)) { notify('Invalid work order number format.', 'error'); return; }
    await generateReport(wo, lang);
}

async function generateReport(wo, lang = 'en') {
    setLoading(true);
    clearNotification();
    document.getElementById('resultContainer').classList.add('d-none');
    setProgress(true, 0, 'Initializing…');
    lastWorkOrderId = wo;

    try {
        setProgress(true, 20, 'Fetching work order from Maximo…');
        await sleep(400);
        setProgress(true, 45, 'Analysing hazards with AI…');

        const res = await fetch(`${API_BASE}/jha/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                work_order_id: wo,
                language: lang
            })
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `Server error ${res.status}`);
        }

        setProgress(true, 80, 'Building report…');
        await sleep(300);

        const data = await res.json();
        setProgress(true, 100, 'Complete!');
        await sleep(350);

        renderReport(data);
        notify('JHA report generated successfully!', 'success');
        loadHistory(true);

    } catch (err) {
        console.error(err);
        notifyWithRetry(err.message || 'Failed to generate report. Please try again.');
    } finally {
        setLoading(false);
        setProgress(false);
    }
}

// ── Render report result ──────────────────────────────────
function renderReport(data) {
    const report   = data.report || data;
    const reportId = data.report_id || report.report_id;
    currentReportId = reportId;
    const wo = report.work_order || {};
    const lang = report.language || 'en';

    // Meta cards
    let html = `<div class="report-meta-grid">
        <div class="report-meta-card">
            <div class="report-meta-label">${t('report_id', lang)}</div>
            <div class="report-meta-value" style="font-size:.8rem;font-family:monospace">${x(reportId)}</div>
        </div>
        <div class="report-meta-card">
            <div class="report-meta-label">${t('work_order', lang)}</div>
            <div class="report-meta-value">${x(report.work_order_id)}</div>
        </div>
        <div class="report-meta-card">
            <div class="report-meta-label">${t('generated', lang)}</div>
            <div class="report-meta-value" style="font-size:.875rem">${fmtDate(report.created_at)}</div>
        </div>
        <div class="report-meta-card">
            <div class="report-meta-label">${t('wo_status', lang)}</div>
            <div class="report-meta-value"><span class="status-chip">${x(wo.status || report.work_order?.status || 'N/A')}</span></div>
        </div>
    </div>`;

    // WO table
    if (wo && Object.keys(wo).length) {
        const rows = [
            [t('work_order_number', lang), wo.id],
            [t('description', lang),  wo.description],
            [t('location', lang),     wo.location],
            [t('equipment', lang),    wo.equipment],
            [t('priority', lang),     wo.priority],
            [t('status', lang),       wo.status],
            [t('assigned_to', lang),  wo.assigned_to],
        ];
        html += `<div class="section-heading"><i class="bi bi-clipboard-data"></i>${t('work_order_details', lang)}</div>
        <table class="wo-table">
            <thead><tr><th>${t('field', lang)}</th><th>${t('value', lang)}</th></tr></thead>
            <tbody>${rows.map(([l,v]) =>
                `<tr><td class="td-label">${x(l)}</td><td>${x(v||'N/A')}</td></tr>`).join('')}
            </tbody>
        </table>`;
    }

    // Hazards
    if (report.hazards?.length) {
        html += `<div class="section-heading"><i class="bi bi-exclamation-triangle"></i>${t('identified_hazards', lang)} (${report.hazards.length})</div>`;
        report.hazards.forEach((h, i) => {
            const rl = (h.risk_level || 'medium').toLowerCase();
            html += `<div class="hazard-card risk-${rl}">
                <div class="hazard-top">
                    <strong>${t('hazard', lang)} ${i + 1}</strong>
                    <span class="risk-tag risk-${rl}">${x(h.risk_level)}</span>
                </div>
                <div class="hazard-body">
                    <p><strong>${t('description', lang)}:</strong> ${x(h.description)}</p>
                    <p><strong>${t('controls', lang)}:</strong> ${x((h.controls||[]).join(', ')||'N/A')}</p>
                    <p><strong>${t('required_ppe', lang)}:</strong> ${x((h.ppe||[]).join(', ')||'Standard PPE')}</p>
                </div>
            </div>`;
        });
    }

    // Emergency contacts
    const ec = report.emergency_contacts || {};
    const contacts = [
        [t('supervisor', lang),         ec.supervisor],
        [t('safety_officer', lang),     ec.safety_officer],
        [t('emergency_services', lang), ec.emergency],
    ].filter(([,v]) => v);

    if (contacts.length) {
        html += `<div class="section-heading"><i class="bi bi-telephone"></i>${t('emergency_contacts', lang)}</div>
        <table class="wo-table">
            <tbody>${contacts.map(([l,v]) =>
                `<tr><td class="td-label">${x(l)}</td><td>${x(v)}</td></tr>`).join('')}
            </tbody>
        </table>`;
    }

    // Additional notes
    if (report.additional_notes) {
        html += `<div class="section-heading"><i class="bi bi-sticky"></i>${t('additional_notes', lang)}</div>
        <p style="font-size:.9rem;line-height:1.7;margin-bottom:1rem">${x(report.additional_notes)}</p>`;
    }

    document.getElementById('reportContent').innerHTML = html;
    const rc = document.getElementById('resultContainer');
    rc.classList.remove('d-none');
    rc.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ── History ───────────────────────────────────────────────
async function loadHistory(badgeOnly = false) {
    try {
        const res = await fetch(`${API_BASE}/jha/history?limit=50`);
        if (!res.ok) throw new Error(res.status);
        const data = await res.json();
        allReports = (data.reports || data || []).sort(
            (a, b) => new Date(b.created_at) - new Date(a.created_at)
        );

        // Badge
        const badge = document.getElementById('reportCountBadge');
        if (allReports.length) {
            badge.textContent = allReports.length;
            badge.style.display = '';
        } else {
            badge.style.display = 'none';
        }

        if (!badgeOnly) renderTable(allReports);
    } catch (err) {
        console.error('History error:', err);
        if (!badgeOnly) {
            document.getElementById('historyContainer').innerHTML =
                `<div class="empty-state">
                    <i class="bi bi-wifi-off empty-icon"></i>
                    <p class="empty-title">Could not load reports</p>
                    <p class="empty-desc">Check your connection and click Refresh.</p>
                </div>`;
        }
    }
}

function renderTable(reports) {
    const el = document.getElementById('historyContainer');
    if (!reports.length) {
        el.innerHTML = `<div class="empty-state">
            <i class="bi bi-inbox empty-icon"></i>
            <p class="empty-title">No reports found</p>
            <p class="empty-desc">Generated reports will appear here.</p>
        </div>`;
        return;
    }

    const rows = reports.map(r => {
        const hi = (r.hazards||[]).filter(h => (h.risk_level||'').toUpperCase() === 'HIGH').length;
        const hiBadge = hi > 0
            ? `<span style="margin-left:.5rem;font-size:.7rem;background:var(--red-10);color:var(--red-60);padding:.1rem .45rem;border-radius:10px;font-weight:700">${hi} High</span>`
            : '';
        return `<tr>
            <td class="td-mono">${x(r.report_id||'—')}</td>
            <td><strong>${x(r.work_order_id||'—')}</strong></td>
            <td style="white-space:nowrap">${fmtDate(r.created_at)}</td>
            <td><span class="status-chip">${x(r.work_order?.status || 'N/A')}</span>${hiBadge}</td>
            <td>
                <div class="td-actions">
                    <button class="cds-btn cds-btn-ghost cds-btn-sm"
                            onclick="previewReport('${xa(r.report_id)}')">
                        <i class="bi bi-eye me-1"></i>View PDF
                    </button>
                    <button class="cds-btn cds-btn-primary cds-btn-sm"
                            onclick="downloadReport('${xa(r.report_id)}')">
                        <i class="bi bi-download me-1"></i>Download
                    </button>
                </div>
            </td>
        </tr>`;
    }).join('');

    el.innerHTML = `<div class="reports-table-wrap">
        <table class="reports-table">
            <thead>
                <tr>
                    <th>Report ID</th>
                    <th>Work Order</th>
                    <th>Generated</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>${rows}</tbody>
        </table>
    </div>`;
}

function filterHistory() {
    const q = document.getElementById('searchHistory').value.toLowerCase();
    const f = allReports.filter(r =>
        (r.report_id||'').toLowerCase().includes(q) ||
        (r.work_order_id||'').toLowerCase().includes(q) ||
        (r.work_order?.description||'').toLowerCase().includes(q)
    );
    renderTable(f);
}

// ── PDF ───────────────────────────────────────────────────
function previewReport(reportId) {
    if (!reportId) return;
    currentReportId = reportId;
    document.getElementById('reportPreviewFrame').src = `${API_BASE}/jha/${reportId}/view`;
    previewModal.show();
}

async function downloadReport(reportId) {
    if (!reportId) { notify('No report available.', 'warning'); return; }
    try {
        const res = await fetch(`${API_BASE}/jha/${reportId}/download?format=pdf`);
        if (!res.ok) throw new Error('Download failed');
        const blob = await res.blob();
        const url  = URL.createObjectURL(blob);
        const a    = Object.assign(document.createElement('a'), {
            href: url, download: `JHA_Report_${reportId}.pdf`
        });
        document.body.appendChild(a);
        a.click();
        URL.revokeObjectURL(url);
        a.remove();
        notify('PDF downloaded successfully.', 'success');
    } catch {
        notify('Failed to download report.', 'error');
    }
}

// ── UI helpers ────────────────────────────────────────────
function setLoading(on) {
    const btn = document.getElementById('generateBtn');
    btn.disabled = on;
    document.getElementById('btnText').classList.toggle('d-none', on);
    document.getElementById('btnSpinner').classList.toggle('d-none', !on);
}

function setProgress(show, pct = 0, msg = '') {
    const el = document.getElementById('progressContainer');
    el.classList.toggle('d-none', !show);
    if (show) {
        document.getElementById('progressBar').style.width = `${pct}%`;
        document.getElementById('progressStatus').textContent = msg;
    }
}

function notify(msg, type = 'success') {
    const icons = { success: 'check-circle-fill', error: 'exclamation-triangle-fill',
                    warning: 'exclamation-circle-fill' };
    const cls   = { success: 'cds-notification-success', error: 'cds-notification-error',
                    warning: 'cds-notification-warning' };
    document.getElementById('alertContainer').innerHTML =
        `<div class="cds-notification ${cls[type]||cls.success}">
            <i class="bi bi-${icons[type]||icons.success} cds-notification-icon"></i>
            <span>${x(msg)}</span>
        </div>`;
}

function notifyWithRetry(msg) {
    document.getElementById('alertContainer').innerHTML =
        `<div class="cds-notification cds-notification-error">
            <i class="bi bi-exclamation-triangle-fill cds-notification-icon"></i>
            <div class="notification-retry">
                <span>${x(msg)}</span>
                <button class="cds-btn cds-btn-neutral cds-btn-sm" onclick="retry()">
                    <i class="bi bi-arrow-clockwise me-1"></i>Retry
                </button>
            </div>
        </div>`;
}

function clearNotification() {
    document.getElementById('alertContainer').innerHTML = '';
}

function retry() {
    if (lastWorkOrderId) {
        document.getElementById('workOrderId').value = lastWorkOrderId;
        generateReport(lastWorkOrderId);
    }
}

// ── Utils ─────────────────────────────────────────────────
function fmtDate(ds) {
    if (!ds) return 'N/A';
    return new Date(ds).toLocaleString(undefined, {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
}

function x(s) {
    return String(s ?? '').replace(/[&<>"']/g, c =>
        ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function xa(s) { return String(s ?? '').replace(/'/g, "\\'"); }

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// Made with Bob
