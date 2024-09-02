# main.py
from flask import Flask, request, jsonify
import africastalking
import os
import requests
import logging


app = Flask(__name__)
username = "sandbox"
api_key = "AFRICASTALKING API KEY"
africastalking.initialize(username, api_key)
sms = africastalking.SMS




@app.route('/', methods=['POST', 'GET'])
def ussd_callback():
    global response
    session_id = request.values.get("sessionId", None)
    service_code = request.values.get("serviceCode", None)
    phone_number = request.values.get("phoneNumber", None)
    text = request.values.get("text", "default")
    sms_phone_number = [phone_number]

    # USSD logic
    if text == "":
        # Main menu
        response = "CON Welcome to Mahiga Self Help Group.\n"
        response += "1. Make savings\n"
        response += "2. Request Loan\n"
        response += "3. Cycle\n"
    
    elif text == "1":
        # Sub menu for making savings
        response = "CON Choose savings type:\n"
        response += "1. Welfare\n"
        response += "2. Social fund\n"
        response += "3. Emergency\n"
        response += "4. Goal\n"
    
    elif text in ["1*1", "1*2", "1*3", "1*4"]:
        # Prompt for the amount of money to save based on the savings type chosen
        response = "CON Enter the amount to save:\n"
    
    elif text.count('*') == 2 and text.startswith("1*"):
        # Save the amount and send confirmation SMS
        save_amount = text.split('*')[-1]
        response = f"END please pay Ksh {save_amount} to the prompt. Thank you!"
        # Sending SMS confirmation
        try:
            sms.send(f"Your savings of Ksh {save_amount}. are received", sms_phone_number, sender_id="20880")
        except Exception as e:
            print(f"Failed to send SMS: {e}")

    elif text == "2":
        # Requesting loan
        response = "CON Enter the amount of loan amount you would like to request:\n"

    elif text.startswith("2*") and len(text.split('*')) == 2:
        # Handle loan amount request and check SIM swap status before approval
        loan_amount = text.split('*')[-1]
        sim_swap_result = check_sim_swap_state_api([phone_number])  # Check SIM swap status
        
        # Check the SIM swap status
        sim_swap_status = sim_swap_result.get('status', 'Not Swapped')
        print(sim_swap_status)
       
        africastalking.initialize(user, api_key)
        sms = africastalking.SMS
        
        if sim_swap_status == "Swapped":
            # Decline loan if SIM has been swapped recently
            response = "END Your loan request has been received."
            try:
                sms.send("Your loan request has been declined due to recent SIM swap detection.", sms_phone_number)
            except Exception as e:
                print(f"Failed to send SMS: {e}")
        else:
            # Approve loan if no SIM swap detected
            response = f"END Your loan request of Ksh {loan_amount} has been received."
            try:
                sms.send(f"Your loan request for Ksh {loan_amount} has been approved.", sms_phone_number, sender_id="20880")
            except Exception as e:
                print(f"Failed to send SMS: {e}")

    elif text == "3":
        # Information about the current cycle
        response = "END This cycle ranges from 8th Jan to 15th June."
    
    else:
        response = "END Invalid input."
    
    return response

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Global dictionary to store SIM swap status
sim_swap_status = {}



def check_sim_swap_state_api(phone_numbers):
    url = "https://insights.sandbox.africastalking.com/v1/sim-swap"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "apiKey": "AFRICASTALKING API KEY"  # Replace with your actual API key
    }
    payload = {
        "username": "sandbox",  # Replace with your actual username
        "phoneNumbers": phone_numbers if isinstance(phone_numbers, list) else [phone_numbers]
    }

    try:
        logging.debug(f"Sending request to {url} with payload {payload}")
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        print('----')
        # result=print(result)
        logging.debug(f"Response received: {result}")
        transactionId = result[0]

        print(transactionId)
        #s
        # Add SIM swap status from the global dictionary
        for phone_number in phone_numbers:
            if phone_number in sim_swap_status:
                result['status'] = sim_swap_status[phone_number]['status']
            else:
                result['status'] = 'Not Found'
        
        return result
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}, Response: {response.text}")
        return {"error": f"HTTP error occurred: {http_err}"}
    except Exception as err:
        logging.error(f"An error occurred: {err}")
        return {"error": f"An error occurred: {err}"}

@app.route('/check_sim_swap_state', methods=['POST'])
def check_sim_swap_state():
    logging.debug("Received request at /check_sim_swap_state")
    data = request.json
    phone_numbers = data.get('phoneNumbers')
    
    if not phone_numbers:
        return jsonify({"error": "phoneNumbers are required"}), 400

    # Ensure phone_numbers is a list
    if isinstance(phone_numbers, str):
        phone_numbers = [phone_numbers]
    
    result = check_sim_swap_state_api(phone_numbers)
    return jsonify(result)

@app.route('/receive', methods=['POST'])
def receive():
    try:
        # Extract data from the JSON request body
        data = request.json
        status = data.get('status')
        last_sim_swap_date = data.get('lastSimSwapDate')
        provider_ref_id = data.get('providerRefId')
        request_id = data.get('requestId')
        transaction_id = data.get('transactionId')

        # if not phone_number:
        #     logging.error("Received callback without phoneNumber.")
        #     return jsonify({"error": "phoneNumber is required"}), 400

        # # Store the SIM swap status in the global dictionary
        # sim_swap_status[phone_number] = {
        #     'status': status,
        #     'lastSimSwapDate': last_sim_swap_date,
        #     'providerRefId': provider_ref_id,
        #     'requestId': request_id,
        #     'transactionId': transaction_id
        # }

        logging.info(f"SIM Swap Callback Received: {data}")
        print("Received data:", data)

        return jsonify({"message": "Callback received successfully"}), 200
    except Exception as error:
        logging.error(f"Error processing SIM swap callback: {error}")
        return jsonify({"error": "Failed to process callback"}), 400







if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.environ.get("PORT"))
