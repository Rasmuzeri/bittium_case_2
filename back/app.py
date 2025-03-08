from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS to allow requests from your frontend

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400

    user_message = data['message']
    
    # Simulate a bot response (replace this with your LLM integration)
    bot_response = f"Backend response to: \"{user_message}\""
    
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True)
