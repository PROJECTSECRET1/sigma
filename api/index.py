from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify(message='Hello, World!')

@app.route('/about')
def about():
    return jsonify(message='About')

if __name__ == '__main__':
    app.run(debug=True)
