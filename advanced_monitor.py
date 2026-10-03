import numpy as np
import pandas as pd


class AdvancedBusinessMonitor:

    def __init__(self, df, baseline_window=7, threshold_pct=0.15, z_threshold=3.0):
        self.df = df
        self.baseline_window = baseline_window
        self.threshold_pct = threshold_pct
        self.z_threshold = z_threshold

    def check_data_quality(self):
        """1. Data Quality & Integrity Checks (Nulls, Duplicates)"""
        issues = []

        # Null values check
        null_counts = self.df.isnull().sum()
        cols_with_nulls = null_counts[null_counts > 0]
        if not cols_with_nulls.empty:
            for col, count in cols_with_nulls.items():
                issues.append(
                    {
                        'type': 'Data Integrity',
                        'issue': f"Missing Values in '{col}'",
                        'detail': f'{count} null rows detected.',
                    }
                )

        # Duplicate rows check
        dup_count = self.df.duplicated().sum()
        if dup_count > 0:
            issues.append(
                {
                    'type': 'Data Integrity',
                    'issue': 'Duplicate Rows',
                    'detail': f'{dup_count} duplicate rows found in dataset.',
                }
            )

        return issues

    def detect_outliers_and_fraud(self, numeric_cols):
        """2. Outlier & Fraud Detection using Z-Score"""
        outlier_issues = []

        for col in numeric_cols:
            if col in self.df.columns and self.df[col].dropna().count() > 3:
                series = self.df[col].dropna()
                mean = series.mean()
                std = series.std()

                if std > 0:
                    z_scores = (series - mean) / std
                    outliers = series[abs(z_scores) > self.z_threshold]

                    if not outliers.empty:
                        outlier_issues.append(
                            {
                                'type': 'Outlier / Fraud Risk',
                                'issue': f"Extreme Values in '{col}'",
                                'detail': f'{len(outliers)} rows exceeded Z-score threshold of {self.z_threshold} (Max value: {outliers.max():,.2f}).',
                            }
                        )

        return outlier_issues

    def detect_metric_anomalies(self, metric_cols):
        """3. Baseline Moving Average Trend Shifts"""
        trend_issues = []

        if 'Date' not in self.df.columns:
            return trend_issues

        df_sorted = self.df.copy()
        df_sorted['Date'] = pd.to_datetime(df_sorted['Date'])
        df_sorted = df_sorted.sort_values('Date')

        if len(df_sorted) <= self.baseline_window:
            return trend_issues

        latest_row = df_sorted.iloc[-1]
        baseline = df_sorted.iloc[-(self.baseline_window + 1) : -1]

        for col in metric_cols:
            if col in df_sorted.columns:
                curr_val = latest_row[col]
                avg_val = baseline[col].mean()

                if avg_val > 0:
                    pct_change = (curr_val - avg_val) / avg_val
                    if abs(pct_change) >= self.threshold_pct:
                        direction = (
                            'increased' if pct_change > 0 else 'declined'
                        )
                        trend_issues.append(
                            {
                                'type': 'Trend Anomaly',
                                'issue': f"Metric Shift in '{col}'",
                                'detail': f'{col} {direction} by {abs(pct_change)*100:.1f}% compared to 7-day average (Current: {curr_val:,.2f} | Baseline: {avg_val:,.2f}).',
                            }
                        )

        return trend_issues

    def run_all_checks(self, numeric_cols, metric_cols):
        """Comprehensive Audit Report"""
        all_issues = []
        all_issues.extend(self.check_data_quality())
        all_issues.extend(self.detect_outliers_and_fraud(numeric_cols))
        all_issues.extend(self.detect_metric_anomalies(metric_cols))
        return all_issues


# Self Testing Block
if __name__ == '__main__':
    # Sample dataset with missing values, duplicate, and high outlier
    test_data = {
        'Date': [
            '2026-09-20',
            '2026-09-21',
            '2026-09-22',
            '2026-09-23',
            '2026-09-24',
            '2026-09-25',
            '2026-09-26',
            '2026-09-27',
            '2026-09-27',
        ],
        'Revenue': [
            12000,
            11800,
            12200,
            None,
            12100,
            12300,
            12050,
            15200,
            15200,
        ],  # None + Duplicate + Spike
        'Transaction_Amount': [
            100,
            150,
            120,
            130,
            110,
            140,
            125,
            130,
            95000,
        ],  # Extreme Fraud Outlier 95000
    }
    df_test = pd.DataFrame(test_data)

    monitor = AdvancedBusinessMonitor(df_test)
    detected_issues = monitor.run_all_checks(
        numeric_cols=['Revenue', 'Transaction_Amount'],
        metric_cols=['Revenue'],
    )

    print('=== 🔍 DETECTED SYSTEM ISSUES ===')
    for issue in detected_issues:
        print(
            f"[{issue['type']}] {issue['issue']} -> {issue['detail']}"
        )