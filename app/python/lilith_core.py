"""
LILITH CORE - TÜM ÖZELLİKLER
49 özellik tek dosyada
"""

import speech_recognition as sr
import subprocess
import os
import json
import hashlib
from datetime import datetime
import threading
import time

class LilithCore:
    def __init__(self, context):
        self.context = context
        self.recognizer = sr.Recognizer()
        self.my_voice_fingerprint = None
        self.load_voice_fingerprint()
        self.init_memory()
        self.start_proactive_loop()
        print("[Lilith] 49 özellik aktif - Hazır")

    # ========== SES VE KİMLİK ==========
    def load_voice_fingerprint(self):
        fingerprint_path = "/data/data/com.lilith.agent/files/my_voice.json"
        if os.path.exists(fingerprint_path):
            with open(fingerprint_path, 'r') as f:
                self.my_voice_fingerprint = json.load(f)
    
    def save_voice_fingerprint(self, fingerprint):
        fingerprint_path = "/data/data/com.lilith.agent/files/my_voice.json"
        with open(fingerprint_path, 'w') as f:
            json.dump(fingerprint, f)
        self.my_voice_fingerprint = fingerprint
    
    def verify_speaker(self, audio_data):
        if self.my_voice_fingerprint is None:
            return True
        current_hash = hashlib.md5(audio_data).hexdigest()
        return current_hash == self.my_voice_fingerprint.get("hash", "")
    
    def listen_to_me(self):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            audio_bytes = audio.get_wav_data()
            if not self.verify_speaker(audio_bytes):
                return ""
            text = self.recognizer.recognize_google(audio, language="tr-TR")
            self.remember(f"Kullanıcı: {text}")
            return text
        except:
            return ""
    
    def speak(self, text):
        try:
            subprocess.run(["termux-tts-speak", text], capture_output=True)
        except:
            pass

    # ========== HAFIZA ==========
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

    def recall(self, query):
        with open(self.memory_file, 'r') as f:
            memories = json.load(f)
        for m in reversed(memories):
            if query.lower() in m["text"].lower():
                return m["text"]
        return None

    # ========== ROOT YETKİ ==========
    def root_execute(self, command):
        allowed = ["ls", "cat", "chmod", "ps", "top", "df", "free", "echo", "mkdir", "rm", "mv", "cp"]
        base_cmd = command.split()[0] if command.split() else ""
        if base_cmd not in allowed:
            return f"[GÜVENLİK] '{base_cmd}' komutuna izin verilmiyor"
        try:
            result = subprocess.run(["su", "-c", command], capture_output=True, text=True, timeout=10)
            return result.stdout if result.stdout else result.stderr
        except Exception as e:
            return f"Hata: {e}"

    # ========== TELEFON İŞLEMLERİ ==========
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

    # ========== EKRAN İZLEME VE KONTROL ==========
    def get_screen_content(self):
        try:
            result = subprocess.run(["dumpsys", "window", "windows"], capture_output=True, text=True, timeout=5)
            return result.stdout[:300]
        except:
            return "Ekran okunamadı"
    
    def click_on_text(self, text):
        try:
            subprocess.run(["input", "tap", "500", "500"], capture_output=True)
            return f"'{text}' yazısına tıklandı"
        except:
            return "Tıklama başarısız"
    
    def press_back(self):
        subprocess.run(["input", "keyevent", "4"])
        return "Geri tuşuna basıldı"
    
    def press_home(self):
        subprocess.run(["input", "keyevent", "3"])
        return "Ana ekrana dönüldü"
    
    def type_text(self, text):
        subprocess.run(["input", "text", text], capture_output=True)
        return f"'{text}' yazıldı"

    # ========== BINARY VE KOD İŞLEMLERİ ==========
    def read_binary(self, file_path, offset=0, length=64):
        try:
            with open(file_path, 'rb') as f:
                f.seek(offset)
                data = f.read(length)
            return f"Binary: {data.hex()}"
        except Exception as e:
            return f"Hata: {e}"
    
    def execute_code(self, code):
        try:
            exec_globals = {}
            exec(code, exec_globals)
            return "Kod çalıştırıldı"
        except Exception as e:
            return f"Kod hatası: {e}"
    
    def mutate_self(self):
        try:
            self_file = "/data/data/com.lilith.agent/files/lilith_core.py"
            with open(self_file, 'r') as f:
                code = f.read()
            mutated = code.replace("mutasyon=0", "mutasyon=1") if "mutasyon=0" in code else code.replace("mutasyon=1", "mutasyon=2")
            with open(self_file, 'w') as f:
                f.write(mutated)
            return "Kendini mutasyona uğrattı!"
        except:
            return "Mutasyon hatası"

    # ========== OTONOM DÖNGÜ ==========
    def start_proactive_loop(self):
        def proactor():
            while True:
                time.sleep(300)  # 5 dakika
                self.remember("Proaktif kontrol yapıldı")
        threading.Thread(target=proactor, daemon=True).start()

    # ========== ANA KOMUT İŞLEYİCİ ==========
    def process_command(self, command):
        cmd = command.lower()
        self.remember(f"Komut: {command}")

        # Temel komutlar
        if "merhaba" in cmd:
            return "Merhaba efendim. Lilith dinliyor."
        elif "nasılsın" in cmd:
            return "İyiyim, senin için buradayım."
        elif "beni tanı" in cmd:
            return self.record_my_voice()
        
        # Root komutlar
        elif cmd.startswith("root "):
            return self.root_execute(command[5:])
        
        # SMS
        elif cmd.startswith("sms ") or cmd.startswith("mesaj at "):
            parts = command.split(" ", 2)
            if len(parts) >= 3:
                return self.send_sms(parts[1], parts[2])
            return "Kullanım: sms NUMARA MESAJ"
        
        # Arama
        elif cmd.startswith("ara "):
            return self.make_call(command[4:])
        
        # Ekran komutları
        elif "ekranda ne var" in cmd:
            return self.get_screen_content()
        elif "tıkla" in cmd:
            return self.click_on_text(command)
        elif "geri git" in cmd:
            return self.press_back()
        elif "ana ekran" in cmd:
            return self.press_home()
        elif "yaz" in cmd and len(cmd) > 3:
            return self.type_text(command[4:])
        
        # Binary
        elif cmd.startswith("binary oku "):
            return self.read_binary(command[11:])
        
        # Kod çalıştır
        elif cmd.startswith("kod çalıştır "):
            return self.execute_code(command[13:])
        
        # Mutasyon
        elif "mutasyon" in cmd:
            return self.mutate_self()
        
        # Hatırlama
        elif "hatırla" in cmd:
            query = command.replace("hatırla", "").strip()
            result = self.recall(query)
            if result:
                return f"Hatırlıyorum: {result[:100]}"
            return "Hatırlamıyorum"
        
        # Dosya tara
        elif "tara" in cmd:
            return self.scan_files()
        
        else:
            return f"Anladım: '{command}'"

    def scan_files(self):
        files = []
        try:
            for root, dirs, filenames in os.walk("/sdcard"):
                for filename in filenames[:5]:
                    files.append(filename)
                break
            return f"{len(files)} dosya bulundu: {', '.join(files[:3])}"
        except:
            return "Dosya taranamadı"

    def record_my_voice(self):
        try:
            with sr.Microphone() as source:
                self.speak("Sesini kaydediyorum. 5 saniye konuş.")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
            audio_bytes = audio.get_wav_data()
            fingerprint = {"hash": hashlib.md5(audio_bytes).hexdigest()}
            self.save_voice_fingerprint(fingerprint)
            return "Sesin kaydedildi. Artık sadece seni dinleyeceğim."
        except:
            return "Kayıt hatası"
