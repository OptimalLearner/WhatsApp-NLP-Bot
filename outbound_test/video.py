# import OS for environment variables
import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()


url = "https://iqwhatsapp.airtel.in:443/gateway/airtel-xchange/basic/whatsapp-manager/v1/session/send/text"
YOUTUBE_API_KEY='AIzaSyArfrE-f5WsH4BjguwU1QAWnQWrEiOzFMQ'

def youtube():
    search_url = 'https://www.googleapis.com/youtube/v3/search'
    video_url = 'https://www.googleapis.com/youtube/v3/videos'

    videos = []

    search_params = {
        'key' : YOUTUBE_API_KEY,
        'q' : 'Plants',
        'part' : 'snippet',
        'maxResults' : 4,
        'type' : 'video'
    }

    r = requests.get(search_url, params=search_params)

    results = r.json()['items']

    video_ids = []
    for result in results:
        video_ids.append(result['id']['videoId'])


    video_params = {
        'key' : YOUTUBE_API_KEY,
        'id' : ','.join(video_ids),
        'part' : 'snippet,contentDetails',
        'maxResults' : 4
    }

    r = requests.get(video_url, params=video_params)
    results = r.json()['items']
    print(results[0])
    for result in results:
          
        video_data = {
            'id' : result['id'],
            'url' : f'https://www.youtube.com/watch?v={ result["id"] }',
            'thumbnail' : result['snippet']['thumbnails']['high']['url'],
            'duration' : 0,
            'title' : result['snippet']['title'],
        }
        videos.append(video_data)
        
    for video in videos:
        
        payload = json.dumps({
          "sessionId": "5792547f57a44b358d3f1425dc163b7f",
          "to": "919960855675",
          "from": "918904587734",
          "message": {
            "text": video['title']  + '\n' + video['url']
          }
        })
        headers = {
          'Content-Type': 'application/json',
          'Authorization': 'Basic QUlSVEVMX0RJR19MeEk4VFVLOGVLZnRCa3lQdWlmTDoxeipMVTZLTjxrenNMPytiVzM2'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response)

youtube()

