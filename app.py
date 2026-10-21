import io
import json
import time
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Import the existing agents and evaluation components
from agents.hr_manager_agent import hr_manager_agent
from evaluation.benchmark_dataset import create_benchmark_dataset
from evaluation.evaluator import evaluate_validation
from evaluation.metrics import calculate_metrics

# Page configuration
st.set_page_config(
    page_title="HR Agentic Onboarding Platform",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for polished, modern look + Hide Deploy Button
st.markdown(
    """
    <style>
    /* Hide Streamlit Deploy button and toolbar deploy controls */
    .stDeployButton,
    [data-testid="stDeployButton"],
    [data-testid="stToolbarActions"],
    header [data-testid="stToolbar"] .stDeployButton {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        width: 0 !important;
        height: 0 !important;
    }

    /* Main container and font styling */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Gradient header banner */
    .hero-header {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #1e3a8a 100%);
        padding: 1.8rem 2.2rem;
        border-radius: 16px;
        color: #ffffff;
        margin-bottom: 1.8rem;
        box-shadow: 0 10px 25px -5px rgba(30, 27, 75, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #c7d2fe;
        margin-top: 0.5rem;
        font-weight: 400;
        line-height: 1.4;
    }

    /* Agent status cards */
    .agent-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 12px;
        padding: 1.25rem 1.4rem;
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .agent-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
    }
    .agent-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
    }
    .agent-name {
        font-weight: 700;
        font-size: 1.1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Status Badges */
    .badge {
        display: inline-block;
        padding: 0.3rem 0.75rem;
        font-size: 0.78rem;
        font-weight: 700;
        border-radius: 9999px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-ready {
        background-color: #065f46;
        color: #34d399;
        border: 1px solid #059669;
    }
    .badge-valid {
        background-color: #065f46;
        color: #34d399;
        border: 1px solid #059669;
    }
    .badge-incomplete {
        background-color: #7f1d1d;
        color: #f87171;
        border: 1px solid #dc2626;
    }
    .badge-pending {
        background-color: #1e3a8a;
        color: #60a5fa;
        border: 1px solid #2563eb;
    }
    .badge-planned {
        background-color: #581c87;
        color: #c084fc;
        border: 1px solid #9333ea;
    }
    .badge-timing {
        background: rgba(255, 255, 255, 0.08);
        color: #94a3b8;
        font-size: 0.75rem;
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        font-family: monospace;
    }

    /* Big Overall status banner */
    .status-banner-ready {
        background: linear-gradient(135deg, #064e3b 0%, #065f46 100%);
        color: #ecfdf5;
        border: 1px solid #10b981;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.2);
    }
    .status-banner-incomplete {
        background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%);
        color: #fef2f2;
        border: 1px solid #ef4444;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(239, 68, 68, 0.2);
    }

    /* Stat KPI Card */
    .kpi-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        text-align: center;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 800;
        margin-top: 0.25rem;
    }
    .kpi-label {
        font-size: 0.82rem;
        color: #94a3b8;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header Section
st.markdown(
    """
    <div class="hero-header">
        <h1 class="hero-title">👔 HR Employee Onboarding Multi-Agent System</h1>
        <p class="hero-subtitle">
            Autonomous multi-agent orchestration for employee verification, credentials assessment,
            IT provisioning, orientation scheduling, and quantitative benchmark evaluation.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar Navigation
with st.sidebar:
    st.image(
        "https://api.iconify.design/lucide:bot.svg?color=%236366f1&width=48",
        width=48,
    )
    st.title("System Control")
    st.markdown("Select an operation mode:")

    app_mode = st.radio(
        "Navigation",
        [
            "🚀 Full Onboarding Orchestrator",
            "📊 Benchmark & Evaluation",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.subheader("Active Agents")
    st.markdown(
        """
        - 👑 **HR Manager Agent** (Coordinator)
        - 👤 **Employee Info Agent**
        - 📄 **Document Verification Agent**
        - 💻 **IT Setup Agent**
        - 🎯 **Orientation Agent**
        """
    )

    st.markdown("---")
    st.caption("Engine: Streamlit + Python Multi-Agent Architecture")


# ==============================================================================
# MODE 1: FULL ONBOARDING ORCHESTRATOR
# ==============================================================================
if app_mode == "🚀 Full Onboarding Orchestrator":
    st.subheader("🚀 HR Manager Agent: Full Onboarding Pipeline")
    st.write(
        "Configure employee profile and submitted credentials below, then trigger the autonomous multi-agent pipeline."
    )

    # Preset Quick Loaders
    st.markdown("**Quick Preset Profiles:**")
    col_pre1, col_pre2, col_pre3, col_pre4 = st.columns(4)

    preset_name = None
    if col_pre1.button("✅ Complete Profile (Rahul)", use_container_width=True):
        preset_name = "rahul_valid"
    if col_pre2.button("⚠️ Missing Document (Priya)", use_container_width=True):
        preset_name = "priya_missing_doc"
    if col_pre3.button("❌ Missing Fields (Alex)", use_container_width=True):
        preset_name = "alex_missing_field"
    if col_pre4.button("⚡ Reset Form", use_container_width=True):
        preset_name = "reset"

    # Manage defaults based on presets
    if "form_name" not in st.session_state or preset_name == "reset":
        st.session_state["form_name"] = "Rahul Sharma"
        st.session_state["form_emp_id"] = "EMP-101"
        st.session_state["form_dept"] = "Engineering"
        st.session_state["form_role"] = "Senior Software Engineer"
        st.session_state["form_doc_id"] = True
        st.session_state["form_doc_edu"] = True
        st.session_state["form_doc_offer"] = True

    if preset_name == "rahul_valid":
        st.session_state["form_name"] = "Rahul Sharma"
        st.session_state["form_emp_id"] = "EMP-101"
        st.session_state["form_dept"] = "Engineering"
        st.session_state["form_role"] = "Senior Software Engineer"
        st.session_state["form_doc_id"] = True
        st.session_state["form_doc_edu"] = True
        st.session_state["form_doc_offer"] = True
    elif preset_name == "priya_missing_doc":
        st.session_state["form_name"] = "Priya Nair"
        st.session_state["form_emp_id"] = "EMP-102"
        st.session_state["form_dept"] = "Human Resources"
        st.session_state["form_role"] = "Talent Specialist"
        st.session_state["form_doc_id"] = True
        st.session_state["form_doc_edu"] = False  # Missing education cert
        st.session_state["form_doc_offer"] = True
    elif preset_name == "alex_missing_field":
        st.session_state["form_name"] = "Alex Morgan"
        st.session_state["form_emp_id"] = ""  # Missing ID
        st.session_state["form_dept"] = "Product"
        st.session_state["form_role"] = ""  # Missing Role
        st.session_state["form_doc_id"] = True
        st.session_state["form_doc_edu"] = True
        st.session_state["form_doc_offer"] = True

    col_form1, col_form2 = st.columns([1, 1], gap="large")

    with col_form1:
        st.markdown("### 1. Employee Details")
        emp_name = st.text_input("Full Name", value=st.session_state.get("form_name", ""))
        emp_id = st.text_input("Employee ID", value=st.session_state.get("form_emp_id", ""))
        emp_dept = st.text_input("Department", value=st.session_state.get("form_dept", ""))
        emp_role = st.text_input("Job Role", value=st.session_state.get("form_role", ""))

    with col_form2:
        st.markdown("### 2. Document Submission Status")
        st.write("Toggle verification for incoming employee onboarding documentation:")
        doc_id = st.checkbox(
            "🆔 Identity Document (Passport / National ID)",
            value=st.session_state.get("form_doc_id", True),
        )
        doc_edu = st.checkbox(
            "🎓 Educational Certificates (Degree / Transcripts)",
            value=st.session_state.get("form_doc_edu", True),
        )
        doc_offer = st.checkbox(
            "✍️ Signed Offer Letter",
            value=st.session_state.get("form_doc_offer", True),
        )

        st.caption(
            "Note: All 3 documents are strictly mandatory for compliance clearance."
        )

    st.markdown("---")
    run_onboarding_btn = st.button(
        "⚡ Run HR Manager Agent Pipeline",
        type="primary",
        use_container_width=True,
    )

    if run_onboarding_btn:
        employee_data = {
            "name": emp_name.strip(),
            "employee_id": emp_id.strip(),
            "department": emp_dept.strip(),
            "role": emp_role.strip(),
        }

        documents_data = {
            "identity_document": doc_id,
            "educational_certificate": doc_edu,
            "signed_offer_letter": doc_offer,
        }

        with st.spinner("🤖 Coordinating Sub-Agents..."):
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                report = hr_manager_agent(employee_data, documents_data)

        st.session_state["last_report"] = report

        # Status Banner
        is_ready = report["overall_status"] == "READY FOR ONBOARDING"
        if is_ready:
            st.markdown(
                f"""
                <div class="status-banner-ready">
                    <h2 style="margin: 0; font-size: 1.8rem; font-weight: 800;">
                        ✅ OVERALL STATUS: READY FOR ONBOARDING
                    </h2>
                    <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.9;">
                        Candidate <strong>{report['employee']['name'] or 'Employee'}</strong> passed all validation checks. IT and orientation pipelines scheduled.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="status-banner-incomplete">
                    <h2 style="margin: 0; font-size: 1.8rem; font-weight: 800;">
                        ⚠️ OVERALL STATUS: INCOMPLETE
                    </h2>
                    <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.9;">
                        Candidate profile cannot proceed. Required employee fields or compliance documents are missing.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # 4 Sub-Agent Result Cards in 2x2 Grid
        c1, c2 = st.columns(2)

        with c1:
            # Agent 1: Employee Information
            info_res = report["information"]
            info_status = info_res["status"]
            info_badge_class = "badge-valid" if info_status == "VALID" else "badge-incomplete"
            info_timing = report["agent_timings_ms"].get("employee_information_agent_ms", 0)

            st.markdown(
                f"""
                <div class="agent-card">
                    <div class="agent-header">
                        <div class="agent-name">👤 Employee Information Agent</div>
                        <div>
                            <span class="badge {info_badge_class}">{info_status}</span>
                            <span class="badge-timing">{info_timing:.3f} ms</span>
                        </div>
                    </div>
                    <div style="font-size: 0.92rem;">
                        <strong>Name:</strong> {report['employee']['name'] or '<em style="color:#f87171">Missing</em>'}<br/>
                        <strong>ID:</strong> {report['employee']['employee_id'] or '<em style="color:#f87171">Missing</em>'}<br/>
                        <strong>Department:</strong> {report['employee']['department'] or '<em style="color:#f87171">Missing</em>'}<br/>
                        <strong>Role:</strong> {report['employee']['role'] or '<em style="color:#f87171">Missing</em>'}<br/>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if info_res["missing_fields"]:
                st.error(f"Missing Fields: {', '.join(info_res['missing_fields'])}")
            else:
                st.success("All required profile fields validated successfully.")

        with c2:
            # Agent 2: Document Verification
            doc_res = report["documents"]
            doc_status = doc_res["status"]
            doc_badge_class = "badge-ready" if doc_status == "READY" else "badge-incomplete"
            doc_timing = report["agent_timings_ms"].get("document_verification_agent_ms", 0)

            st.markdown(
                f"""
                <div class="agent-card">
                    <div class="agent-header">
                        <div class="agent-name">📄 Document Verification Agent</div>
                        <div>
                            <span class="badge {doc_badge_class}">{doc_status}</span>
                            <span class="badge-timing">{doc_timing:.3f} ms</span>
                        </div>
                    </div>
                    <div style="font-size: 0.92rem;">
                        <strong>Submitted:</strong> {len(doc_res['submitted_documents'])} / 3 documents<br/>
                        <strong>Missing:</strong> {len(doc_res['missing_documents'])} documents
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if doc_res["missing_documents"]:
                formatted_missing = [d.replace('_', ' ').title() for d in doc_res['missing_documents']]
                st.error(f"Missing Documents: {', '.join(formatted_missing)}")
            else:
                st.success("All required compliance documents verified.")

        c3, c4 = st.columns(2)

        with c3:
            # Agent 3: IT Setup
            it_res = report["it_setup"]
            it_timing = report["agent_timings_ms"].get("it_setup_agent_ms", 0)

            st.markdown(
                f"""
                <div class="agent-card">
                    <div class="agent-header">
                        <div class="agent-name">💻 IT Setup Agent</div>
                        <div>
                            <span class="badge badge-pending">{it_res['status']}</span>
                            <span class="badge-timing">{it_timing:.3f} ms</span>
                        </div>
                    </div>
                    <div style="font-size: 0.92rem;">
                        <strong>Employee Target:</strong> {it_res['employee'] or 'Unknown'}<br/>
                        <strong>Provisioning Checklist:</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            for task, status in it_res["tasks"].items():
                st.markdown(f"- ⏳ **{task}**: `{status}`")

        with c4:
            # Agent 4: Orientation Agent
            ori_res = report["orientation"]
            ori_timing = report["agent_timings_ms"].get("orientation_agent_ms", 0)

            st.markdown(
                f"""
                <div class="agent-card">
                    <div class="agent-header">
                        <div class="agent-name">🎯 Orientation Agent</div>
                        <div>
                            <span class="badge badge-planned">{ori_res['status']}</span>
                            <span class="badge-timing">{ori_timing:.3f} ms</span>
                        </div>
                    </div>
                    <div style="font-size: 0.92rem;">
                        <strong>Employee Target:</strong> {ori_res['employee'] or 'Unknown'}<br/>
                        <strong>Planned Modules:</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            for act, status in ori_res["activities"].items():
                st.markdown(f"- 📅 **{act}**: `{status}`")

        # Performance & Timing Breakdown
        st.markdown("### ⏱️ Agent Execution Latency Breakdown")
        timings = report["agent_timings_ms"]
        df_timings = pd.DataFrame(
            [
                {"Agent": "Employee Info", "Latency (ms)": timings.get("employee_information_agent_ms", 0)},
                {"Agent": "Document Verification", "Latency (ms)": timings.get("document_verification_agent_ms", 0)},
                {"Agent": "IT Setup", "Latency (ms)": timings.get("it_setup_agent_ms", 0)},
                {"Agent": "Orientation", "Latency (ms)": timings.get("orientation_agent_ms", 0)},
            ]
        )

        fig_lat = px.bar(
            df_timings,
            x="Agent",
            y="Latency (ms)",
            text="Latency (ms)",
            color="Agent",
            title="Execution Latency per Sub-Agent (ms)",
            color_discrete_sequence=["#6366f1", "#10b981", "#3b82f6", "#a855f7"],
        )
        fig_lat.update_traces(texttemplate="%{text:.4f} ms", textposition="outside")
        fig_lat.update_layout(showlegend=False, height=340, margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig_lat, use_container_width=True)

        # Download Report Options
        st.markdown("### 📥 Export Final Onboarding Report")
        col_dl1, col_dl2 = st.columns(2)

        json_str = json.dumps(report, indent=4)
        col_dl1.download_button(
            label="📄 Download Report as JSON",
            data=json_str,
            file_name=f"onboarding_report_{report['employee']['employee_id'] or 'candidate'}.json",
            mime="application/json",
            use_container_width=True,
        )

        text_summary = f"""=============================================
EMPLOYEE ONBOARDING REPORT
=============================================
Employee Name: {report['employee']['name']}
Employee ID: {report['employee']['employee_id']}
Department: {report['employee']['department']}
Role: {report['employee']['role']}

Information Status: {report['information']['status']}
Document Status: {report['documents']['status']}
Missing Documents: {', '.join(report['documents']['missing_documents'])}
Overall Status: {report['overall_status']}
=============================================
"""
        col_dl2.download_button(
            label="📝 Download Summary as Text",
            data=text_summary,
            file_name=f"onboarding_summary_{report['employee']['employee_id'] or 'candidate'}.txt",
            mime="text/plain",
            use_container_width=True,
        )


# ==============================================================================
# MODE 2: BENCHMARK & EVALUATION
# ==============================================================================
elif app_mode == "📊 Benchmark & Evaluation":
    st.subheader("📊 Multi-Agent Benchmark & Evaluation Suite")
    st.write(
        "Execute automated regression testing across all 10 benchmark test cases (TC01-TC10) "
        "to measure accuracy, failure rate, latency percentiles, and agent throughput."
    )

    if st.button("🚀 Run Full Benchmark Suite", type="primary", use_container_width=True):
        progress_bar = st.progress(0, text="Initializing benchmark dataset...")

        cases = create_benchmark_dataset()
        results = []
        benchmark_start = time.perf_counter()

        for idx, case in enumerate(cases):
            progress_bar.progress(
                (idx + 1) / len(cases),
                text=f"Evaluating Test Case {case['id']}: {case['description']}...",
            )

            case_start = time.perf_counter()
            try:
                with redirect_stdout(io.StringIO()):
                    report = hr_manager_agent(case["employee"], case["documents"])

                latency_ms = (time.perf_counter() - case_start) * 1000
                actual_status = report["overall_status"]
                passed = actual_status == case["expected_status"]
                correct_checks, total_checks = evaluate_validation(report, case)

                results.append(
                    {
                        "test_id": case["id"],
                        "description": case["description"],
                        "expected_status": case["expected_status"],
                        "actual_status": actual_status,
                        "passed": passed,
                        "latency_ms": latency_ms,
                        "error": "",
                        "validation_checks": total_checks,
                        "correct_checks": correct_checks,
                        "agent_timings_ms": report.get("agent_timings_ms", {}),
                    }
                )
            except Exception as exc:
                latency_ms = (time.perf_counter() - case_start) * 1000
                results.append(
                    {
                        "test_id": case["id"],
                        "description": case["description"],
                        "expected_status": case["expected_status"],
                        "actual_status": "EXECUTION ERROR",
                        "passed": False,
                        "latency_ms": latency_ms,
                        "error": str(exc),
                        "validation_checks": 0,
                        "correct_checks": 0,
                        "agent_timings_ms": {},
                    }
                )

        total_time_seconds = time.perf_counter() - benchmark_start
        metrics = calculate_metrics(results, total_time_seconds)

        # Aggregate timings
        agent_totals = {}
        for r in results:
            for ag, dur in r["agent_timings_ms"].items():
                agent_totals.setdefault(ag, []).append(dur)

        agent_avg_timings = {
            ag: round(sum(times) / len(times), 4) for ag, times in agent_totals.items() if times
        }

        # Cache summary into session state
        st.session_state["benchmark_summary"] = {
            "metrics": metrics,
            "results": results,
            "agent_avg_timings": agent_avg_timings,
            "total_time_seconds": total_time_seconds,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        progress_bar.empty()
        st.success(f"Benchmark finished in {total_time_seconds:.4f} seconds!")

    # Check if we have cached benchmark results or load existing reports
    summary_data = st.session_state.get("benchmark_summary")
    if not summary_data:
        # Check if saved file exists
        saved_json = Path(__file__).resolve().parent / "reports" / "evaluation_summary.json"
        if saved_json.exists():
            try:
                with open(saved_json, "r", encoding="utf-8") as f:
                    cached_file = json.load(f)
                    summary_data = {
                        "metrics": cached_file["metrics"],
                        "results": cached_file["individual_results"],
                        "agent_avg_timings": cached_file.get("average_agent_latency_ms", {}),
                        "timestamp": cached_file.get("timestamp", "Pre-computed"),
                    }
            except Exception:
                pass

    if summary_data:
        metrics = summary_data["metrics"]
        results = summary_data["results"]
        agent_avg = summary_data["agent_avg_timings"]

        st.markdown("### 📈 Benchmark Executive KPI Summary")
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">Success Rate</div>
                    <div class="kpi-value" style="color: #34d399;">{metrics['success_rate_percent']}%</div>
                    <div style="font-size: 0.8rem; color:#94a3b8;">{metrics['passed_tests']} / {metrics['total_tests']} Passed</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">Validation Accuracy</div>
                    <div class="kpi-value" style="color: #60a5fa;">{metrics['validation_accuracy_percent']}%</div>
                    <div style="font-size: 0.8rem; color:#94a3b8;">{metrics.get('correct_validation_checks', 0)} / {metrics.get('total_validation_checks', 0)} Checks</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">Avg Latency</div>
                    <div class="kpi-value" style="color: #c084fc;">{metrics['average_latency_ms']} <span style="font-size:1rem;">ms</span></div>
                    <div style="font-size: 0.8rem; color:#94a3b8;">P50: {metrics['p50_latency_ms']} ms</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col4:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">P95 Latency</div>
                    <div class="kpi-value" style="color: #f59e0b;">{metrics['p95_latency_ms']} <span style="font-size:1rem;">ms</span></div>
                    <div style="font-size: 0.8rem; color:#94a3b8;">Max: {metrics['maximum_latency_ms']} ms</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col5:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">Throughput</div>
                    <div class="kpi-value" style="color: #38bdf8;">{metrics['throughput_requests_per_second']}</div>
                    <div style="font-size: 0.8rem; color:#94a3b8;">Req / Second</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # Visual Analytics
        c_chart1, c_chart2 = st.columns(2)

        with c_chart1:
            df_cases = pd.DataFrame(results)
            df_cases["status_flag"] = df_cases["passed"].apply(lambda p: "PASS" if p else "FAIL")
            fig_cases = px.bar(
                df_cases,
                x="test_id",
                y="latency_ms",
                color="status_flag",
                hover_data=["description", "expected_status", "actual_status"],
                title="Test Case Latency & Pass/Fail Status",
                color_discrete_map={"PASS": "#10b981", "FAIL": "#ef4444"},
                labels={"test_id": "Test Case ID", "latency_ms": "Latency (ms)", "status_flag": "Result"},
            )
            fig_cases.update_layout(height=350, margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig_cases, use_container_width=True)

        with c_chart2:
            if agent_avg:
                df_agent_avg = pd.DataFrame(
                    [{"Agent": k.replace("_agent_ms", "").replace("_", " ").title(), "Avg Latency (ms)": v} for k, v in agent_avg.items()]
                )
                fig_agent_avg = px.bar(
                    df_agent_avg,
                    x="Agent",
                    y="Avg Latency (ms)",
                    color="Agent",
                    text="Avg Latency (ms)",
                    title="Average Execution Latency per Sub-Agent",
                    color_discrete_sequence=["#6366f1", "#10b981", "#3b82f6", "#a855f7"],
                )
                fig_agent_avg.update_traces(texttemplate="%{text:.4f} ms", textposition="outside")
                fig_agent_avg.update_layout(showlegend=False, height=350, margin=dict(t=40, b=20, l=20, r=20))
                st.plotly_chart(fig_agent_avg, use_container_width=True)

        # Test Case Table
        st.markdown("### 📋 Test Case Evaluation Log")
        display_df = pd.DataFrame(
            [
                {
                    "Test ID": r["test_id"],
                    "Description": r["description"],
                    "Expected": r["expected_status"],
                    "Actual": r["actual_status"],
                    "Result": "✅ PASS" if r["passed"] else "❌ FAIL",
                    "Latency (ms)": round(r["latency_ms"], 4),
                    "Checks Passed": f"{r.get('correct_checks', 0)}/{r.get('validation_checks', 0)}",
                }
                for r in results
            ]
        )
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Export CSV and JSON buttons
        st.markdown("### 📥 Export Benchmark Reports")
        col_exp1, col_exp2 = st.columns(2)

        csv_buffer = io.StringIO()
        pd.DataFrame(results).to_csv(csv_buffer, index=False)
        col_exp1.download_button(
            label="📊 Download Results (CSV)",
            data=csv_buffer.getvalue(),
            file_name="benchmark_results.csv",
            mime="text/csv",
            use_container_width=True,
        )

        full_json_str = json.dumps(summary_data, indent=4)
        col_exp2.download_button(
            label="📁 Download Full Evaluation Summary (JSON)",
            data=full_json_str,
            file_name="evaluation_summary.json",
            mime="application/json",
            use_container_width=True,
        )
    else:
        st.info("Click 'Run Full Benchmark Suite' above to start testing.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 1rem 0;">
        HR Multi-Agent Onboarding & Evaluation Engine | Built with Streamlit, Plotly & Python
    </div>
    """,
    unsafe_allow_html=True,
)
