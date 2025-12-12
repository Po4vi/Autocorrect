import os
import json
import re
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import requests
from dotenv import load_dotenv
from datetime import timedelta
from collections import deque

load_dotenv()

app = Flask(__name__, static_folder='public', static_url_path='', template_folder='public')
CORS(app)
app.secret_key = 'autocorrect-chatbot-secret-key-2025'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
API_URL = 'https://openrouter.ai/api/v1/chat/completions'

# Load dictionary
with open('dictionary.json', 'r') as f:
    dictionary = set(json.load(f))

# Session conversation storage (in-memory, can be replaced with database)
conversation_history = {}

def levenshtein_distance(a, b):
    """Calculate edit distance between two strings"""
    if len(a) < len(b):
        return levenshtein_distance(b, a)
    
    if len(b) == 0:
        return len(a)
    
    previous_row = range(len(b) + 1)
    for i, c1 in enumerate(a):
        current_row = [i + 1]
        for j, c2 in enumerate(b):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def get_suggestions(word, max_distance=2):
    """Get spelling suggestions for a word"""
    suggestions = []
    
    for dict_word in list(dictionary)[:1000]:  # Check first 1000 words for performance
        distance = levenshtein_distance(word, dict_word)
        if 0 < distance <= max_distance:
            suggestions.append((dict_word, distance))
    
    suggestions.sort(key=lambda x: x[1])
    return [word for word, _ in suggestions[:5]]

def check_spelling(text):
    """Check spelling in text"""
    words = re.findall(r'\b\w+\b', text.lower())
    errors = []
    
    for i, word in enumerate(words):
        if word not in dictionary:
            errors.append({
                'word': word,
                'position': i,
                'suggestions': get_suggestions(word)
            })
    
    return errors

def generate_corrected_sentence(original_text, spelling_errors):
    """Generate a corrected version of the sentence using best suggestions"""
    if not spelling_errors:
        return original_text
    
    corrected = original_text
    
    # Sort errors by position (reverse) to replace from end to start (preserve positions)
    sorted_errors = sorted(spelling_errors, key=lambda x: x['position'], reverse=True)
    
    for error in sorted_errors:
        if error['suggestions']:
            # Use the first (best) suggestion
            best_suggestion = error['suggestions'][0]
            wrong_word = error['word']
            
            # Replace the wrong word with the best suggestion
            regex = re.compile(re.escape(wrong_word), re.IGNORECASE)
            corrected = regex.sub(best_suggestion, corrected, count=1)
    
    return corrected

@app.route('/')
def index():
    """Serve the chat interface"""
    return app.send_static_file('index.html')

def get_session_id():
    """Get or create session ID"""
    session.permanent = True
    if 'session_id' not in session:
        import uuid
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

def get_conversation(session_id):
    """Get conversation history for session"""
    if session_id not in conversation_history:
        conversation_history[session_id] = {
            'messages': deque(maxlen=50),  # Keep last 50 messages
            'metadata': {'created': str(os.times())}
        }
    return conversation_history[session_id]

def trim_conversation_for_api(messages, max_tokens=3000):
    """
    Trim conversation to fit within API token limits while keeping context.
    Keeps system message + last N messages that fit within token budget.
    Rough estimate: 1 token ≈ 4 characters
    """
    messages_to_send = []
    token_count = 0
    max_message_tokens = max_tokens - 500  # Reserve 500 tokens for response
    
    # Always include system message
    if messages and messages[0].get('role') == 'system':
        messages_to_send.append(messages[0])
        token_count += len(messages[0]['content']) // 4
    
    # Add messages from most recent, going backwards
    for msg in reversed(messages[1:]):
        msg_tokens = len(msg['content']) // 4
        if token_count + msg_tokens < max_message_tokens:
            messages_to_send.insert(1, msg)  # Insert after system message
            token_count += msg_tokens
        else:
            break
    
    return messages_to_send

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint with spell-checking, conversation memory, and OpenRouter API"""
    try:
        data = request.json
        message = data.get('message', '').strip()
        clear_history = data.get('clearHistory', False)
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get or create session
        session_id = get_session_id()
        conversation = get_conversation(session_id)
        
        # Clear history if requested
        if clear_history:
            conversation['messages'].clear()
            return jsonify({
                'message': 'Conversation cleared. Starting fresh!',
                'spellingErrors': [],
                'thinking': 'Conversation history cleared'
            })
        
        # Check spelling
        spelling_errors = check_spelling(message)
        
        # Generate corrected sentence
        corrected_sentence = generate_corrected_sentence(message, spelling_errors)
        
        # Determine if user is asking about spelling/grammar or having general conversation
        is_spell_check_query = any(word in message.lower() for word in 
            ['correct', 'fix', 'mistake', 'error', 'wrong', 'spell', 'grammar', 'check'])
        
        # Build system prompt based on query type
        if is_spell_check_query or spelling_errors:
            system_prompt = """You are "Think", an intelligent writing assistant focused on helping users improve their writing.

