import logging
import os

def setup_logging(log_file_path="app.log", level=logging.INFO):
    """root logger setup for the application"""
    
    log_dir = os.path.dirname(log_file_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # clear existing handlers to prevent duplicate logs on reload
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler() # console logging
        ]
    )
    