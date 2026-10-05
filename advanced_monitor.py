import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

def detect_zscore_anomalies(df: pd.DataFrame, column: str, threshold: float = 2.5) -> pd.DataFrame:
    """Z-Score Statistical Method"""
    mean_val = df[column].mean()
    std_val = df[column].std()
    
    if std_val == 0 or pd.isna(std_val):
        df['anomaly'] = False
        df['anomaly_score'] = 0.0
        return df

    z_scores = (df[column] - mean_val) / std_val
    df['anomaly_score'] = z_scores.abs()
    df['anomaly'] = df['anomaly_score'] > threshold
    return df

def detect_iqr_anomalies(df: pd.DataFrame, column: str, multiplier: float = 1.5) -> pd.DataFrame:
    """Interquartile Range (IQR) Method"""
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - (multiplier * IQR)
    upper_bound = Q3 + (multiplier * IQR)
    
    df['anomaly'] = (df[column] < lower_bound) | (df[column] > upper_bound)
    # Distance from nearest bound as score
    df['anomaly_score'] = np.maximum(lower_bound - df[column], df[column] - upper_bound).clip(lower=0)
    return df

def detect_iso_forest_anomalies(df: pd.DataFrame, numeric_cols: list, contamination: float = 0.05) -> pd.DataFrame:
    """Unsupervised Machine Learning: Isolation Forest"""
    clean_df = df[numeric_cols].fillna(df[numeric_cols].median())
    
    model = IsolationForest(contamination=contamination, random_state=42)
    preds = model.fit_predict(clean_df)
    scores = model.decision_function(clean_df)
    
    df['anomaly'] = preds == -1
    df['anomaly_score'] = -scores  # Higher score = more anomalous
    return df

def detect_categorical_anomalies(df: pd.DataFrame, column: str, min_frequency_percent: float = 1.0) -> pd.DataFrame:
    """Categorical / Text Rare Frequency Detection"""
    total_count = len(df)
    freqs = df[column].value_counts(normalize=True) * 100
    
    rare_categories = freqs[freqs < min_frequency_percent].index
    
    df['anomaly'] = df[column].isin(rare_categories)
    df['anomaly_score'] = df[column].map(freqs).apply(lambda x: 100.0 - x if pd.notna(x) else 100.0)
    return df