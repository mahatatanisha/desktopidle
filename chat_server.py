from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key
openai_api_key = os.getenv("OPENAI_API_KEY")

# Use the API key in your code
openai.api_key = openai_api_key

app = Flask(__name__)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    user_input = data.get('question', '')

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or gpt-4
            messages=[{"role": "user", "content": user_input}]
        )
        reply = response['choices'][0]['message']['content']
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(port=5005)
