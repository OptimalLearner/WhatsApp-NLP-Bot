# import OS for environment variables
import os
import requests
import json
import re

def chabo_search(query_text):

    # query_text = re.sub(r'.', '', query_text, count = 6)

    print(query_text)

    Chabo_API_Key =  os.environ['Chabo_API_KEY']
    faultyText = "No results found! Please check your input once again!"
    print('>>>> Query text', query_text)
    if query_text == '':
        return faultyText
    
    url = "https://api.openai.com/v1/chat/completions"

    payload = json.dumps({
    "model": "gpt-3.5-turbo-0301",
    "messages": [
        {
        "role": "system",
        "content": query_text
        }
    ]
    })

    headers = {
    'Authorization': 'Bearer ' + Chabo_API_Key,
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    answer = json.loads(response.text)
    # print(response.text)
    print(answer['choices'][0]['message']['content'])
 
    return answer['choices'][0]['message']['content']
