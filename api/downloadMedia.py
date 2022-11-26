import requests


def getMedia(mediaId):
    url = "https://iqwhatsapp.airtel.in:443/gateway/airtel-xchange/basic/whatsapp-manager/v1/download/media?mediaId="+mediaId+"&businessId=Hackathon3_8904587734"

    payload={}
    headers = {
        'Authorization': 'Basic QUlSVEVMX0RJR19MeEk4VFVLOGVLZnRCa3lQdWlmTDoxeipMVTZLTjxrenNMPytiVzM2'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)
    return response