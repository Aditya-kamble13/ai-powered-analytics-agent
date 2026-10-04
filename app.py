import os
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

# Local modules import
from ai_agent import ask_data_agent
from advanced_monitor import detect_anomalies
from logger_alert import log_alert
from real_emailer import send_alert_email
from report_generator import generate_pdf_report

load_dotenv()

st.set_page_config(
    page_title="AI Business Intelligence Agent",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI Business Intelligence & Anomaly Detection Agent")

# Sidebar
st.sidebar.header("📁 Data Source & Settings")
uploaded_file = st.sidebar.file_uploader("Upload Business Data (CSV, XLSX, XML)", type=["csv", "xlsx", "xml"])

st.sidebar.subheader("📧 Email Alert Settings")
enable_email = st.sidebar.checkbox("Enable Automated Email Alerts", value=False)
recipient_email = st.sidebar.text_input("Recipient Email", value="")

@st.cache_data
def load_data(file):
    ext = file.name.split(".")[-1].lower()
    if ext == "csv":
        return pd.read_csv(file)
    elif ext == "xlsx":
        return pd.read_excel(file)
    elif ext == "xml":
        return pd.read_xml(file)

if uploaded_file is not None:
    df = load_data(uploaded_file)
    st.sidebar.success(f"Loaded: {uploaded_file.name}")
else:
    st.info("👈 Please upload a dataset (CSV, Excel, or XML) from sidebar.")
    st.stop()

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Data & Anomalies", "💬 Ask AI Data Analyst", "📄 Export & Send PDF Report"])

# TAB 1: Data & Anomalies
with tab1:
    st.subheader("Data Preview")
    st.dataframe(df.head(10), use_container_width=True)

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    if numeric_cols:
        selected_col = st.selectbox("Select Numeric Metric for Anomaly Detection", numeric_cols)
        z_threshold = st.slider("Z-Score Threshold", 1.5, 4.0, 2.5, 0.1)

        anomalies_df = detect_anomalies(df, column=selected_col, threshold=z_threshold)

        if not anomalies_df.empty:
            st.error(f"⚠️ Detected {len(anomalies_df)} anomalies in `{selected_col}`!")
            st.dataframe(anomalies_df, use_container_width=True)
            
            fig = px.scatter(df, x=df.index, y=selected_col, title=f"{selected_col} Distribution")
            fig.add_scatter(x=anomalies_df.index, y=anomalies_df[selected_col], mode='markers', marker=dict(color='red', size=10, symbol='x'))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success(f"No anomalies detected in `{selected_col}`.")

# TAB 2: AI Analyst
with tab2:
    st.subheader("💬 Ask AI Data Analyst")
    user_query = st.text_input("Enter your query (e.g. Total salary, null count, average):")
    if st.button("Analyze Data", type="primary"):
        if user_query:
            with st.spinner("Analyzing..."):
                res = ask_data_agent(df, user_query)
                st.info(res)

# TAB 3: Export & Send PDF Report
with tab3:
    st.subheader("📄 Export Audit & Summary Report")
    st.write("Generate and download a clean PDF summary report of your uploaded dataset.")

    # PDF Generate
    pdf_buffer = generate_pdf_report(df, summary_text=f"Dataset contains {len(df)} rows and {len(df.columns)} columns.")

    st.download_button(
        label="📥 Download PDF Audit Report",
        data=pdf_buffer,
        file_name="Business_Audit_Report.pdf",
        mime="application/pdf",
        type="primary"
    )

    st.markdown("---")
    st.subheader("📧 Send Report via Email")
    
    if enable_email and recipient_email:
        if st.button("Send PDF Summary Email"):
            with st.spinner("Sending email..."):
                status, err_msg = send_alert_email(
                    recipient_email, 
                    "Business Intelligence Audit Report", 
                    f"Hello,\n\nPlease find attached the business audit report for your uploaded dataset.\n\nTotal Records Analyzed: {len(df)} rows.\n\nBest regards,\nAI Business Intelligence Agent",
                    pdf_buffer=pdf_buffer,
                    filename="Business_Audit_Report.pdf"
                )
                if status:
                    st.success(f"Report PDF ke sath {recipient_email} par bhej di gayi hai! 📩")
                else:
                    st.error(f"Email failed: {err_msg}")