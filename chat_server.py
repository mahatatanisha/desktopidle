from flask import Flask, request, jsonify
import openai

openai.api_key = 'your_openai_api_key'

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
