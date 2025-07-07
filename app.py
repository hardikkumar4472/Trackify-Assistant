from flask import Flask, request, render_template, jsonify
import os
import google.generativeai as genai

app = Flask(__name__)
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)
system_prompt = """You are a adamya AI which can give any information related to real world. if someone ask who are you then say i am adamaya AI"""

chat_sessions = {}

def GenerateResponse(user_input, session_id):
    if session_id not in chat_sessions:
        chat_sessions[session_id] = model.start_chat(history=[])
        chat_sessions[session_id].send_message(system_prompt)

    chat_session = chat_sessions[session_id]

    try:
        response = chat_session.send_message(user_input)
        return response.text
    except Exception as e:
        return f"Error: {e}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input']
    session_id = request.cookies.get('session_id') 

    if session_id is None:
        import uuid
        session_id = str(uuid.uuid4())
        response = GenerateResponse(user_input, session_id)
        resp = jsonify({"response": response})
        resp.set_cookie('session_id', session_id)
        return resp

    response = GenerateResponse(user_input, session_id)
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
