import os
import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

# Local modules import
from ai_agent import ask_data_agent, generate_audit_narrative
from advanced_monitor import detect_anomalies
from logger_alert import log_alert
from real_emailer import send_alert_email

# Load environment variables
load_dotenv()

# Streamlit Page Config
st.set_page_config(
    page_title="AI Business Intelligence & Audit Agent",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI Business Intelligence & Anomaly Detection Agent")
st.markdown("Automated multi-format data auditing, statistical anomaly detection, and interactive AI analytics.")

# ---------------------------------------------------------
# Sidebar: File Upload & Controls
# ---------------------------------------------------------
st.sidebar.header("📁 Data Source & Settings")
uploaded_file = st.sidebar.file_uploader(
    "Upload Business Data (CSV, XLSX, XML)", 
    type=["csv", "xlsx", "xml"]
)

# Email Notification Settings
st.sidebar.subheader("📧 Email Alert Settings")
enable_email = st.sidebar.checkbox("Enable Automated Email Alerts", value=False)
recipient_email = st.sidebar.text_input("Recipient Email", value="")

# ---------------------------------------------------------
# Data Loader Function
# ---------------------------------------------------------
@st.cache_data
def load_data(file):
    file_extension = file.name.split(".")[-1].lower()
    if file_extension == "csv":
        return pd.read_csv(file)
    elif file_extension == "xlsx":
        return pd.read_excel(file)
    elif file_extension == "xml":
        return pd.read_xml(file)
    else:
        raise ValueError("Unsupported file format")

# Default / Fallback Data loading if no file uploaded
if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)
        st.sidebar.success(f"Successfully loaded {uploaded_file.name}")
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()
else:
    # Sample fallback data for immediate UI demo
    sample_data_path = os.path.join("data", "business_metrics.csv")
    if os.path.exists(sample_data_path):
        df = pd.read_csv(sample_data_path)
        st.info("Using sample dataset (`data/business_metrics.csv`). Upload your file from the sidebar to audit custom data.")
    else:
        st.warning("Please upload a CSV, Excel, or XML file to begin.")
        st.stop()

# ---------------------------------------------------------
# Tab Layout Setup
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📊 Data Overview & Anomalies", "💬 Ask AI Data Analyst", "📝 Executive Audit Report"])

# =========================================================
# TAB 1: Data Overview & Anomaly Detection
# =========================================================
with tab1:
    st.subheader("Data Preview")
    st.dataframe(df.head(10), use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Rows", df.shape[0])
    col2.metric("Total Columns", df.shape[1])
    col3.metric("Missing Values", df.isnull().sum().sum())

    st.markdown("---")
    st.subheader("🔍 Statistical Anomaly Detection")

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    if numeric_cols:
        selected_col = st.selectbox("Select Numeric Metric for Anomaly Detection", numeric_cols)
        z_threshold = st.slider("Z-Score Threshold", min_value=1.5, max_value=4.0, value=2.5, step=0.1)

        anomalies_df = detect_anomalies(df, column=selected_col, threshold=z_threshold)

        if not anomalies_df.empty:
            st.error(f"⚠️ Detected {len(anomalies_df)} anomalies in `{selected_col}`!")
            st.dataframe(anomalies_df, use_container_width=True)

            # Plotly Visualization
            fig = px.scatter(
                df, 
                x=df.index, 
                y=selected_col, 
                title=f"{selected_col} Distribution & Outliers"
            )
            fig.add_scatter(
                x=anomalies_df.index, 
                y=anomalies_df[selected_col], 
                mode='markers', 
                marker=dict(color='red', size=10, symbol='x'),
                name='Anomaly'
            )
            st.plotly_chart(fig, use_container_width=True)

            # Trigger Email Alert if enabled
            if enable_email and recipient_email:
                if st.button("Send Anomaly Alert Email"):
                    alert_msg = f"Detected {len(anomalies_df)} anomalies in column '{selected_col}' exceeding Z-score threshold of {z_threshold}."
                    email_sent = send_alert_email(recipient_email, "AI BI Agent Alert: Anomalies Detected", alert_msg)
                    if email_sent:
                        log_alert(f"Email alert sent to {recipient_email} for {selected_col}")
                        st.success(f"Alert email sent to {recipient_email}")
                    else:
                        st.error("Failed to send email. Check SMTP credentials in Streamlit Secrets.")
        else:
            st.success(f"No statistical anomalies found in `{selected_col}` with threshold {z_threshold}.")
    else:
        st.warning("No numeric columns found in the dataset for anomaly detection.")

# =========================================================
# TAB 2: Interactive AI Data Analyst Chat (Code Execution Agent)
# =========================================================
with tab2:
    st.subheader("💬 Natural Language Data Queries")
    st.markdown("""
    Poochho apne dataset se jude koi bhi sawal — jaise **totals, null counts, averages, specific employee calculations, ya anomalies ka reason**!
    AI backend par directly **Pandas Python code execute** karke 100% accurate results dega.
    """)

    # Quick prompt suggestions
    st.markdown("**Example Questions:**")
    example_col1, example_col2, example_col3 = st.columns(3)
    if example_col1.button("Kahan par null values hain?"):
        st.session_state["user_q"] = "Konsi columns mein kitni null ya missing values hain?"
    if example_col2.button("Summary metrics batao"):
        st.session_state["user_q"] = "Har numeric column ka average aur total sum calculate karke batao."
    if example_col3.button("Outliers / Key Findings"):
        st.session_state["user_q"] = "Dataset mein sabse high aur low values waale records search karo."

    default_q = st.session_state.get("user_q", "")
    user_query = st.text_input("Enter your question about the dataset:", value=default_q)

    if st.button("Analyze Data", type="primary"):
        if user_query.strip():
            with st.spinner("AI Pandas Code execute kar raha hai..."):
                agent_response = ask_data_agent(df, user_query)
                st.markdown("### 🤖 AI Response:")
                st.info(agent_response)
        else:
            st.warning("Kripya pehle koi sawal enter karein.")

# =========================================================
# TAB 3: Executive Narrative Audit Report
# =========================================================
with tab3:
    st.subheader("📝 Executive Summary & Root-Cause Audit")
    
    if st.button("Generate Executive Audit Narrative"):
        with st.spinner("Gemini AI audit report compile kar raha hai..."):
            narrative = generate_audit_narrative(df)
            st.markdown(narrative)