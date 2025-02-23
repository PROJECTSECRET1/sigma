from flask import Flask, request
import threading
import time

app = Flask(__name__)

# List to store found codes
found_codes = []
found_codes_lock = threading.Lock()  # Lock for thread safety

def cleanup_found_codes():
    while True:
        time.sleep(180)  # Wait for 3 minutes
        with found_codes_lock:  # Acquire the lock before modifying the list
            found_codes.clear()  # Clear the list of found codes
            print("All found codes have been cleared.")  # Log operation for debugging

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
            "timestamp": time.time()  # included for potential future use
        }

        with found_codes_lock:  # Acquire the lock before modifying the list
            found_codes.append(code_entry)

        return 'Found code received', 201

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return 'An error occurred while processing the request', 500

@app.route('/GetFoundCodes', methods=['GET'])
def get_all_codes():
    with found_codes_lock:  # Acquire the lock before reading the list
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
