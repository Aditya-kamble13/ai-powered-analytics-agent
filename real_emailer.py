from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib
from dotenv import load_dotenv

# .env file se credentials load honge
load_dotenv()


class EmailAlertSystem:

    def __init__(self):
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')

    def send_alert_email(
        self, recipient_email, issues_list, dataset_name, pdf_buffer=None
    ):
        if not issues_list:
            print('No issues detected. Email alert skipped.')
            return False

        if not self.sender_email or not self.sender_password:
            print(
                '⚠️ Email Credentials missing in .env file! Skipping live email.'
            )
            return False

        # Email content construction
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = recipient_email
        msg['Subject'] = (
            f"🚨 CRITICAL AUDIT ALERT: Anomalies Detected in '{dataset_name}'"
        )

        body_text = f"Hi Team,\n\nOur Automated Analytics Monitor detected {len(issues_list)} issues in the recently uploaded dataset ('{dataset_name}').\n\n"
        body_text += "📋 DETECTED ISSUES SUMMARY:\n"
        body_text += "------------------------------------------\n"

        for idx, issue in enumerate(issues_list, 1):
            body_text += (
                f"{idx}. [{issue['type']}] {issue['issue']}\n"
                f"   Details: {issue['detail']}\n\n"
            )

        body_text += "💡 RECOMMENDED ACTIONS:\n"
        body_text += (
            "- Review the attached official PDF Audit Report for details.\n"
        )
        body_text += "- Verify missing/null data rows before processing monthly reports.\n\n"
        body_text += (
            "Best regards,\nAutomated AI-Powered Business Intelligence Agent"
        )

        msg.attach(MIMEText(body_text, "plain"))

        # Attach PDF Report if provided
        if pdf_buffer:
            pdf_attachment = MIMEApplication(
                pdf_buffer.getvalue(), _subtype="pdf"
            )
            pdf_attachment.add_header(
                "Content-Disposition",
                "attachment",
                filename=f"Audit_Report_{dataset_name}.pdf",
            )
            msg.attach(pdf_attachment)

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            print(
                f"✅ Live Email Alert with PDF Attachment successfully sent to {recipient_email}!"
            )
            return True
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False