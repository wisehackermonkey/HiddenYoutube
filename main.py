#!/usr/bin/env python3
# HiddenYoutube Source Code
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests
import random
import string
# import env
import os
"""
import env
env.YOUTUBE_API_KEY
"""
app = Flask(__name__)
CORS(app)

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY") # or env.YOUTUBE_API_KEY

def generate_video_id():
    chars = string.ascii_letters + string.digits + '-_'
    return ''.join(random.choice(chars) for _ in range(11))

def generate_mock_videos(query, count=15):
    videos = []
    for i in range(count):
        view_count = 0 if random.random() < 0.3 else random.randint(1, 10000)
        videos.append({
            'id': generate_video_id(),
            'title': query + (f' ({random.randint(1, 100)})' if random.random() > 0.7 else ''),
            'viewCount': view_count,
            'channelName': f'User{random.randint(1000, 9999)}'
        })
    return videos

@app.route('/')
def index():
    with open('index.html', 'r') as f:
        return f.read()

@app.route('/api/search', methods=['POST'])
def search_videos():
    data = request.get_json()
    query = data.get('query', '')
    
    try:
        url = 'https://www.googleapis.com/youtube/v3/search'
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'maxResults': 20,
            'key': YOUTUBE_API_KEY
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            youtube_data = response.json()
            video_ids = [item['id']['videoId'] for item in youtube_data['items']]
            
            stats_url = 'https://www.googleapis.com/youtube/v3/videos'
            stats_params = {
                'part': 'statistics',
                'id': ','.join(video_ids),
                'key': YOUTUBE_API_KEY
            }
            
            stats_response = requests.get(stats_url, params=stats_params)
            stats_data = stats_response.json()
            
            videos = []
            for item, stats in zip(youtube_data['items'], stats_data['items']):
                view_count = int(stats['statistics'].get('viewCount', 0))
                videos.append({
                    'id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'viewCount': view_count,
                    'channelName': item['snippet']['channelTitle']
                })
            
            return jsonify({'videos': videos})
        else:
            return jsonify({'videos': generate_mock_videos(query)})
            
    except Exception as e:
        return jsonify({'videos': generate_mock_videos(query)})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port="80", debug=False)