from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from transformers import pipeline
import requests
import pyttsx3 

app = Flask(__name__)
CORS(app)  # อนุญาตให้มีการเรียกข้าม Origin

def speak(text):# ฟังก์ชันสำหรับการพูด (Text-to-Speech)
    engine = pyttsx3.init()  # สร้าง engine สำหรับเสียงพูด
    
    # ตรวจสอบเสียงที่มีอยู่ในเครื่อง
    voices = engine.getProperty('voices')
     
        

    # เลือกเสียงที่ต้องการ (เสียงที่ 0=ชาย, 1=หญิง)
    engine.setProperty('voice', voices[1].id)
    
    engine.setProperty('rate', 130)  # ความเร็วของการพูด (ค่า default คือ 200)
    engine.setProperty('volume', 1)  # ระดับเสียง (1.0  = เต็มที่)
    engine.say(text)  # พูดข้อความ
    engine.runAndWait()  # รอให้การพูดเสร็จสิ้น


# ตั้งค่า logging เพื่อบันทึกข้อความ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ตั้งค่าการวิเคราะห์ความรู้สึก
classifier = pipeline("sentiment-analysis")
token = 'yh7G6aKYB37puFgdcsd7nTz7lhAjAMDgWtZbH1TAQEc'  # ใส่ Line Token ที่คุณใช้

# ฟังก์ชันการส่งข้อความ Line Notify
def send_line_notify(message, token):
    url = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {token}'}
    data = {'message': message}
    response = requests.post(url, headers=headers, data=data)
    return "Success" if response.status_code == 200 else "Failed"

# ตรวจสอบคำหยาบ
def contains_profanity(text):
    profanity_words = ["idiot", "stupid", "dumb", "loser", "fat", "ugly", "retard", "freak", "worthless", "fatso", "jerk", "weak", "nerd", "bitch", "asshole", "bastard"]
    return any(word in text.lower() for word in profanity_words)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.json
    text = data.get('text', '')
    timestamp = data.get('timestamp', '')
    
    # บันทึกข้อความที่ได้รับแบบ real-time
    logger.info(f"เวลา: {timestamp} - ข้อความที่ได้รับ: {text}")
    
    # วิเคราะห์ความรู้สึก
    sentiment = classifier(text)[0]['label']
    logger.info(f"อารมณ์: {sentiment}")
    
    # ส่งข้อความ LINE ถ้าเป็นข้อความเชิงลบ
    if sentiment == 'NEGATIVE':
        send_line_notify("ตรวจพบประโยคเชิงลบ", token)
    
    # ตรวจสอบคำหยาบ
    if contains_profanity(text):
        send_line_notify("ตรวจพบคำหยาบ!!!", token)
    
    
    # ส่งผลลัพธ์กลับไปยังเว็บไซต์
    return jsonify({
        'status': 'success',
        'received_text': text,
        'sentiment': sentiment,
        'timestamp': timestamp
    })

if __name__ == '__main__':
    app.run(debug=True)
