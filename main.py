from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from transformers import pipeline
import requests
import pyttsx3
import time  # เพิ่มการใช้งาน time.sleep()
import tkinter as tk
from tkinter import scrolledtext, ttk
import threading

app = Flask(__name__)
CORS(app)  # อนุญาตให้มีการเรียกข้าม Origin

# ตั้งค่า logging เพื่อบันทึกข้อความ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ตั้งค่าการวิเคราะห์ความรู้สึก
classifier = pipeline("sentiment-analysis")
token = 'yh7G6aKYB37puFgdcsd7nTz7lhAjAMDgWtZbH1TAQEc'  # ใส่ Line Token ที่คุณใช้


def speak(text):  # ฟังก์ชันสำหรับการพูด (Text-to-Speech)
    engine = pyttsx3.init()  # สร้าง engine สำหรับเสียงพูด
    
    # ตรวจสอบเสียงที่มีอยู่ในเครื่อง
    voices = engine.getProperty('voices')
    
    # เลือกเสียงที่ต้องการ (เสียงที่ 0=ชาย, 1=หญิง)
    engine.setProperty('voice', voices[1].id)
    
    engine.setProperty('rate', 130)  # ความเร็วของการพูด (ค่า default คือ 200)
    engine.setProperty('volume', 1)  # ระดับเสียง (1.0  = เต็มที่)
    engine.say(text)  # พูดข้อความ
    engine.runAndWait()  # รอให้การพูดเสร็จสิ้น


# ฟังก์ชันการส่งข้อความ Line Notify
def send_line_notify(message, token):
    url = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {token}'}
    data = {'message': message}
    
    # ดีเลย์ก่อนที่จะส่งข้อความ
    time.sleep(2)  # เพิ่มดีเลย์ 2 วินาที
    
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
    logger.info(f"เวลา: {timestamp}")
    logger.info(f"ข้อความที่ได้รับ: {text}")
    
    # วิเคราะห์ความรู้สึก
    sentiment = classifier(text)[0]['label']
    logger.info(f"อารมณ์: {sentiment}")
    
    # ดีเลย์หลังจากการวิเคราะห์ความรู้สึก
      # เพิ่มดีเลย์ 1 วินาที
    
    
    if sentiment == 'NEGATIVE':
        send_line_notify("ตรวจพบประโยคเชิงลบ", token)
        time.sleep(1)
    
    if contains_profanity(text):
        send_line_notify("ตรวจพบคำหยาบ!!!", token)
        time.sleep(1)
     
        
    # แปลงข้อความทั้งหมดเป็นตัวพิมพ์เล็ก (case-insensitive)
    text = text.lower()

        # ตรวจสอบคำพูดต่างๆ และใช้ฟังก์ชัน speak() เมื่อพบคำที่ต้องการ
    if "weirdo" in text:
            speak("I’m just being myself, and that’s okay.")

    elif "freak" in text:
            speak("Being different makes the world interesting.")

    elif "socially awkward" in text:
            speak("I communicate in my own way.")

    elif "anti-social" in text:
            speak("I like socializing in ways that feel comfortable for me.")

    elif "to quiet" in text:
            speak("I talk when I feel comfortable.")

    elif "to loud" in text:
            speak("Sometimes I express myself differently, and that’s okay.")

    elif "doesn’t make eye contact" in text:
            speak("Eye contact is hard for me, but I’m still listening.")

    elif "robot" in text:
            speak("I might show emotions differently, but I still feel them.")

    elif "emotionless" in text:
            speak("I feel emotions deeply, even if I don’t show them the same way as others.")

    elif "too sensitive" in text:
            speak("I experience the world in my own way.")

    elif "can’t read the room" in text:
            speak("I try my best, and I appreciate when people help me understand.")

    elif "never stops talking" in text:
            speak("I get excited about things, and that’s a good thing.")

    elif "talks too little" in text:
            speak("I speak when I’m ready.")

    elif "dumb" in text:
            speak("I learn in my own way and at my own pace.")

    elif "slow" in text:
            speak("Everyone learns differently, and that’s okay.")

    elif "stupid" in text:
            speak("I am capable and smart in my own way.")

    elif "can’t focus" in text:
            speak("I focus best in the right environment.")

    elif "hopeless" in text:
            speak("I have potential, just like everyone else.")

    elif "lazy" in text:
            speak("I’m just being myself, and that’s okay.")

        
    
    # ส่งผลลัพธ์กลับไปยังเว็บไซต์
    return jsonify({
        'status': 'success',
        'received_text': text,
        'sentiment': sentiment,
        'timestamp': timestamp
})    

if __name__ == '__main__':
    app.run(debug=True)

# สร้าง GUI ด้วย tkinter
root = tk.Tk()
root.title("Speech Recognition Application")

# ตั้งค่าความกว้างและสูงของหน้าต่าง
root.geometry("700x700")
root.resizable(False, False)

# กำหนดสีพื้นหลังและรูปแบบ
root.config(bg="#f7f8fc")

# สไตล์สำหรับปุ่ม
style = ttk.Style()
style.configure("TButton",
                background="#6200EE",
                foreground="Purple",
                font=("Arial", 12, "bold"),
                padding=12,
                relief="flat")  # ใช้ relief แบบ flat เพราะ ttk ใช้ style แทน relief

style.map("TButton",
          background=[("active", "#3700B3")],
          relief=[("pressed", "sunken"), ("!pressed", "flat")])  # ใช้ map สำหรับการปรับปรุงลักษณะเมื่อปุ่มถูกกด

# กำหนดสไตล์ของกรอบข้อความ
style.configure("TFrame",
                background="#f7f8fc")

style.configure("TLabel",
                background="#f7f8fc",
                font=("Arial", 14),
                foreground="#333")

# สร้างกรอบสำหรับปุ่มและข้อความ
frame = ttk.Frame(root, padding="20")
frame.pack(fill=tk.BOTH, expand=True)



# เพิ่ม Label สำหรับข้อความ
label = ttk.Label(frame, text="แสดงผลเสียงที่รับมา", font=("Arial", 16, "bold"), background="#f7f8fc", foreground="#333333")
label.grid(row=1, column=0, pady=10)

# ปรับปรุง Text Box ให้ดูทันสมัย
text_output = scrolledtext.ScrolledText(frame, width=50, height=20, wrap=tk.WORD, font=("Courier", 12), background="#f0f0f0", foreground="#333333", bd=2, relief="flat")
text_output.grid(row=2, column=0, padx=10, pady=10)

# เพิ่มกรอบรอบๆ Text Box
text_output.config(insertbackground="black")  # สีของ cursor

# เริ่มโปรแกรม GUI
root.mainloop()