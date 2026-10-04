# 📊 AI Business Intelligence & Anomaly Detection Agent

An intelligent business analytics platform designed to monitor key performance metrics, detect data anomalies, and provide conversational insights using Google's Gemini AI.

### ✨ Key Features
- 🔍 **Automated Anomaly Detection**: Monitors key business metrics and highlights sudden dips or surges against baseline trends.
- 💬 **Ask AI Data Analyst**: Ask natural language questions about your dataset to execute instant Pandas queries via `gemini-3.8-flash`.
- 📑 **Dynamic PDF Reporting**: Generates clean, landscape-oriented PDF reports with automatic text-wrapping for multi-column datasets using ReportLab.
- 📩 **Automated Email Delivery**: Sends detailed audit summary PDFs directly to stakeholders using Gmail SMTP integration.
- ⚡ **Streamlit Dashboard**: Fast, intuitive, and interactive UI for real-time data exploration and analytics.

### 🛠️ Tech Stack
- **Frontend / UI**: Streamlit
- **AI Core**: Google GenAI SDK (`gemini-3.8-flash`)
- **Data Processing**: Pandas, NumPy
- **PDF Generation**: ReportLab
- **Notification System**: Python SMTP (Gmail API/App Passwords)
