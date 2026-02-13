import logging
import datetime

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def timesheet():
    """Execute timesheet function"""
    try:
        logging.info("Executing timesheet function...")
        print(f"Timesheet function executed at {datetime.now()}")
        logging.info("Timesheet function completed successfully")
    except Exception as e:
        logging.error(f"Error in timesheet function: {e}", exc_info=True)

def month_test():
    """Execute month test function"""
    try:
        logging.info("Executing month_test function...")
        print(f"Month test function executed at {datetime.now()}")
        logging.info("Month test function completed successfully")
    except Exception as e:
        logging.error(f"Error in month_test function: {e}", exc_info=True)

timesheet()
month_test()