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
        
    item_name = data.get("item_name")
    room_code = data.get("room_code")
    player_count = data.get("player_count")
    region = data.get("region")
    board_position = data.get("board_position")

    # Create a code entry
    code_entry = {
        "item_name": item_name,
        "room_code": room_code,
        "nickname": nickname,
        "player_count": player_count,
        "region": region,
        "board_position": board_position
    }

    # Append to the found codes list
    found_codes.append(code_entry)

    return jsonify(message='Found code received', code_entry=code_entry), 201

@app.route('/GetFoundCodes', methods=['GET'])
def get_all_codes():
    return jsonify(found_codes=found_codes), 200

if __name__ == '__main__':
    app.run(debug=True)
