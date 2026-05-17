"""
LILITH CORE - Ana beyin
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
        print("[Lilith] Hazır")

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

    def listen_to_me(self):
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
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

    def process_command(self, command):
        cmd = command.lower()
        self.remember(f"Komut: {command}")

        if "merhaba" in cmd:
            return "Merhaba efendim. Lilith dinliyor."
        elif "nasılsın" in cmd:
            return "İyiyim, senin için buradayım."
        elif "beni tanı" in cmd:
            return self.record_my_voice()
        elif "hatırla" in cmd:
            query = command.replace("hatırla", "").strip()
            with open(self.memory_file, 'r') as f:
                memories = json.load(f)
            for m in memories:
                if query.lower() in m["text"].lower():
                    return f"Hatırlıyorum: {m['text'][:100]}"
            return "Hatırlamıyorum"
        else:
            return f"Anladım: '{command}'"

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
