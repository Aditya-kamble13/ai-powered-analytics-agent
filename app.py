import io
import xml.etree.ElementTree as ET
import pandas as pd
import plotly.express as px
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from advanced_monitor import AdvancedBusinessMonitor
from real_emailer import EmailAlertSystem
from ai_agent import GeminiBIAgent

# Page Configuration
st.set_page_config(
    page_title="AI Business Health & Generative BI Dashboard", page_icon="🤖", layout="wide"
)

# Helper Function: Parse XML File to Pandas DataFrame
def load_xml_data(uploaded_file):
    tree = ET.parse(uploaded_file)
    root = tree.getroot()

    all_records = []
    for child in root:
        record = {}
        for subchild in child:
            val = subchild.text
            if val is not None:
                try:
                    if "." in val:
                        val = float(val)
                    else:
                        val = int(val)
                except ValueError:
                    pass
            record[subchild.tag] = val
        all_records.append(record)

    return pd.DataFrame(all_records)

# Helper Function: Generate PDF Audit Report in Memory
def create_pdf_report(filename, issues, narrative):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Document Header
    story.append(Paragraph(f"<b>Executive Audit Report: {filename}</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    # Narrative Summary Section
    story.append(Paragraph("<b>AI Root-Cause Executive Summary:</b>", styles["Heading2"]))
    story.append(Paragraph(narrative, styles["BodyText"]))
    story.append(Spacer(1, 14))

    # Detailed Issue Log Section
    story.append(Paragraph("<b>Detailed System Issue Log:</b>", styles["Heading2"]))
    if issues:
        for idx, issue in enumerate(issues, 1):
            text = f"<b>{idx}. [{issue['type']}] {issue['issue']}</b>: {issue['detail']}"
            story.append(Paragraph(text, styles["BodyText"]))
            story.append(Spacer(1, 6))
    else:
        story.append(Paragraph("No anomalies or data integrity issues detected.", styles["BodyText"]))

    doc.build(story)
    buffer.seek(0)
    return buffer

# Title Header
st.title("🤖 Generative AI Business Health & Anomaly Agent")
st.markdown("Multi-format file ingestion (**CSV**, **XML**, **Excel**) powered by **Google Gemini AI** for root-cause analysis and natural language custom rule checks.")

# Sidebar - Configuration
st.sidebar.header("⚙️ Audit Configuration")
baseline_window = st.sidebar.slider("Baseline Window (Days)", 3, 14, 7)
threshold_pct = st.sidebar.slider("Metric Anomaly Sensitivity (%)", 5, 50, 15) / 100.0
recipient_email = st.sidebar.text_input("Alert Recipient Email", "manager@company.com")

# Initialize AI Agent
ai_agent = GeminiBIAgent()

# File Uploader
uploaded_file = st.file_uploader(
    "Upload Data File",
    type=["csv", "xml", "xlsx", "xls"],
    help="Support formats: .csv, .xml, .xlsx, .xls",
)

if uploaded_file is not None:
    filename = uploaded_file.name.lower()

    # Load Data
    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif filename.endswith(".xml"):
            df = load_xml_data(uploaded_file)
        elif filename.endswith(".xlsx") or filename.endswith(".xls"):
            df = pd.read_excel(uploaded_file)

        st.success(f"Successfully loaded **{uploaded_file.name}** ({len(df)} total rows).")

        # Raw Data Display Tab
        with st.expander("📄 View Uploaded Raw Data"):
            st.dataframe(df)

        # -------------------------------------------------------------
        # FEATURE 1: Natural Language Custom Audit Rule (Gemini Powered)
        # -------------------------------------------------------------
        st.markdown("---")
        st.subheader("💬 Ask AI Agent / Custom Rule Prompt")
        user_custom_rule = st.text_input(
            "Type a custom check in natural language:",
            placeholder="e.g., Flag any transaction amount over 50000 or check if West region has lower revenue",
        )

        if user_custom_rule:
            with st.spinner("🤖 Gemini AI is evaluating your custom prompt..."):
                sample_str = df.head(5).to_string()
                ai_rule_response = ai_agent.evaluate_custom_rule(sample_str, user_custom_rule)
                st.info(f"🧠 **AI Prompt Interpretation:**\n\n{ai_rule_response}")

        # -------------------------------------------------------------
        # FEATURE 2: Statistical Anomaly Detection Engine
        # -------------------------------------------------------------
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        metric_cols = [c for c in numeric_cols if c in ["Revenue", "Sales", "Amount"]]
        if not metric_cols and len(numeric_cols) > 0:
            metric_cols = [numeric_cols[0]]

        monitor = AdvancedBusinessMonitor(
            df,
            baseline_window=baseline_window,
            threshold_pct=threshold_pct,
        )
        detected_issues = monitor.run_all_checks(
            numeric_cols=numeric_cols, metric_cols=metric_cols
        )

        st.markdown("---")
        st.subheader("🔍 Automated Audit & AI Root-Cause Analysis")

        # Dynamic AI Root-Cause Narrative
        dataset_summary = f"Columns: {list(df.columns)}, Total Rows: {len(df)}"
        if detected_issues:
            with st.spinner("🤖 Generating AI Root-Cause Analysis using Gemini..."):
                narrative = ai_agent.explain_root_cause(dataset_summary, detected_issues)
        else:
            narrative = "All automated checks passed smoothly! Data integrity is intact with no statistical anomalies detected."

        # Display AI Narrative Card
        st.info(f"💡 **AI Executive Root-Cause Summary:**\n\n{narrative}")

        if detected_issues:
            st.warning(f"**{len(detected_issues)} System Issue(s) / Anomalies Detected!**")

            # Display Issues in Cards
            for issue in detected_issues:
                st.error(f"**[{issue['type']}] {issue['issue']}** — {issue['detail']}")

            st.markdown("---")

            # Generate PDF in Memory
            pdf_data = create_pdf_report(uploaded_file.name, detected_issues, narrative)

            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                st.info(f"Send automated anomaly summary to: **{recipient_email}**")

            # Action Button 1: Live Email with Attached PDF
            with col2:
                if st.button("📧 Send Email Alert", type="primary"):
                    emailer = EmailAlertSystem()
                    sent = emailer.send_alert_email(
                        recipient_email,
                        detected_issues,
                        uploaded_file.name,
                        pdf_buffer=pdf_data,
                    )
                    if sent:
                        st.success("Alert email with PDF report dispatched successfully!")
                    else:
                        st.error("Failed to send email. Check .env credentials.")

            # Action Button 2: Direct PDF Download
            with col3:
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_data,
                    file_name=f"Audit_Report_{uploaded_file.name}.pdf",
                    mime="application/pdf",
                )

        else:
            st.success("✅ All system checks passed!")

        # Interactive Visualization
        if "Date" in df.columns and len(numeric_cols) > 0:
            st.markdown("---")
            st.subheader("📈 Interactive Metric Trend Visualizer")
            selected_col = st.selectbox("Select Metric to Plot", numeric_cols)

            fig = px.line(
                df,
                x="Date",
                y=selected_col,
                title=f"{selected_col} Behavior Over Time",
                markers=True,
            )
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

else:
    st.info("👆 Please upload a CSV, XML, or Excel file to start the automated audit.")