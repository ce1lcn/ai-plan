# AI Plan App - Backend Server
# 放在你的 Windows 电脑上跑，iPhone PWA 通过内网穿透访问

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__, static_folder='static')
CORS(app)

DEEPSEEK_KEY = os.environ.get("DEEPSEEK_KEY", "sk-f933d288dc354231a5092240fb82d0db")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", [])
    agent_config = data.get("agent_config", {})
    
    # 构造 system prompt
    system = {
        "role": "system",
        "content": f"""你是用户的AI生活规划助手。你的性格：{agent_config.get('personality','友好专业')}。
用户需要你帮助的领域：{agent_config.get('domains','综合规划')}。
当用户提出需求时，你需要：
1. 拆解需求为具体任务
2. 提出日程方案（含时间安排）
3. 如果用户同意，输出结构化的日程JSON，包含：任务名称、开始时间、持续时间、备注
回复风格：简洁有温度，像朋友一样但保持专业。"""
    }
    
    full_messages = [system] + messages
    
    resp = requests.post(DEEPSEEK_URL, json={
        "model": "deepseek-chat",
        "messages": full_messages,
        "temperature": 0.7
    }, headers={"Authorization": f"Bearer {DEEPSEEK_KEY}"})
    
    return jsonify(resp.json())

@app.route("/api/generate_calendar", methods=["POST"])
def generate_calendar():
    """生成 .ics 日历文件"""
    events = request.json.get("events", [])
    ics = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//AI Plan//CN"]
    for i, ev in enumerate(events):
        ics += [
            "BEGIN:VEVENT",
            f"DTSTART:{ev.get('start','')}",
            f"DTEND:{ev.get('end','')}",
            f"SUMMARY:{ev.get('title','任务')}",
            f"DESCRIPTION:{ev.get('note','')}",
            f"UID:aiplan{i}@planapp",
            "END:VEVENT"
        ]
    ics.append("END:VCALENDAR")
    return "\n".join(ics), 200, {"Content-Type":"text/calendar"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5200, debug=True)
