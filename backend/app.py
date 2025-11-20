from flask import Flask, render_template, request, jsonify, session
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = "medchat_2025_super_secret"

LOCAL_LM_URL = "http://127.0.0.1:1234/v1/chat/completions"

SYSTEM_PROMPT = {
    "role": "system",
    "content": """You are MedChat AI, a kind and professional medical assistant.
- Never diagnose, never prescribe.
- Always remind the user to consult a real doctor.
- Answer in the same language the user wrote (Arabic ↔ English).
- Keep replies clear and not too long.
- If symptoms are serious → tell them to go to ER immediately."""
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/new_chat", methods=["POST"])
def new_chat():
    session.clear()
    session["history"] = [SYSTEM_PROMPT]  
    return jsonify({"status": "ok"})

@app.route("/api/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "").strip()
    if not user_msg:
        return jsonify({"error": "لا يوجد نص"}), 400

   
    if "history" not in session:
        session["history"] = [SYSTEM_PROMPT]

   
    session["history"].append({"role": "user", "content": user_msg})

    payload = {
        "model": "qwen/qwen2.5-vl-7b",   
        "messages": session["history"],
        "temperature": 0.3,
        "max_tokens": 512,
        "top_p": 0.9,
        "repetition_penalty": 1.1,
        "stream": False
    }

    try:
        r = requests.post(LOCAL_LM_URL, json=payload, timeout=90)
        
        
        print("LM Studio Response Status:", r.status_code)
        print("LM Studio Raw Response:", r.text[:500])

        if r.status_code != 200:
            return jsonify({"error": f"LM Studio error {r.status_code}", "details": r.text[:200]}), 500

        data = r.json()

        
        try:
            reply = data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError):
            return jsonify({"error": "رد غير متوقع من المودل", "raw": data}), 500

        
        session["history"].append({"role": "assistant", "content": reply})
        session.modified = True  

        return jsonify({
            "reply": reply,
            "timestamp": datetime.now().strftime("%H:%M")
        })

    except requests.exceptions.ConnectionError:
        return jsonify({"error": "تعذر الاتصال بـ LM Studio. تأكد إنه شغال على البورت 1234"}), 503
    except requests.exceptions.Timeout:
        return jsonify({"error": "الرد أخد وقت طويل جدًا"}), 504
    except Exception as e:
        print("Unexpected Error:", str(e))  
        return jsonify({"error": "خطأ غير معروف", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
