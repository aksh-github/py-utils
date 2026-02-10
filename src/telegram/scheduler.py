import schedule
import json
import time
import requests
import logging
from datetime import datetime
from market import send_update

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def market():
    """Execute market update"""
    try:
        logger.info("Executing market function...")
        send_update()
        logger.info("Market function completed successfully")
    except Exception as e:
        logger.error(f"Error in market function: {e}", exc_info=True)

    
def timesheet():
    """Execute timesheet function"""
    try:
        logger.info("Executing timesheet function...")
        print(f"Timesheet function executed at {datetime.now()}")
        logger.info("Timesheet function completed successfully")
    except Exception as e:
        logger.error(f"Error in timesheet function: {e}", exc_info=True)


def read_json_from_github(repo_url):
    """
    Reads a JSON file from a GitHub repository.

    Args:
        repo_url (str): URL of the JSON file in the GitHub repository.
                         Format: https://raw.githubusercontent.com/username/repo_name/branch_name/path/to/file.json

    Returns:
        dict: JSON data from the file.
    """
    try:
        response = requests.get(repo_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error reading from GitHub: {e}")
        return None


def process():
    """Load schedule config and schedule jobs"""
    repo_url = "https://raw.githubusercontent.com/aksh-github/py-utils/refs/heads/master/src/telegram/schedule.json"
    config = read_json_from_github(repo_url)

    if config is None:
        logger.error("Failed to load configuration from GitHub. Exiting.")
        return

    # Map function names to actual functions
    func_map = {
        'market': market,
        'timesheet': timesheet,
    }

    scheduled_jobs = 0
    
    # Schedule jobs
    for freq, jobs in config.items():
        for job in jobs:
            func = func_map.get(job['function_name'])
            if func is None:
                logger.warning(f"Function '{job['function_name']}' not found in func_map")
                continue
                
            if freq == 'daily':
                schedule.every().day.at(job['time']).do(func)
                logger.info(f"Scheduled {job['function_name']} daily at {job['time']}")
                scheduled_jobs += 1
            elif freq == 'hourly':
                schedule.every().hour.do(func)
                logger.info(f"Scheduled {job['function_name']} hourly")
                scheduled_jobs += 1
            elif freq == 'monthly':
                logger.warning("Monthly scheduling not directly supported by schedule library")
            else:
                logger.warning(f"Unknown frequency: {freq}")

    logger.info(f"Total jobs scheduled: {scheduled_jobs}")
    
    # Run scheduler
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error in scheduler loop: {e}", exc_info=True)
            time.sleep(5)  # Wait before retrying


if __name__ == '__main__':
    logger.info("Container is running...")
    logger.info("Starting scheduler...")
    process()
