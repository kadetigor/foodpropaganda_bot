import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging
def setup_logger(name):
    """Set up a logger with file and console handlers."""
    
    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Check if logger already has handlers to avoid duplicates
    if logger.handlers:
        return logger
    
    # Create a file handler for the log file with date in filename
    date_str = datetime.now().strftime('%Y-%m-%d')
    file_handler = logging.FileHandler(f'logs/bot_{date_str}.log')
    file_handler.setLevel(logging.INFO)
    
    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
