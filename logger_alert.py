from datetime import datetime
import logging

# Audit Logging Configuration
logging.basicConfig(
    filename='alerts_history.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)


class NotificationEngine:

    @staticmethod
    def log_and_notify(date_str, anomalies, narrative):
        if not anomalies:
            print('No anomalies to log or alert.')
            return

        # 1. Audit Trail Record
        flagged_metrics = [a['metric'] for a in anomalies]
        log_message = (
            f"ANOMALY DETECTED [{date_str}] - Metrics: {', '.join(flagged_metrics)}"
        )
        logging.info(log_message)

        # 2. Mock Email Notification Layout
        print('\n==========================================')
        print('📧 AUTOMATED EMAIL ALERT SIMULATION')
        print('==========================================')
        print(f"To: management-team@company.com")
        print(
            f"Subject: 🚨 ACTION REQUIRED: Metric Anomaly Detected [{date_str}]"
        )
        print('------------------------------------------')
        print('Hi Team,\n')
        print(
            'Our automated monitoring agent detected significant performance deviations:\n'
        )
        print(f'{narrative}\n')
        print('💡 Recommended Action:')
        print(
            '- Review top traffic acquisition channels to assess conversion drop.'
        )
        print(
            '- Verify checkout funnel stability for payment gateway issues.\n'
        )
        print('Best regards,')
        print('Automated Business Intelligence Agent')
        print('==========================================\n')

        print("✅ Alert logged successfully in 'alerts_history.log'!")


# Self Testing
if __name__ == '__main__':
    sample_anomalies = [{'metric': 'Revenue'}, {'metric': 'Conversion_Rate'}]
    sample_narrative = (
        'Revenue increased sharply while conversion rate declined.'
    )
    NotificationEngine.log_and_notify(
        '2026-09-27', sample_anomalies, sample_narrative
    )