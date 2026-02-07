import schedule
import json
import time
import pytz
import importlib

# ... (func1, func2, etc. definitions)


def market(to):
    print(f"Market function executed for group {to}")
    
def timesheet(to):
    print(f"Timesheet function executed")

# Load JSON config for docker server
with open('./schedule.json') as f:
# Load JSON config for local testing
# with open('./src/telegram/schedule.json') as f:
    config = json.load(f)

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
    pytz.timezone('Asia/Kolkata')
    schedule.run_pending()
    time.sleep(1)