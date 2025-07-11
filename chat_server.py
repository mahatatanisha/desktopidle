from flask import Flask, request, jsonify 
import os
from dotenv import load_dotenv
import requests
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# Load environment variables from .env file
load_dotenv()

# Get the API key
openrouter_api_key = os.getenv("OPEN_ROUTER_API_KEY")



app = Flask(__name__)

# Store conversation state (in production, use a proper database)
conversation_states = {}

def format_tasks_list(tasks):
    """Format tasks into a readable string"""
    if not tasks:
        return "No tasks available."
    
    task_list = []
    for i, task in enumerate(tasks, 1):
        task_name = task.get('desc', 'Unnamed task')
        task_time = task.get('time', 'No time specified')
        task_list.append(f"{i}. {task_name} (Time: {task_time})")
    
    return "\n".join(task_list)

def get_initial_message(tasks):
    """Generate the initial bot message with tasks"""
    if not tasks:
        return "Hi there! 👋 I'm here to help you, but it looks like you don't have any tasks yet. What can I assist you with? 😊"
    
    tasks_formatted = format_tasks_list(tasks)
    return f"Hi there! 👋 Do you need any help with the following tasks? 📝\n\n{tasks_formatted}\n\nJust let me know which task you'd like help with by send text in format 'task 1' or 'task_name' , or ask me anything else! 😊"

@app.route('/ask', methods=['POST'])
def ask():
    if not request.is_json:
        return jsonify({'error': "Invalid Content-Type. Use 'application/json'."}), 415

    data = request.get_json()
    user_input = data.get('question', '')
    tasks = data.get('tasks', [])
    session_id = data.get('session_id', 'default')  # Add session tracking
    
    
    
    print(f"User input: {user_input}")
    print(f"Tasks: {tasks}")
    
    # Handle initial message (when user_input is empty or indicates start)
    if not user_input or user_input.lower() in ['start', 'init', 'hello']:
        initial_msg = get_initial_message(tasks)
        conversation_states[session_id] = {
            'stage': 'initial',
            'tasks': tasks,
            'selected_task': None
        }
        return jsonify({'reply': initial_msg})
    
    # Get or create conversation state
    if session_id not in conversation_states:
        conversation_states[session_id] = {
            'stage': 'initial',
            'tasks': tasks,
            'selected_task': None
        }
    
    state = conversation_states[session_id]
    
    # Check if user is responding to task selection
    if state['stage'] == 'initial' and tasks:
        # Check if user mentioned a task number or name
        user_lower = user_input.lower()
        selected_task = None
        
        # Check for task number (e.g., "1", "task 1", "first one")
        for i, task in enumerate(tasks, 1):
            if str(i) in user_input or f"task {i}" in user_lower:
                selected_task = task
                break
        
        # Check for task name
        if not selected_task:
            for task in tasks:
                task_name = task.get('name', '').lower()
                if task_name and task_name in user_lower:
                    selected_task = task
                    break
        
        # If a task was selected, update state and provide task-specific help
        if selected_task:
            state['selected_task'] = selected_task
            state['stage'] = 'task_selected'
            task_name = selected_task.get('name', 'your task')
            task_time = selected_task.get('time', 'No time specified')
            
            system_message = f"You are helping the user with their task: '{task_name}' (Time: {task_time}). Be helpful, concise, and encouraging. Use emojis appropriately."
            user_message = f"I need help with my task: {task_name}. The time allocated is: {task_time}. How can you help me get started or stay organized?"
        else:
            # User didn't select a task, ask for clarification
            system_message = "You are a helpful assistant. The user has tasks available but didn't specify which one they need help with. Ask them to clarify or help with their general question."
            user_message = user_input
    else:
        # Continue normal conversation
        if state.get('selected_task'):
            task_name = state['selected_task'].get('name', 'your task')
            task_time = state['selected_task'].get('time', 'No time specified')
            system_message = f"You are helping the user with their task: '{task_name}' (Time: {task_time}). Be helpful, concise, and encouraging. Use emojis appropriately."
        else:
            system_message = "You are a helpful, playful and witty assistant that always replies with humor and emojis. Be concise but helpful."
        
        user_message = user_input

    # Make API call
    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/magistral-small-2506",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 1000 
    }


    try:

        # response = conversation.run(user_input)
        # return jsonify({'reply': response})

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        response_json = response.json()

        if "choices" not in response_json:
            return jsonify({'error': "API response does not contain 'choices'.", 'details': response_json})
            
        reply = response_json["choices"][0]["message"]["content"].strip()
        return jsonify({'reply': reply})
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/reset', methods=['POST'])
def reset_conversation():
    """Reset conversation state"""
    data = request.get_json()
    session_id = data.get('session_id', 'default')
    
    if session_id in conversation_states:
        del conversation_states[session_id]
    
    return jsonify({'status': 'reset'})

if __name__ == '__main__':
    app.run(port=5005, debug=True)



