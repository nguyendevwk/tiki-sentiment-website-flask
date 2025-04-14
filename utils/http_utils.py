import time
import requests

def get_with_retry(session, url, params=None, max_retries=3, delay=1):
    """Make a GET request with retry logic"""
    for attempt in range(max_retries):
        try:
            response = session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if attempt == max_retries - 1:
                # Last attempt failed, re-raise the exception
                raise
            print(f"Attempt {attempt+1} failed: {str(e)}. Retrying in {delay} seconds...")
            time.sleep(delay)