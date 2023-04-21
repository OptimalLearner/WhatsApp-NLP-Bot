import requests
import json
from api.uploadMedia import uploadMedia
from deep_translator import GoogleTranslator

url = "https://iqwhatsapp.airtel.in:443/gateway/airtel-xchange/basic/whatsapp-manager/v1/template/send"

def sendPromotion(receiver, langId, courseName, courseLink):
    text1 = "Hey I am Chabo! We have a brand new course called *"
    text2 = "* which is extremely popular in the industry!🤩 You can visit this link "
    text3 = " for more details!🚀"
    if langId != 'en':
        text1 = GoogleTranslator(source="en", target=langId).translate(text1)
        text2 = GoogleTranslator(source="en", target=langId).translate(text2)
        text3 = GoogleTranslator(source="en", target=langId).translate(text3)
        
    text = text1+courseName+text2+courseLink+text3
    mediaId, mediaType = uploadMedia('courseraPromotion.jpg', 'static/helpMedia/courseraPromotion.jpg', 'jpg')
    print(mediaId, mediaType)
    
    payload = json.dumps({
      "templateId": "c43c4f50-64f3-4130-b28d-c0d3faa341aa",
      "to": receiver,
      "from": "918904587734",
      "message": {
        "variables": [
          text
        ]
      },
      "mediaAttachment": {
        "type": "IMAGE",
        "id": mediaId
      },
      "filterBlacklistNumbers": False
    })
    headers = {
      'X-Correlation-Id': 'abcd',
      'X-Date': '{{date}}',
      'Authorization': 'Basic QUlSVEVMX0RJR19MeEk4VFVLOGVLZnRCa3lQdWlmTDoxeipMVTZLTjxrenNMPytiVzM2',
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
