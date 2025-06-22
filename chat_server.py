from flask import Flask, request, jsonify 
import os
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Get the API key
openrouter_api_key = os.getenv("OPENAI_API_KEY")

# Use the API key in your code


app = Flask(__name__)

@app.route('/ask', methods=['POST'])
def ask():
    if not request.is_json:
        return jsonify({'error': "Invalid Content-Type. Use 'application/json'."}), 415

    data = request.get_json()
      # Debugging line to see incoming data
    user_input = data.get('question', '')
    
    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/magistral-small-2506",  # Adjust model name based on availability
        "messages": [
            {"role": "system", "content": "Respond concisely. One-line answers only."},
            {"role": "user", "content": user_input}],
        "max_tokens": 1000 
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        response_json = response.json()

        if "choices" not in response_json:
            return jsonify({'error': "API response does not contain 'choices'.", 'details': response_json})
            

        reply = response_json["choices"][0]["message"]["content"].strip()
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'error': str(e)})



if __name__ == '__main__':
    app.run(port=5005)
