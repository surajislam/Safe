import json
import os
import threading
from datetime import datetime
import time

class SearchedUsernameManager:
    """
    Manages the list of usernames searched by users that were not found.
    Uses JSON file storage with threading locks and atomic writes for safety.
    """
    def __init__(self):
        self.data_file = 'searched_usernames.json'
        self._lock = threading.Lock()
        self.init_database()

    def init_database(self):
        """Initialize database with empty list if file does not exist"""
        if not os.path.exists(self.data_file):
            default_data = {"searched_logs": []}
            self._save_data(default_data)

    def _load_data(self):
        """Internal helper to load data with threading lock"""
        max_retries = 5
        retry_delay = 0.1

        for attempt in range(max_retries):
            try:
                with self._lock:
                    with open(self.data_file, 'r') as f:
                        data = json.load(f)
                        if 'searched_logs' not in data:
                            data['searched_logs'] = []
                        return data
            except (FileNotFoundError, json.JSONDecodeError):
                if attempt == 0:
                    self.init_database()
                    continue
                raise
            except (OSError, IOError) as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                raise
        raise Exception("Failed to load searched usernames after maximum retries")

    def _save_data(self, data):
        """Internal helper to save data with threading lock and atomic writes"""
        max_retries = 5
        retry_delay = 0.1
        temp_file = self.data_file + '.tmp'

        for attempt in range(max_retries):
            try:
                with self._lock:
                    # 1. Write to temporary file
                    with open(temp_file, 'w') as f:
                        json.dump(data, f, indent=2)
                        f.flush()
                        os.fsync(f.fileno())

                    # 2. Atomic move to replace original file
                    os.replace(temp_file, self.data_file)
                    return
            except (OSError, IOError) as e:
                if os.path.exists(temp_file):
                    try: os.remove(temp_file)
                    except: pass
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                raise
        raise Exception("Failed to save searched usernames after maximum retries")

    def add_searched_username(self, username, user_hash):
        """Add a non-found username to the log"""
        data = self._load_data()
        new_log = {
            "username": username.strip(),
            "user_hash": user_hash,
            "timestamp": datetime.now().isoformat()
        }
        data['searched_logs'].append(new_log)
        self._save_data(data)

    def get_all_searched_usernames(self):
        """Retrieve all logged searched usernames"""
        data = self._load_data()
        return data['searched_logs']

# Global instance
searched_username_manager = SearchedUsernameManager()