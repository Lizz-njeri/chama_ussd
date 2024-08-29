from flask import Flask, request
import africastalking
import os


app = Flask(__name__)
username = "sandbox"
api_key = "3adc38411762a440a8be783fec02b2c736fe13619ff3f760976fef0b51f668e4"
africastalking.initialize(username, api_key)
sms = africastalking.SMS

@app.route('/', methods=['POST', 'GET'])

def ussd_callback():
    global response
    session_id = request.values.get("sessionId", None)
    service_code = request.values.get("serviceCode", None)
    phone_number = request.values.get("phoneNumber", None)
    text = request.values.get("text", "default")
    sms_phone_number = []
    sms_phone_number.append(phone_number)

    #ussd logic
    if text == "":
        #main menu
        response = "CON Welcome to mahiga self help group.\n"
        response += "1. Make savings\n"
        response += "2. Request Loan\n"
        response += "3. Cycle\n"
    elif text == "1":
        #sub menu 1
        response = "CON Make savings in?\n"
        response += "1. Welfare\n"
        response += "2. Social fund\n"
        response += "3. Emergenccy\n"
        response += "4. Goal\n"

    elif text == "1*1":
        response = ""

    elif text == "1*2":
        response = ""
    
    elif text == "1*3":
        response = ""
        
    elif text == "1*4":
        response = ""
        
    elif text == "2":
        #sub menu 1 
        response = "CON Enter amount of loan you would like to request?"
        response += ""

    elif text == "3":
        #sub menu 1 
        response = "END This cycle ranges from 8th Jan to 15th june"
    
    else:
        response= "END Invalid input"
    
    return response




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.environ.get("PORT"))