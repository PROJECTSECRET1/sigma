from flask import Flask, request
from threading import Lock

app = Flask(__name__)

# List to store found codes
found_codes = []
lock = Lock()  # Lock for thread-safe access to found_codes

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'

@app.route('/GetFoundCodes', methods=['POST'])
def getcodes():
    data = request.get_json()
    if not data:
        return 'No data provided', 400

    try:
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

    except Exception as e:
        return 'An error occurred while processing the request', 500

@app.route('/GetFoundCodes', methods=['GET'])
def get_all_codes():
    with lock:
        if not found_codes:
            return 'No found codes available', 200

        response_lines = []
        for code in found_codes:
            response_lines.append(f"Item Name: {code['item_name']}, Room Code: {code['room_code']}")
        
        return '\n'.join(response_lines), 200

@app.route('/clearFoundCodes', methods=['GET'])
def clear_found_codes():
    with lock:
        found_codes.clear()
    return 'Found codes cleared', 200

if __name__ == "__main__":
    app.run(debug=True, port=5001, use_reloader=False)
