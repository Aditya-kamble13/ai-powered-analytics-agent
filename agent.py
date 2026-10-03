from logger_alert import NotificationEngine
from monitor import BusinessMonitor


class ExecutiveAgent:

    def __init__(self, data_path):
        self.monitor = BusinessMonitor(data_path)

    def run_pipeline(self):
        # 1. Anomaly Detection
        anomalies, date_str = self.monitor.load_and_process_data()

        print(f'==========================================')
        print(f'📊 EXECUTIVE BUSINESS REPORT [{date_str}]')
        print(f'==========================================\n')

        if not anomalies:
            print(
                'All business health metrics are operating within normal baseline ranges.'
            )
            return

        anom_map = {a['metric']: a for a in anomalies}
        narrative = ''

        # 2. Executive Narrative Logic
        if 'Revenue' in anom_map and 'Conversion_Rate' in anom_map:
            rev = anom_map['Revenue']
            conv = anom_map['Conversion_Rate']

            if rev['direction'] == 'increased' and conv['direction'] == 'declined':
                narrative = (
                    'Revenue increased sharply this week despite a decline in conversion rate. '
                    'This pattern indicates a significant surge in top-of-funnel traffic volume, '
                    'which drove higher total revenue even though intent/checkout efficiency decreased.'
                )

        print('💡 Executive Narrative:')
        print(f'{narrative}\n')

        # 3. Clean Metric Breakdown
        print('📈 Key Metric Deviations:')
        for a in anomalies:
            metric_name = a['metric'].replace('_', ' ')
            change_val = a['pct_change']
            curr = float(a['current'])
            base = float(a['baseline'])

            print(
                f"- {metric_name}: {a['direction'].upper()} by {abs(change_val):.1f}% "
                f"(Current: {curr:,.2f} | 7-Day Avg: {base:,.2f})"
            )

        # 4. Trigger Logging & Email Notification
        NotificationEngine.log_and_notify(date_str, anomalies, narrative)


if __name__ == '__main__':
    agent = ExecutiveAgent('data/business_metrics.csv')
    agent.run_pipeline()