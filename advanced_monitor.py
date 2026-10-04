import pandas as pd
import numpy as np

def detect_anomalies(df: pd.DataFrame, column: str, threshold: float = 2.5) -> pd.DataFrame:
    """
    Z-score statistical method ka use karke select kiye gaye numeric column
    mein se anomalies / outliers detect karta hai.
    """
    if column not in df.columns:
        return pd.DataFrame()

    # Drop missing values for calculation
    col_data = df[column].dropna()

    if col_data.empty or col_data.std() == 0:
        return pd.DataFrame()

    # Mean aur Standard Deviation calculate karo
    mean = col_data.mean()
    std = col_data.std()

    # Z-score formula calculation
    z_scores = (df[column] - mean) / std

    # Threshold se zyada deviation waale rows filter karo
    anomalies = df[np.abs(z_scores) > threshold]
    return anomalies