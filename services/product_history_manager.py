# services/product_history_manager.py
# -*- coding: utf-8 -*-
"""
Created on 2023-10-01 12:00:00
author: nguyendevwk
"""

import json
import os
import time

HISTORY_FILE = 'database/search_history.json'

class ProductHistoryManager:
    def __init__(self, history_file=HISTORY_FILE):
        self.history_file = history_file
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump({}, f)

    def load_history(self):
        with open(self.history_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_history(self, history):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def log_keyword(self, user_id, keyword):
        if not keyword.strip():
            return
        history = self.load_history()
        if user_id not in history:
            history[user_id] = []

        history[user_id].append({
            "keyword": keyword.strip(),
            "timestamp": time.time()
        })

        self.save_history(history)

    def get_user_history(self, user_id):
        history = self.load_history()
        return history.get(user_id, [])

    def clear_user_history(self, user_id):
        history = self.load_history()
        if user_id in history:
            del history[user_id]
            self.save_history(history)
            return True
        return False
