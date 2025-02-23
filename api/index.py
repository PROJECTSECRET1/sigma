from flask import Flask, request, jsonify
from threading import Lock
import json
import os
import logging
from functools import wraps
from time import time

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

# List to store found codes
found_codes = []
lock = Lock()  # Lock for thread-safe access to found_codes

# Dictionary to store keys and their associated HWIDs
keys = {}
key_lock = Lock()  # Lock for thread-safe access to keys

# Rate limiting configuration
RATE_LIMIT = 10  # Number of requests allowed
TIME_WINDOW = 60  # Time frame in seconds
timestamps = {}

def rate_limiter(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = request.remote_addr  # The user ID can be replaced with a more reliable identifier
        current_time = time()
        
        # Initialize timestamps
        if user_id not in timestamps:
            timestamps[user_id] = []

        # Filter out timestamps outside the time window
        timestamps[user_id] = [ts for ts in timestamps[user_id] if current_time - ts < TIME_WINDOW]

        if len(timestamps[user_id]) < RATE_LIMIT:
            timestamps[user_id].append(current_time)  # Log this request timestamp
            return func(*args, **kwargs)
        else:
            return jsonify({"error": "Rate limit exceeded"}), 429  # Too Many Requests
    return wrapper

@app.route('/', methods=['GET'])
def home():
    return 'Hello, World!'

@app.route('/about', methods=['GET'])
def about():
    return 'About'

@app.route('/GetFoundCodes', methods=['POST'])
@rate_limiter
def get_codes():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    item_name = data.get("item_name")
    room_code = data.get("room_code")

    if item_name is None or room_code is None:
        return jsonify({'error': 'Missing required fields'}), 400

    # Append the code entry in a thread-safe manner
    with lock:
        code_entry = {"Item In Code": item_name, "Code": room_code}
        found_codes.append(code_entry)

    return '', 201

@app.route('/GetFoundCodes', methods=['GET'])
@rate_limiter
def get_all_codes():
    with lock:
        if not found_codes:
            return jsonify('No found codes available'), 200

        return jsonify(found_codes), 200  # Return as JSON

@app.route('/clearFoundCodes', methods=['GET'])
@rate_limiter
def clear_found_codes():
    with lock:
        found_codes.clear()
    return 'Found codes cleared', 200

@app.route('/create_key', methods=['POST'])
@rate_limiter
def create_key():
    key = request.json.get('key')
    
    if not key:
        return jsonify({'error': 'Key is required'}), 400

    with key_lock:
        keys[key] = None  # Initialize the key with no HWID
    return jsonify({'message': f'Key {key} created.'}), 201

@app.route('/verify_key', methods=['POST'])
@rate_limiter
def verify_key():
    data = request.get_json()
    key = data.get('key')
    hwid = data.get('hwid')

    if not key or not hwid:
        return jsonify({'error': 'Key and HWID are required'}), 400

    with key_lock:
        if key not in keys:
            return jsonify({'error': 'Key not found'}), 404

        keys[key] = hwid  # Assign the HWID to the key
        return jsonify({'message': f'HWID for {key} set to {hwid}.'}), 200

@app.route('/delete_key/<key>', methods=['DELETE'])
@rate_limiter
def delete_key(key):
    with key_lock:
        if key in keys:
            del keys[key]
            return jsonify({'message': f'Key {key} deleted'}), 200
        else:
            return jsonify({'error': 'Key not found'}), 404

@app.route('/resethwid/<key>', methods=['PUT'])
@rate_limiter
def reset_hwid(key):
    new_hwid = request.json.get('hwid')

    with key_lock:
        if key not in keys:
            return jsonify({'error': 'Key not found'}), 404
        
        if not new_hwid:
            return jsonify({'error': 'New HWID is required'}), 400
        
        keys[key] = new_hwid
        return jsonify({'message': f'HWID for {key} reset to {new_hwid}'}), 200

if __name__ == "__main__":
    app.run(debug=False, port=5001, use_reloader=False)
