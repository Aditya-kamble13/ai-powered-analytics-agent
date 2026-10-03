import pandas as pd


class BusinessMonitor:

    def __init__(self, filepath, baseline_days=7, threshold=0.15):
        self.filepath = filepath
        self.baseline_days = baseline_days
        self.threshold = threshold  # 0.15 matlab 15% deviation threshold

    def load_and_process_data(self):
        # 1. CSV Data Load karo
        df = pd.read_csv(self.filepath)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')

        # 2. Latest Day vs Past Baseline split karo
        latest_row = df.iloc[-1]
        baseline_data = df.iloc[-(self.baseline_days + 1) : -1]

        anomalies = []
        metrics = ['Revenue', 'Conversion_Rate', 'Traffic_Volume']

        # 3. Har metric ko compare karo
        for metric in metrics:
            current_value = latest_row[metric]
            baseline_avg = baseline_data[metric].mean()

            # Percentage Change Formula
            pct_change = (current_value - baseline_avg) / baseline_avg

            # Threshold Check
            if abs(pct_change) >= self.threshold:
                anomalies.append(
                    {
                        'metric': metric,
                        'current': current_value,
                        'baseline': baseline_avg,
                        'pct_change': pct_change * 100,
                        'direction': (
                            'increased' if pct_change > 0 else 'declined'
                        ),
                    }
                )

        return anomalies, latest_row['Date'].strftime('%Y-%m-%d')


# Self Testing Block
if __name__ == '__main__':
    monitor = BusinessMonitor('data/business_metrics.csv')
    found_anomalies, date_str = monitor.load_and_process_data()
    print(f'=== Date: {date_str} ===')
    print('Detected Anomalies:', found_anomalies)