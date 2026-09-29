import os
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from google import genai
from chatbot_config import BOT_NAME, SYSTEM_PROMPT

load_dotenv(override=True)
app = Flask(__name__)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is missing from the .env file.")

client = genai.Client(api_key=api_key)
MODEL_NAME = "gemini-3.1-flash-lite"

@app.route("/")
def home():
    return render_template("index.html", bot_name=BOT_NAME)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = str(data.get("message", "")).strip()
    if not user_message:
        return jsonify({"error": "Please enter a question."}), 400
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=f"{SYSTEM_PROMPT}\n\nStudent question:\n{user_message}",
            config={"thinking_config": {"thinking_level": "minimal"}},
        )
        answer = (response.text or "").strip()
        return jsonify({"reply": answer or "I could not generate a response. Please try again."})
    except Exception:
        return jsonify({"error": "Unable to contact Gemini right now. Please try again."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
