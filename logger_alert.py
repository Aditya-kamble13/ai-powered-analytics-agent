import logging
from datetime import datetime

# Logging setup
logging.basicConfig(
    filename="alerts_history.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_alert(message: str) -> None:
    """
    Alert messages ko local log file (alerts_history.log) mein record karta hai.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{timestamp}] {message}"
    logging.info(formatted_msg)
    print(f"Logged Alert: {formatted_msg}")