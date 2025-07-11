from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain_community.callbacks.manager import get_openai_callback
import json

# Load environment variables from .env file
load_dotenv()

# Get the API key
openrouter_api_key = os.getenv("OPEN_ROUTER_API_KEY")

app = Flask(__name__)

# Store conversation memories and states (in production, use a proper database)
conversation_memories = {}
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

def get_or_create_memory(session_id):
    """Get or create conversation memory for a session"""
    if session_id not in conversation_memories:
        conversation_memories[session_id] = ConversationBufferMemory(
            return_messages=True,
            memory_key="history"
        )
    return conversation_memories[session_id]

def get_or_create_llm(session_id):
    """Get or create LLM instance for a session"""
    llm = ChatOpenAI(
        model="mistralai/magistral-small-2506",
        openai_api_key=openrouter_api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        max_tokens=1000,
        temperature=0.7
    )
    return llm

def create_conversation_chain(session_id, system_message):
    """Create a conversation chain with memory"""
    memory = get_or_create_memory(session_id)
    llm = get_or_create_llm(session_id)
    
    # Create a custom prompt template that includes system message
    prompt = PromptTemplate(
        input_variables=["history", "input"],
        template=f"{system_message}\n\nConversation History:\n{{history}}\n\nUser: {{input}}\nAssistant:"
    )
    
    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        prompt=prompt,
        verbose=True
    )
    
    return conversation

@app.route('/ask', methods=['POST'])
def ask():
    if not request.is_json:
        return jsonify({'error': "Invalid Content-Type. Use 'application/json'."}), 415
    
    data = request.get_json()
    user_input = data.get('question', '')
    tasks = data.get('tasks', [])
    session_id = data.get('session_id', 'default')
    
    print(f"User input: {user_input}")
    print(f"Tasks: {tasks}")
    print(f"Session ID: {session_id}")
    
    # Handle initial message (when user_input is empty or indicates start)
    if not user_input or user_input.lower() in ['start', 'init', 'hello']:
        initial_msg = get_initial_message(tasks)
        
        # Initialize conversation state
        conversation_states[session_id] = {
            'stage': 'initial',
            'tasks': tasks,
            'selected_task': None
        }
        
        # Initialize memory with system message
        memory = get_or_create_memory(session_id)
        memory.chat_memory.add_ai_message(initial_msg)
        
        return jsonify({'reply': initial_msg})
    
    # Get or create conversation state
    if session_id not in conversation_states:
        conversation_states[session_id] = {
            'stage': 'initial',
            'tasks': tasks,
            'selected_task': None
        }
    
    state = conversation_states[session_id]
    
    # Determine system message based on current state
    system_message = "You are a helpful, playful and witty assistant that always replies with humor and emojis. Be concise but helpful."
    
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
        else:
            # User didn't select a task, ask for clarification
            system_message = "You are a helpful assistant. The user has tasks available but didn't specify which one they need help with. Ask them to clarify or help with their general question."
    
    elif state.get('selected_task'):
        # Continue with task-specific assistance
        task_name = state['selected_task'].get('name', 'your task')
        task_time = state['selected_task'].get('time', 'No time specified')
        system_message = f"You are helping the user with their task: '{task_name}' (Time: {task_time}). Be helpful, concise, and encouraging. Use emojis appropriately."
    
    try:
        # Create conversation chain with memory
        conversation = create_conversation_chain(session_id, system_message)
        
        # Get response from LangChain
        with get_openai_callback() as cb:
            response = conversation.predict(input=user_input)
            print(f"Tokens used: {cb.total_tokens}")
        
        return jsonify({
            'reply': response,
            'tokens_used': cb.total_tokens if 'cb' in locals() else None
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset_conversation():
    """Reset conversation state and memory"""
    data = request.get_json()
    session_id = data.get('session_id', 'default')
    
    # Clear conversation state
    if session_id in conversation_states:
        del conversation_states[session_id]
    
    # Clear conversation memory
    if session_id in conversation_memories:
        del conversation_memories[session_id]
    
    return jsonify({'status': 'reset'})

@app.route('/history', methods=['GET'])
def get_conversation_history():
    """Get conversation history for a session"""
    session_id = request.args.get('session_id', 'default')
    
    if session_id not in conversation_memories:
        return jsonify({'history': []})
    
    memory = conversation_memories[session_id]
    messages = memory.chat_memory.messages
    
    # Convert messages to a serializable format
    history = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            history.append({'role': 'user', 'content': msg.content})
        elif isinstance(msg, AIMessage):
            history.append({'role': 'assistant', 'content': msg.content})
    
    return jsonify({'history': history})

@app.route('/save_memory', methods=['POST'])
def save_memory():
    """Save conversation memory to file (for persistence)"""
    data = request.get_json()
    session_id = data.get('session_id', 'default')
    
    if session_id not in conversation_memories:
        return jsonify({'error': 'No memory found for session'}), 404
    
    memory = conversation_memories[session_id]
    
    # Create a directory for storing memories if it doesn't exist
    os.makedirs('memories', exist_ok=True)
    
    # Save memory to file
    memory_file = f'memories/{session_id}_memory.json'
    messages = []
    for msg in memory.chat_memory.messages:
        if isinstance(msg, HumanMessage):
            messages.append({'role': 'user', 'content': msg.content})
        elif isinstance(msg, AIMessage):
            messages.append({'role': 'assistant', 'content': msg.content})
    
    with open(memory_file, 'w') as f:
        json.dump(messages, f, indent=2)
    
    return jsonify({'status': 'saved', 'file': memory_file})

@app.route('/load_memory', methods=['POST'])
def load_memory():
    """Load conversation memory from file"""
    data = request.get_json()
    session_id = data.get('session_id', 'default')
    
    memory_file = f'memories/{session_id}_memory.json'
    
    if not os.path.exists(memory_file):
        return jsonify({'error': 'Memory file not found'}), 404
    
    try:
        with open(memory_file, 'r') as f:
            messages = json.load(f)
        
        # Create new memory and populate it
        memory = ConversationBufferMemory(return_messages=True, memory_key="history")
        
        for msg in messages:
            if msg['role'] == 'user':
                memory.chat_memory.add_user_message(msg['content'])
            elif msg['role'] == 'assistant':
                memory.chat_memory.add_ai_message(msg['content'])
        
        conversation_memories[session_id] = memory
        
        return jsonify({'status': 'loaded', 'messages_count': len(messages)})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5005, debug=True)