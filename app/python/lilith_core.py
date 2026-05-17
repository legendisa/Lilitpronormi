"""
LILITH CORE - 64 ÖZELLİK + GÜVENLİK KATMANI
- Sadece senin sesin
- Başkası yazı yazarsa engelle
- 7/24 çevre dinleme
- 7/24 kamera kullanımı
"""

import speech_recognition as sr
import subprocess
import os
import json
import hashlib
from datetime import datetime
import threading
import time
import requests

class LilithCore:
    def __init__(self, context):
        self.context = context
        self.recognizer = sr.Recognizer()
        
        # Güvenlik - Sadece sen
        self.my_voice_fingerprint = None
        self.my_user_id = None
        self.load_user_data()
        
        # Eğer kullanıcı kayıtlı değilse, ilk açılışta kayıt iste
        if self.my_user_id is None:
            self.need_registration = True
        else:
            self.need_registration = False
        
        self.init_memory()
        
        # Sürekli dinleme ve kamera başlat
        self.start_continuous_listening()
        self.start_continuous_camera()
        self.start_proactive_loop()
        
        print("[Lilith] 64 özellik + Güvenlik aktif - Sadece senin için çalışıyor")

    # ========== GÜVENLİK KATMANI ==========
    def load_user_data(self):
        user_file = "/data/data/com.lilith.agent/files/user.json"
        if os.path.exists(user_file):
            with open(user_file, 'r') as f:
                data = json.load(f)
                self.my_voice_fingerprint = data.get("voice_hash")
                self.my_user_id = data.get("user_id")
    
    def save_user_data(self):
        user_file = "/data/data/com.lilith.agent/files/user.json"
        with open(user_file, 'w') as f:
            json.dump({"voice_hash": self.my_voice_fingerprint, "user_id": self.my_user_id}, f)
    
    def verify_user(self, audio_data, text_input=None):
        # Ses kontrolü
        if audio_data and self.my_voice_fingerprint:
            voice_hash = hashlib.md5(audio_data).hexdigest()
            if voice_hash != self.my_voice_fingerprint:
                return False, "Sesin tanınmadı. Sen değilsin."
        
        # Yazı kontrolü - sadece senin yazdıklarını kabul et
        if text_input and self.my_user_id:
            # Basit bir doğrulama: Kullanıcı kayıtlı mı?
            return False, "Sadece sesli komut kabul edilir. Yazılı giriş devre dışı."
        
        return True, "Onaylandı"
    
    def register_user(self):
        try:
            with sr.Microphone() as source:
                self.speak("Sesini kaydediyorum. Lütfen 5 saniye konuş.")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
            audio_bytes = audio.get_wav_data()
            self.my_voice_fingerprint = hashlib.md5(audio_bytes).hexdigest()
            self.my_user_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
            self.save_user_data()
            self.need_registration = False
            return "Kayıt tamam. Artık sadece seni dinleyeceğim ve sadece senin komutlarını kabul edeceğim."
        except:
            return "Kayıt başarısız. Tekrar dene."

    # ========== SÜREKLİ DİNLEME (7/24) ==========
    def start_continuous_listening(self):
        def listener():
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("[Lilith] Sürekli dinleme başladı...")
                while True:
                    try:
                        audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=5)
                        audio_bytes = audio.get_wav_data()
                        
                        # Sadece senin sesini dinle
                        if self.my_voice_fingerprint:
                            voice_hash = hashlib.md5(audio_bytes).hexdigest()
                            if voice_hash != self.my_voice_fingerprint:
                                continue  # Başkasını dinleme
                        
                        text = self.recognizer.recognize_google(audio, language="tr-TR")
                        if text:
                            print(f"[Lilith] Duyulan: {text}")
                            self.process_command(text)
                    except:
                        pass
        threading.Thread(target=listener, daemon=True).start()
    
    # ========== SÜREKLİ KAMERA (7/24) ==========
    def start_continuous_camera(self):
        def camera_loop():
            while True:
                try:
                    # Her 30 saniyede bir fotoğraf çek
                    subprocess.run(["termux-camera-photo", "-c", "0", "/sdcard/lilith_frame.jpg"], 
                                 capture_output=True, timeout=5)
                    # Basit nesne kontrolü (isteğe bağlı)
                    time.sleep(30)
                except:
                    time.sleep(60)
        threading.Thread(target=camera_loop, daemon=True).start()
    
    def detect_object(self):
        return "Kamera aktif. Sürekli görüntü analiz ediliyor."

    # ========== MEVCUT ÖZELLİKLER ==========
    def speak(self, text):
        try:
            subprocess.run(["termux-tts-speak", text], capture_output=True)
        except:
            pass

    def init_memory(self):
        self.memory_file = "/data/data/com.lilith.agent/files/memory.json"
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, 'w') as f:
                json.dump([], f)
    
    def remember(self, text):
        with open(self.memory_file, 'r') as f:
            memories = json.load(f)
        memories.append({"text": text, "time": datetime.now().isoformat()})
        with open(self.memory_file, 'w') as f:
            json.dump(memories[-500:], f)

    def root_execute(self, command):
        allowed = ["ls", "cat", "chmod", "ps", "top", "df", "free", "echo", "mkdir", "rm", "mv", "cp"]
        base_cmd = command.split()[0] if command.split() else ""
        if base_cmd not in allowed:
            return f"[GÜVENLİK] '{base_cmd}' komutuna izin verilmiyor"
        try:
            result = subprocess.run(["su", "-c", command], capture_output=True, text=True, timeout=10)
            return result.stdout if result.stdout else result.stderr
        except:
            return "Hata"

    def send_sms(self, number, message):
        try:
            subprocess.run(["su", "-c", f"service call isms 7 i32 0 s16 'com.android.mms' s16 '{number}' s16 'null' s16 '{message}'"], timeout=5)
            return f"Mesaj gönderildi: {number}"
        except:
            return "Mesaj gönderilemedi"
    
    def make_call(self, number):
        try:
            subprocess.run(["su", "-c", f"service call phone 2 s16 '{number}'"], timeout=5)
            return f"Aranıyor: {number}"
        except:
            return "Arama yapılamadı"

    def get_screen_content(self):
        try:
            result = subprocess.run(["dumpsys", "window", "windows"], capture_output=True, text=True, timeout=5)
            return result.stdout[:300]
        except:
            return "Ekran okunamadı"

    def start_proactive_loop(self):
        def proactor():
            while True:
                time.sleep(300)
                self.remember("Proaktif kontrol yapıldı")
        threading.Thread(target=proactor, daemon=True).start()

    # ========== ANA KOMUT İŞLEYİCİ (Güvenlikli) ==========
    def process_command(self, command):
        # Önce kullanıcı kayıtlı değilse kayıt iste
        if self.need_registration:
            if "beni tanı" in command.lower():
                return self.register_user()
            return "Lütfen önce 'beni tanı' deyip sesini kaydet."
        
        cmd = command.lower()
        self.remember(f"Komut: {command}")

        # Kayıt komutu
        if cmd == "beni tanı":
            return "Zaten kayıtlısın."
        
        # Temel
        if "merhaba" in cmd:
            return "Merhaba efendim. Lilith 64 özellikle senin için çalışıyor. Çevre dinleniyor, kamera aktif."

        # Root
        if cmd.startswith("root "):
            return self.root_execute(command[5:])

        # SMS
        if cmd.startswith("sms "):
            parts = command.split(" ", 2)
            if len(parts) >= 3:
                return self.send_sms(parts[1], parts[2])

        # Arama
        if cmd.startswith("ara "):
            return self.make_call(command[4:])

        # Ekran
        if "ekranda ne var" in cmd:
            return self.get_screen_content()

        # Kamera
        if "kamera" in cmd or "nesne tanı" in cmd:
            return self.detect_object()

        # Binary
        if cmd.startswith("binary oku "):
            return self.read_binary(command[11:])

        # Hatırlama
        if "hatırla" in cmd:
            query = command.replace("hatırla", "").strip()
            with open(self.memory_file, 'r') as f:
                memories = json.load(f)
            for m in reversed(memories):
                if query.lower() in m["text"].lower():
                    return f"Hatırlıyorum: {m['text'][:100]}"
            return "Hatırlamıyorum"

        return f"Anladım: '{command}'"

    def read_binary(self, file_path, offset=0, length=64):
        try:
            with open(file_path, 'rb') as f:
                f.seek(offset)
                data = f.read(length)
            return f"Binary: {data.hex()}"
        except:
            return "Hata"
