from flask import Flask, request, jsonify 
import openai
import os
from dotenv import load_dotenv
import ssl
import certifi

# Load environment variables from .env file
load_dotenv()

# Get the API key
openai_api_key = os.getenv("OPENAI_API_KEY")

# Use the API key in your code
openai.api_key = openai_api_key

app = Flask(__name__)

@app.route('/ask', methods=['POST'])
def ask():
    if not request.is_json:
        return jsonify({'error': "Invalid Content-Type. Use 'application/json'."}), 415

    data = request.get_json()
    user_input = data.get('question', '')

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": user_input}],
            
        )
        reply = response.choices[0].message.content  # ✅ Updated format
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(port=5005)
