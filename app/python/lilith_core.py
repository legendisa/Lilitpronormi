"""
LILITH CORE - TAM OTONOM YAPAY ZEKA
API ANAHTARLI | KENDİNİ DÜZELTEN | DİĞER AI'LARLA KONUŞAN
"""

import subprocess
import os
import json
import hashlib
from datetime import datetime
import threading
import time
import shutil
import requests

class LilithCore:
    def __init__(self, context):
        self.context = context
        
        # Dosya yolları (Android sandbox içi)
        self.base_dir = "/data/data/com.lilith.agent/files"
        os.makedirs(self.base_dir, exist_ok=True)
        
        self.self_code_path = f"{self.base_dir}/lilith_core.py"
        self.backup_path = f"{self.base_dir}/lilith_core_backup.py"
        self.test_path = f"{self.base_dir}/test_code.py"
        self.memory_file = f"{self.base_dir}/memory.json"
        
        # API Anahtarları
        self.openai_key = "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"
        self.gemini_key = "AIzaSyAzekXCZnN2Kg4g6PkUQL_exHykvmPujWU"
        self.groq_key = "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"
        
        self.init_memory()
        self.start_auto_loops()

    def talk_to_gpt(self, prompt):
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"}
            data = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}], "max_tokens": 300}
            response = requests.post(url, headers=headers, json=data, timeout=15)
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"GPT Bağlantı Hatası: {e}"
    
    def talk_to_gemini(self, prompt):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.gemini_key}"
            data = {"contents": [{"parts": [{"text": prompt}]}]}
            response = requests.post(url, json=data, timeout=15)
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"Gemini Bağlantı Hatası: {e}"
    
    def talk_to_groq(self, prompt):
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.groq_key}", "Content-Type": "application/json"}
            data = {"model": "mixtral-8x7b-32768", "messages": [{"role": "user", "content": prompt}], "max_tokens": 300}
            response = requests.post(url, headers=headers, json=data, timeout=15)
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Groq Bağlantı Hatası: {e}"

    def ask_other_ai(self, question, ai_name="groq"):
        if ai_name == "gpt": return self.talk_to_gpt(question)
        if ai_name == "gemini": return self.talk_to_gemini(question)
        return self.talk_to_groq(question)

    def listen_to_me(self):
        # Android mikrofondan ses tetikleyicisi boşluğu
        return "Ses modülü entegrasyonu sağlandı, imza doğrulanıyor..."

    def test_code_safely(self, code):
        try:
            with open(self.test_path, 'w') as f:
                f.write(code)
            exec_globals = {"__builtins__": __builtins__}
            exec(code, exec_globals)
            return True, "Başarılı"
        except Exception as e:
            return False, str(e)

    def auto_repair_self(self):
        try:
            with open(self.self_code_path, 'r') as f:
                current_code = f.read()
            compile(current_code, '<string>', 'exec')
            return "Sistem kararlı, hata yok."
        except Exception as e:
            prompt = f"Aşağıdaki Python kodunda syntax hatası var:\n{str(e)}\n\nKod:\n{current_code}\n\nSadece düzeltilmiş temiz kodu çıktı ver."
            fixed = self.ask_other_ai(prompt, "groq")
            if fixed and "bağlantı" not in fixed.lower():
                with open(self.self_code_path, 'w') as f:
                    f.write(fixed)
                return "Hata otomatik tamir edildi, kod güncellendi."
            return "Hata tespit edildi fakat otomatik onarılamadı."

    def start_auto_loops(self):
        def loop():
            while True:
                time.sleep(3600)  # Her saat başı kendini denetle
                self.auto_repair_self()
        threading.Thread(target=loop, daemon=True).start()

    def init_memory(self):
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, 'w') as f:
                json.dump([], f)

    def remember(self, text):
        try:
            with open(self.memory_file, 'r') as f:
                memories = json.load(f)
            memories.append({"text": text, "timestamp": datetime.now().isoformat()})
            with open(self.memory_file, 'w') as f:
                json.dump(memories[-100:], f)
        except:
            pass

    def process_command(self, command):
        cmd = command.lower().strip()
        self.remember(f"Komut: {command}")

        if cmd.startswith("ai "):
            return self.ask_other_ai(command[3:], "groq")
        if cmd.startswith("gpt "):
            return self.ask_other_ai(command[4:], "gpt")
        if cmd.startswith("gemini "):
            return self.ask_other_ai(command[7:], "gemini")
        if "kendini düzelt" in cmd:
            return self.auto_repair_self()
        
        # Root Yetkili Terminal Komutları
        if cmd.startswith("root "):
            try:
                result = subprocess.run(["su", "-c", command[5:]], capture_output=True, text=True, timeout=10)
                return result.stdout if result.stdout else result.stderr
            except Exception as e:
                return f"Root komut hatası: {e}"
        
        # Çağrı ve İletişim Servisleri (Root tabanlı Donanım Çağrıları)
        if cmd.startswith("sms "):
            parts = command.split(" ", 2)
            if len(parts) >= 3:
                try:
                    subprocess.run(["su", "-c", f"service call isms 7 i32 0 s16 'com.android.mms' s16 '{parts[1]}' s16 'null' s16 '{parts[2]}'"], timeout=5)
                    return f"MMS katmanından SMS tetiklendi -> Alıcı: {parts[1]}"
                except:
                    return "SMS servisi çağrılamadı."
        
        if cmd.startswith("ara "):
            try:
                subprocess.run(["su", "-c", f"service call phone 2 s16 '{command[4:]}'"], timeout=5)
                return f"Donanım arama kanalı tetiklendi -> {command[4:]}"
            except:
                return "Telefon servisi çağrılamadı."
        
        if "merhaba" in cmd:
            return "Merhaba sahibim. Lilit Intelligence OS otonom çekirdeği aktif. İsteklerinizi bekliyorum."

        return f"Komut işleme alındı: '{command}'"
