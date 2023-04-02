import requests
import json
from deep_translator import GoogleTranslator

url = "https://iqwhatsapp.airtel.in:443/gateway/airtel-xchange/basic/whatsapp-manager/v1/session/send/text"

def sendHelp(receiver, langId, sessionId):
    
    text = "*Hey I am Chabo! HELP Tools* \n You can avail and enjoy our chatbot services in many ways! Try these examples below! \n\n To trigger video search, text something like *'Video on Pythagoras Theorem'* \n To search something on the internet, you can ask *'What is the biggest fruit?'* \n You can also see your progress by messaging *'Progress me'* \n Feel like testing yourself? Try quizzes by using *'Quiz me'*\n Talk to a counselor by texting *'Schedule an appointment'* \n Need resources about some course? Try *'I want study resources'* \n You can know more about the organisation by saying *'Know about organisation'*\n\n You can also trigger this message again by texting *'Help commands'*🤩"
    if langId != 'en':
        text = GoogleTranslator(source="en", target=langId).translate(text)
        
    payload = json.dumps({
        "sessionId": sessionId,
        "to": receiver,
        "from": "918904587734",
        "message": {
            "text": text
        }
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic QUlSVEVMX0RJR19MeEk4VFVLOGVLZnRCa3lQdWlmTDoxeipMVTZLTjxrenNMPytiVzM2'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

# 919820860959
