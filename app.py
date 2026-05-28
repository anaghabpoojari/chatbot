from flask import Flask, render_template, request, jsonify, session
from chatbot import Chatbot
import uuid

app = Flask(__name__)
app.secret_key = "change-this-secret"

# One Chatbot instance per session (stored in a dict keyed by session id)
sessions: dict[str, Chatbot] = {}

def get_bot() -> Chatbot:
    sid = session.setdefault("id", str(uuid.uuid4()))
    if sid not in sessions:
        sessions[sid] = Chatbot()
    return sessions[sid]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "").strip()
    if not user_input:
        return jsonify({"error": "empty message"}), 400

    bot = get_bot()
    result = bot.respond(user_input)
    result["history"] = bot.memory.get_history()
    return jsonify(result)

@app.route("/reset", methods=["POST"])
def reset():
    get_bot().memory.clear()
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    app.run(debug=True)