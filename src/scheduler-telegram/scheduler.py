import schedule
import os
import time
import requests
import logging
from datetime import datetime
import subprocess


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def is_script_exists(script_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, 'scripts', f"{script_name}.py")
    return os.path.isfile(script_path)


def run_script(script_name):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, 'scripts', script_name)
        subprocess.run(['python', script_path])
    except Exception as e:
        logger.error(f"Error running {script_path}: {e}")

# def market():
#     """Execute market update"""
#     try:
#         logger.info("Executing market function...")
#         send_update()
#         logger.info("Market function completed successfully")
#     except Exception as e:
#         logger.error(f"Error in market function: {e}", exc_info=True)


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


def parse_times(time_field):
    """Parse time field, which can be a single time or comma-separated times."""
    if isinstance(time_field, str):
        return [t.strip() for t in time_field.split(',')]
    elif isinstance(time_field, list):
        return [t.strip() for t in time_field]
    else:
        return []

def process():
    """Load schedule config and schedule jobs"""
    repo_url = "https://raw.githubusercontent.com/aksh-github/py-utils/refs/heads/master/src/scheduler-telegram/schedule.json"
    config = read_json_from_github(repo_url)

    if config is None:
        logger.error("Failed to load configuration from GitHub. Exiting.")
        return

    # Map function names to actual functions
    # func_map = {
    #     'market': market,
    #     'timesheet': timesheet,
    #     'month_test': month_test
    # }

    scheduled_jobs = 0
    monthly_warning_logged = False

    scheduled = []
    skipped = []
    
    # Schedule jobs
    for freq, jobs in config.items():
        for job in jobs:
            # func = func_map.get(job['script'])
            # if func is None:
            #     logger.warning(f"Function '{job['script']}' not found in func_map")
            #     continue

            # Parse times (support comma-separated)
            times = parse_times(job.get('time', ''))

            if freq == 'daily':
                current_time = datetime.now().strftime("%H:%M")
                for t in times:
                    if current_time < t:

                        # check if script file exists
                        # logger.info(os.path.join(script_dir, 'scripts', f"{job['script']}.py"))
                        if not is_script_exists(job['script']):
                            logger.warning(f"Script file {job['script']}.py does not exist")
                            continue

                        schedule.every().day.at(t).do(run_script, f"{job['script']}.py")
                        # logger.info(f"Scheduled {job['script']} daily at {t}")
                        scheduled.append(f"[DAILY]: Scheduled {job['script']} at {t}")
                        scheduled_jobs += 1
                    else:
                        # logger.info(f"Skipped scheduling {job['script']} daily at {t} (time has passed)")
                        skipped.append(f"[DAILY]: Skipped scheduling {job['script']} at {t} (time has passed)")
            # elif freq == 'hourly':
            #     schedule.every().hour.do(func)
            #     logger.info(f"Scheduled {job['script']} hourly")
            #     scheduled_jobs += 1
            elif freq == 'monthly':

                if not monthly_warning_logged:
                    logger.warning("** Monthly ** Need a cron job for monthly scheduling to work. Refer cron.txt for details.")
                    monthly_warning_logged = True

                current_day = datetime.now().day
                # Support both single day and array of days
                job_days = job['day'] #if isinstance(job['day'], list) else [job['day']]
                for t in times:
                    if current_day in job_days and datetime.now().strftime("%H:%M") < t:

                        # check if script file exists
                        if not is_script_exists(job['script']):
                            logger.warning(f"Script file {job['script']}.py does not exist")
                            continue


                        schedule.every().day.at(t).do(run_script, f"{job['script']}.py")
                        # logger.info(f"Scheduled {job['script']} monthly on day(s) {job_days} at {t}")
                        scheduled.append(f"[MONTHLY]: Scheduled {job['script']} on day(s) {job_days} at {t}")
                        scheduled_jobs += 1
                    else:
                        # logger.info(f"Skipped scheduling monthly job for {job['script']} at {current_day} {t} (day mismatch or time passed)")
                        skipped.append(f"[MONTHLY]: Skipped scheduling for {job['script']} on day {current_day} at {t} (day mismatch or time passed)")
            else:
                logger.warning(f"Unknown frequency: {freq}")

    logger.info(f"Total jobs scheduled: {scheduled_jobs}")

    # log scheduled and skipped jobs
    for s in scheduled:
        logger.info(s)

    for s in skipped:
        logger.info(s)
    
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
    

