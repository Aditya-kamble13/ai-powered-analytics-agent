import streamlit as st
import pandas as pd
from advanced_monitor import (
    detect_zscore_anomalies, 
    detect_iqr_anomalies, 
    detect_iso_forest_anomalies, 
    detect_categorical_anomalies
)
from ai_agent import ask_gemini_analyst
from report_generator import generate_pdf_report
from real_emailer import send_email_with_attachment

st.set_page_config(page_title="AI Analytics Agent", layout="wide")

st.title("📊 AI Business Intelligence & Anomaly Detection Agent")

# Helper function to load multi-format datasets
def load_uploaded_file(uploaded_file):
    file_ext = uploaded_file.name.split('.')[-1].lower()
    if file_ext == 'csv':
        return pd.read_csv(uploaded_file)
    elif file_ext in ['xlsx', 'xls']:
        return pd.read_excel(uploaded_file)
    elif file_ext == 'json':
        return pd.read_json(uploaded_file)
    elif file_ext == 'xml':
        return pd.read_xml(uploaded_file)
    else:
        st.error("Unsupported file format!")
        return None

# Sidebar File Uploader supporting CSV, Excel, JSON, XML
uploaded_file = st.sidebar.file_uploader(
    "Upload Dataset File", 
    type=["csv", "xlsx", "xls", "json", "xml"]
)

if uploaded_file is not None:
    try:
        df = load_uploaded_file(uploaded_file)

        if df is not None:
            tab1, tab2, tab3 = st.tabs(["📊 Data & Anomalies", "💬 Ask AI Data Analyst", "📑 Export & Send PDF Report"])

            # TAB 1: Data & Anomalies
            with tab1:
                st.subheader("📊 Data & Anomaly Detection Control Center")
                st.dataframe(df.head(10), use_container_width=True)

                st.markdown("---")
                st.subheader("⚙ Choose Detection Method")

                col_method, col_config = st.columns([1, 1])

                with col_method:
                    method = st.selectbox(
                        "Select Detection Technique:",
                        [
                            "Z-Score (Statistical)",
                            "IQR Boxplot (Outlier Robust)",
                            "Isolation Forest (Machine Learning)",
                            "Rare Categorical Frequency (Text Data)"
                        ]
                    )

                    with st.expander("ℹ How does this method work?"):
                        if "Z-Score" in method:
                            st.write("**Z-Score (Parametric)**: Measures standard deviations from mean.")
                            st.latex(r"Z = \frac{X - \mu}{\sigma}")
                        elif "IQR" in method:
                            st.write("**IQR (Non-Parametric)**: Uses 25th (Q1) and 75th (Q3) percentiles. Robust against outliers.")
                        elif "Isolation Forest" in method:
                            st.write("**Isolation Forest (ML)**: Unsupervised model that isolates rare anomalies.")
                        elif "Rare Categorical" in method:
                            st.write("**Rare Frequency**: Flags text values below chosen frequency percentage.")

                with col_config:
                    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

                    if "Z-Score" in method:
                        if numeric_cols:
                            col = st.selectbox("Select Metric:", numeric_cols)
                            thresh = st.slider("Z-Score Threshold", 1.5, 4.0, 2.5)
                            res_df = detect_zscore_anomalies(df.copy(), col, thresh)
                        else:
                            st.warning("No numeric columns found.")

                    elif "IQR" in method:
                        if numeric_cols:
                            col = st.selectbox("Select Metric:", numeric_cols)
                            mult = st.slider("IQR Multiplier", 1.0, 3.0, 1.5)
                            res_df = detect_iqr_anomalies(df.copy(), col, mult)
                        else:
                            st.warning("No numeric columns found.")

                    elif "Isolation Forest" in method:
                        if numeric_cols:
                            selected_cols = st.multiselect("Select Features:", numeric_cols, default=numeric_cols)
                            contam = st.slider("Contamination Rate", 0.01, 0.20, 0.05)
                            if selected_cols:
                                res_df = detect_iso_forest_anomalies(df.copy(), selected_cols, contam)
                        else:
                            st.warning("No numeric columns found.")

                    elif "Rare Categorical" in method:
                        if categorical_cols:
                            col = st.selectbox("Select Text Column:", categorical_cols)
                            min_freq = st.slider("Minimum Frequency (%)", 0.1, 10.0, 1.0)
                            res_df = detect_categorical_anomalies(df.copy(), col, min_freq)
                        else:
                            st.warning("No text columns found.")

                if 'res_df' in locals():
                    anomalies = res_df[res_df['anomaly'] == True]
                    st.session_state['res_df'] = res_df
                    st.markdown("---")
                    st.write(f"### 🚨 Detected Anomalies ({len(anomalies)} found)")
                    if not anomalies.empty:
                        st.dataframe(anomalies, use_container_width=True)
                    else:
                        st.success("No anomalies detected with current parameters!")

            # TAB 2: Ask AI Data Analyst
            with tab2:
                st.subheader("💬 Ask AI Data Analyst")
                user_query = st.text_input("Ask a question about your uploaded dataset:")
                if user_query:
                    with st.spinner("Analyzing dataset..."):
                        response = ask_gemini_analyst(df, user_query)
                        st.write("### 🤖 Gemini Insights:")
                        st.write(response)

            # TAB 3: Export & Send PDF Report
            with tab3:
                st.subheader("📑 Export & Send PDF Report")
                recipient_email = st.text_input("Enter Recipient Email Address:")
                
                col_pdf, col_email = st.columns(2)

                with col_pdf:
                    if st.button("📄 Generate PDF Report"):
                        res_data = st.session_state.get('res_df', df)
                        pdf_filename = generate_pdf_report(res_data)
                        with open(pdf_filename, "rb") as f:
                            st.download_button("⬇ Download PDF", f, file_name="Anomaly_Report.pdf")

                with col_email:
                    if st.button("📧 Send Email Alert"):
                        if recipient_email:
                            res_data = st.session_state.get('res_df', df)
                            pdf_filename = generate_pdf_report(res_data)
                            success, status_msg = send_email_with_attachment(recipient_email, pdf_filename)
                            if success:
                                st.success(f"Email successfully sent to {recipient_email}!")
                            else:
                                st.error(f"Failed to send email: {status_msg}")
                        else:
                            st.warning("Please enter a recipient email.")

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("👈 Please upload a dataset file (CSV, XLSX, XLS, JSON, XML) in the sidebar to start analysis.")