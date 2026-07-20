import logging
import sys

def setup_logging(app):
    log_level = logging.DEBUG if app.config.get('DEBUG') else logging.INFO
    
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s'
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    root_logger.addHandler(console_handler)
    
    # Specific standard levels
    logging.getLogger('app.workflow').setLevel(logging.INFO)
    logging.getLogger('app.audit').setLevel(logging.INFO)
    logging.getLogger('app.repository').setLevel(logging.DEBUG)
    
    # Optional SQLAlchemy queries debugging
    if app.config.get('DEBUG'):
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
