from flask import Flask, jsonify, request
import threading
import time

app = Flask(__name__)

# List to store found codes, each with a timestamp
found_codes = []

def cleanup_found_codes():
    while True:
        current_time = time.time()
        global found_codes
        # Delete codes older than 60 seconds
        found_codes = [code for code in found_codes if (current_time - code['timestamp']) < 60]
        time.sleep(10)  # Check every 10 seconds

@app.route('/')
def home():
    return jsonify(message='Hello, World!')

@app.route('/about')
def about():
    return jsonify(message='About')

@app.route('/GetFoundCodes', methods=['POST'])
def getcodes():
    data = request.get_json()
    if not data:
        return jsonify(message='No data provided'), 400

    try:
        item_name = data.get("item_name")
        room_code = data.get("room_code")
        player_count = data.get("player_count")
        region = data.get("region")
        board_position = data.get("board_position")

        required_fields = [item_name, room_code, player_count, region, board_position]
        if any(field is None for field in required_fields):
            return jsonify(message='Missing required fields'), 400

        # Create a code entry with a timestamp
        code_entry = {
            "item_name": item_name,
            "room_code": room_code,
            "player_count": player_count,
            "region": region,
            "board_position": board_position,
            "timestamp": time.time()  # Save the current timestamp
        }

        found_codes.append(code_entry)

        return jsonify(message='Found code received', code_entry=code_entry), 201

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify(message='An error occurred while processing the request'), 500

@app.route('/GetFoundCodes', methods=['GET'])
def get_all_codes():
    response_lines = []

    # Construct the desired response
    for code in found_codes:
        entry = {
            "board_position": code['board_position'],
            "item_name": code['item_name'],
            "player_count": code['player_count'],
            "region": code['region'],
            "room_code": code['room_code']
        }
        response_lines.append(entry)
    
    # If no codes are found, return a message
    if not response_lines:
        return jsonify(found_codes=[]), 200
    
    return jsonify(found_codes=response_lines), 200  # Return codes as JSON objects in an array

if __name__ == '__main__':
    # Start the cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_found_codes, daemon=True)
    cleanup_thread.start()
    
    app.run(debug=True)
