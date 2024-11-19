from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import requests

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

project_images = []
generated_images=[]
@app.route('/generate-image', methods=['POST'])
def generate_image():
    data = request.json
    api_url = 'https://modelslab.com/api/v6/realtime/text2img'
    payload = {
        "key": "lf3m2E38YbTynWLwYVUZcPjfcYPJ2VUmpGi67qBo7MAFdreTMpF4DYSV35i1",
        "prompt": data.get("prompt", "A house blueprint with 3 bedrooms"),
        "negative_prompt": "bad quality",
        "width": "512",
        "height": "512",
        "safety_checker": False,
        "seed": None,
        "samples": 1,
        "base64": False,
        "webhook": None,
        "track_id": None
    }

    try:
        response = requests.post(api_url, json=payload, headers={'Content-Type': 'application/json'})
        response_data = response.json()
        img_url=response_data["output"][0]
        generated_images.append(img_url)
        socketio.emit('new_image', {"url": img_url})
        print("Response from API:", response_data) 
        return jsonify({"output": response_data["output"][0]})
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)})


@app.route('/modify-image',methods=['POST'])
def modify_image():
    data = request.json
    api_url = 'https://modelslab.com/api/v6/realtime/img2img'
    init_image = data.get("init_image")
    if not init_image:
        return jsonify({"error": "Initial image is required"})
    payload = {
        "key": "lf3m2E38YbTynWLwYVUZcPjfcYPJ2VUmpGi67qBo7MAFdreTMpF4DYSV35i1",  
        "prompt": data.get("prompt", "A modified image"),
        "negative_prompt": "bad quality",
        "init_image": init_image,
        "width": "512",
        "height": "512",
        "samples": "1",
        "temp": False,
        "safety_checker": False,
        "strength": 0.7,
        "seed": None,
        "webhook": None,
        "track_id": None
    }
    try:
        response = requests.post(api_url, json=payload, headers={'Content-Type': 'application/json'})
        response_data = response.json()
        img_url = response_data["output"][0] 
        generated_images.append(img_url) 
        socketio.emit('new_image', {"url": img_url})
        return jsonify({"output": img_url})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/gallery',methods=['GET'])
def get_gallery_images():
    print("Generated Images:", generated_images)
    return jsonify(generated_images)
if __name__ == '__main__':
    app.run(debug=True)
