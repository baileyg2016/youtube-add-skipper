from flask import Flask, request, jsonify
from flask_cors import CORS
from engine import AdsEngine

app = Flask(__name__)
CORS(app, origins=['chrome-extension://*'])

@app.route('/', methods=['POST'])
def receive_data():
    data = request.get_json()
    youtube_url = data.get('youtube_url', None)
    if youtube_url:
        print(f"Received YouTube URL: {youtube_url}")
        engine = AdsEngine(youtube_url)
        ads = engine()
        return jsonify({'success': True, 'ads': ads})
    else:
        return jsonify({'success': False, 'error': 'YouTube URL not found in the request data'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
