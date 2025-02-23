from flask import Flask, request
from threading import Lock
import json

app = Flask(__name__)

# List to store found codes
found_codes = []
lock = Lock()  # Lock for thread-safe access to found_codes

# Dictionary to store keys and their associated HWIDs
keys = {}
key_lock = Lock()  # Lock for thread-safe access to keys

@app.route('/', methods=['GET'])
def home():
    return 'Hello, World!'

@app.route('/about', methods=['GET'])
def about():
    return 'About'

@app.route('/GetFoundCodes', methods=['POST'])
def get_codes():
    data = request.get_json()
    if not data:
        return 'No data provided', 400

    item_name = data.get("item_name")
    room_code = data.get("room_code")

    if item_name is None or room_code is None:
        return 'Missing required fields', 400

    # Append the code entry in a thread-safe manner
    with lock:
        code_entry = {
            "item_name": item_name,
            "room_code": room_code,
        }
        found_codes.append(code_entry)

    return '', 201

@app.route('/GetFoundCodes', methods=['GET'])
def get_all_codes():
    with lock:
        if not found_codes:
            return 'No found codes available', 200

        response_lines = [f"Item Name: {code['item_name']}, Room Code: {code['room_code']}" for code in found_codes]
        return json.dumps(response_lines), 200  # Return as JSON

@app.route('/clearFoundCodes', methods=['GET'])
def clear_found_codes():
    with lock:
        found_codes.clear()
    return 'Found codes cleared', 200

# Endpoint to create a new key
@app.route('/create_key', methods=['POST'])
def create_key():
    key = request.json.get('key')
    
    if not key:
        return 'Key is required', 400

    with key_lock:
        keys[key] = None  # Initialize the key with no HWID
    return f'Key {key} created.', 201

# Endpoint to verify key and set HWID
@app.route('/verify_key', methods=['GET'])
def verify_key():
    key = request.json.get('key')
    hwid = request.json.get('hwid')

    if not key or not hwid:
        return 'Key and HWID are required', 400

    with key_lock:
        if key not in keys:
            return 'Key not found', 404

        keys[key] = hwid  # Assign the HWID to the key
        return f'HWID for {key} set to {hwid}.', 200

# Endpoint to delete a key
@app.route('/delete_key/<key>', methods=['DELETE'])
def delete_key(key):
    with key_lock:
        if key in keys:
            del keys[key]
            return f'Key {key} deleted', 200
        else:
            return 'Key not found', 404

# Endpoint to reset HWID for a specific key
@app.route('/resethwid/<key>', methods=['PUT'])
def reset_hwid(key):
    new_hwid = request.json.get('hwid')
    
    with key_lock:
        if key not in keys:
            return 'Key not found', 404
        
        if not new_hwid:
            return 'New HWID is required', 400
        
        keys[key] = new_hwid
        return f'HWID for {key} reset to {new_hwid}', 200

if __name__ == "__main__":
    app.run(debug=True, port=5001, use_reloader=False)
