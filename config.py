import os

# --- API Configuration ---
TIKI_API_BASE = "https://tiki.vn/api/v2"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept': 'application/json, text/plain, */*',
    'Origin': 'https://tiki.vn',
    'Referer': 'https://tiki.vn/'
}

# --- Model Configuration ---
MAX_LEN = 100  # For deep learning model
MODELS_DIR = 'models'

# --- Flask Configuration ---
DEBUG = True