from flask import Flask, jsonify, request

app = Flask(__name__)

# List to store found codes
found_codes = []

@app.route('/')
def home():
    return jsonify(message='Hello, World!')

@app.route('/about')
def about():
    return jsonify(message='About')

@app.route('/GetFoundCodes', methods=['POST'])
def getcodes():
    # Check if the request has JSON data
    data = request.get_json()
    if not data:
        return jsonify(message='No data provided'), 400

    # Try to extract code attributes from incoming JSON payload
    try:
        item_name = data.get("item_name")
        room_code = data.get("room_code")
        player_count = data.get("player_count")
        region = data.get("region")
        board_position = data.get("board_position")

        # Validate required fields (excluding nickname)
        required_fields = [item_name, room_code, player_count, region, board_position]
        if any(field is None for field in required_fields):
            return jsonify(message='Missing required fields'), 400

        # Create a code entry without the nickname
        code_entry = {
            "item_name": item_name,
            "room_code": room_code,
            "player_count": player_count,
            "region": region,
            "board_position": board_position
        }

        # Append to the found codes list
        found_codes.append(code_entry)

        return jsonify(message='Found code received', code_entry=code_entry), 201

    except Exception as e:
        # Log the exact error for debugging
        print(f"Error processing request: {str(e)}")
        return jsonify(message='An error occurred while processing the request'), 500

@app.route('/GetFoundCodes', methods=['GET'])
def get_all_codes():
    return jsonify(found_codes=found_codes), 200

if __name__ == '__main__':
    app.run(debug=True)
