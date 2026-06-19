

import requests
import json
import logging

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_arattai_message(webhook_url, message_text):
    # Define the payload format mapped in your Zoho Flow setup
    payload = {
        "content": message_text
    }
    
    # Send the POST request to your custom webhook bridge
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
        
        if response.status_code in [200, 201, 202]:
            logging.info("Message sent to Arattai successfully!")
            logging.info(response.content)
        else:
            logging.info(f"Failed to send message. Status code: {response.status_code}")
            logging.info(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred: {e}")

# # Execute the message broadcast
# send_arattai_message(ZOHO_FLOW_WEBHOOK_URL, "Hello Team! This is an automated message sent via Python.")
