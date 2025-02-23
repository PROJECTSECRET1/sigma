from flask import Flask, request
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

        code_entry = {
            "item_name": item_name,
            "room_code": room_code,
            "timestamp": time.time()  
        }

        found_codes.append(code_entry)
        return 'Found code received', 201

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return 'An error occurred while processing the request', 500

@app.route('/GetFoundCodes', methods=['GET'])
def get_all_codes():
    # Return found codes as plain text
    if not found_codes:
        return 'No found codes available', 200  # Return plain text for no found codes

    response_lines = []

    for code in found_codes:
        entry = f"Item Name: {code['item_name']}, Room Code: {code['room_code']}"
        response_lines.append(entry)  # Create a formatted string for each entry

    return '\n'.join(response_lines), 200  # Join each entry with a newline character

if __name__ == '__main__':
    # Start the cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_found_codes, daemon=True)
    cleanup_thread.start()
    
    app.run(debug=False)  # Set debug to False to avoid unnecessary output formats
