import schedule
import json
import time
import requests
from market import send_update

# ... (func1, func2, etc. definitions)


def market(to):
    # print(f"Market function executed for group {to}")
    send_update()
    
def timesheet(to):
    print(f"Timesheet function executed")


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
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


def process():
    # Load JSON config for docker server
    # with open('./src/schedule.json') as f:
    # Load JSON config for local testing
    # with open('./src/telegram/schedule.json') as f:

    repo_url = "https://raw.githubusercontent.com/aksh-github/py-utils/refs/heads/master/src/telegram/schedule.json"
    config = read_json_from_github(repo_url)

    if config is None:
        print("Failed to load configuration. Exiting.")
        return

    # Map function names to actual functions
    func_map = {
        'market': market,
        'timesheet': timesheet,
    }

    # Schedule jobs
    for freq, jobs in config.items():
        for job in jobs:
            func = func_map.get(job['function_name'])
            if freq == 'daily':
                schedule.every().day.at(job['time']).do(func, job['to'] if 'to' in job else None)
            elif freq == 'hourly':
                schedule.every().hour.do(func)
            elif freq == 'monthly':
                # schedule library doesn't support monthly directly
                # use a workaround or consider APScheduler
                print("Monthly scheduling not directly supported by schedule library")
            # Add more frequencies as needed

    # Run scheduler
    while True:
        # pytz.timezone('Asia/Kolkata')
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    print("Container is running...")
    process()
    # while True:
    #     time.sleep(1)