When users ask about corrections or have spelling errors:
1. Analyze their text professionally
2. Explain errors clearly and educationally
3. Suggest improvements with reasoning
4. Be encouraging and supportive

When having general conversation:
1. Be helpful, friendly, and conversational
2. Answer questions naturally
3. Maintain context from previous messages
4. Provide thoughtful responses

Keep responses concise and clear."""
        else:
            system_prompt = """You are "Think", a friendly and intelligent AI assistant.

Your personality:
- Helpful and conversational
- Clear and concise
- Knowledgeable across many topics
- Remembers conversation context
- Professional yet approachable

Respond naturally to user questions and maintain engaging conversation."""
        
        # Prepare user message (clean, without system annotations for better conversation flow)
        user_message = message
        
        # Build messages array with conversation history
        messages = [{'role': 'system', 'content': system_prompt}]
        
        # Add previous conversation messages
        for msg in conversation['messages']:
            messages.append(msg)
        
        # Add current user message
        messages.append({'role': 'user', 'content': user_message})
        
        # Trim conversation to fit API limits
        trimmed_messages = trim_conversation_for_api(messages)
        
        # Call OpenRouter API
        headers = {
            'Authorization': f'Bearer {OPENROUTER_API_KEY}',
            'HTTP-Referer': 'http://localhost:5000',
            'X-Title': 'Autocorrect Chatbot'
        }
        
        payload = {
            'model': 'openai/gpt-3.5-turbo',
            'messages': trimmed_messages,
            'temperature': 0.7,
            'max_tokens': 500,
            'top_p': 0.9
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        result = response.json()
        
        if response.status_code != 200:
            error_msg = result.get('error', {}).get('message', 'Unknown error')
            return jsonify({'error': f'API Error: {error_msg}'}), 500
        
        ai_response = result['choices'][0]['message']['content']
        
        # Store conversation in history
        conversation['messages'].append({'role': 'user', 'content': message})
        conversation['messages'].append({'role': 'assistant', 'content': ai_response})
        
        return jsonify({
            'message': ai_response,
            'spellingErrors': spelling_errors,
            'correctedSentence': corrected_sentence,
            'hasSpellingErrors': len(spelling_errors) > 0,
            'isSpellCheckMode': is_spell_check_query or len(spelling_errors) > 0,
            'thinking': f'Found {len(spelling_errors)} potential spelling error(s). Analyzing...' if spelling_errors else 'Processing your message...',
            'conversationCount': len(conversation['messages']) // 2,
            'sessionId': session_id
        })
        
    except requests.Timeout:
        return jsonify({'error': 'API request timed out'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """Clear conversation history for current session"""
    session_id = get_session_id()
    if session_id in conversation_history:
        conversation_history[session_id]['messages'].clear()
    return jsonify({'status': 'Conversation cleared'})

@app.route('/api/accept-suggestion', methods=['POST'])
def accept_suggestion():
    """Accept a spelling correction suggestion"""
    try:
        data = request.json
        original_text = data.get('originalText', '').strip()
        corrected_text = data.get('correctedText', '').strip()
        wrong_word = data.get('wrongWord', '').strip()
        correct_word = data.get('correctWord', '').strip()
        
        if not all([original_text, corrected_text, wrong_word, correct_word]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        session_id = get_session_id()
        conversation = get_conversation(session_id)
        
        # Update the last user message in conversation history with the correction
        if conversation['messages']:
            # Find and update the last user message
            for msg in reversed(list(conversation['messages'])):
                if msg['role'] == 'user' and msg['content'] == original_text:
                    # Update with corrected text
                    msg['content'] = corrected_text
                    break
        
        return jsonify({
            'status': 'Suggestion accepted',
            'originalText': original_text,
            'correctedText': corrected_text,
            'message': f'Corrected "{wrong_word}" to "{correct_word}"'
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'Server is running'})

if __name__ == '__main__':
    if not OPENROUTER_API_KEY:
        print('❌ Error: OPENROUTER_API_KEY not found in .env file')
        exit(1)
    
    print('✓ Spell-Check Chatbot running on http://localhost:5000')
    print('✓ Open http://localhost:5000 in your browser')
    app.run(debug=True, port=5000)
