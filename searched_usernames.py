import json
import os
import fcntl
import threading
from datetime import datetime

class SearchedUsernameManager:
    def __init__(self):
        self.data_file = 'searched_usernames.json'
        self._lock = threading.Lock()
        self.init_database()

    def init_database(self):
        """Initialize database for searched usernames"""
        if not os.path.exists(self.data_file):
            default_data = {
                "searched_usernames": []
            }
            self.save_data(default_data)

    def load_data(self):
        """Load data from JSON file with file locking"""
        try:
            with self._lock:
                with open(self.data_file, 'r') as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                    try:
                        data = json.load(f)
                        if 'searched_usernames' not in data:
                            data['searched_usernames'] = []
                        return data
                    finally:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except (FileNotFoundError, json.JSONDecodeError):
            self.init_database()
            return {"searched_usernames": []}

    def save_data(self, data):
        """Save data to JSON file"""
        with self._lock:
            with open(self.data_file, 'w') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    json.dump(data, f, indent=2)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def add_searched_username(self, username, user_hash):
        """Add username jo search hua but result nahi mila"""
        data = self.load_data()

        # Check if username already exists
        for item in data['searched_usernames']:
            if item['username'].lower() == username.lower():
                return  # Already exists, don't add duplicate

        new_entry = {
            "id": len(data['searched_usernames']) + 1,
            "username": username,
            "searched_by": user_hash,
            "searched_at": datetime.now().isoformat(),
            "status": "not_found"
        }

        data['searched_usernames'].append(new_entry)
        self.save_data(data)

    def get_searched_usernames(self):
        """Get all searched usernames"""
        data = self.load_data()
        # Add mobile_number field for display consistency
        for username in data['searched_usernames']:
            if 'mobile_number' not in username:
                username['mobile_number'] = 'Not Available'
        return data['searched_usernames']

    def delete_searched_username(self, username_id):
        """Delete searched username by ID"""
        data = self.load_data()
        data['searched_usernames'] = [item for item in data['searched_usernames'] if item['id'] != username_id]
        self.save_data(data)

# Global instance
searched_username_manager = SearchedUsernameManager()