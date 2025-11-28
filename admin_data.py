import json
import os
import threading
import time
import random
import string
from datetime import datetime

class AdminDataManager:
    """
    Handles user, username, UTR, and custom message data management.
    Uses JSON file storage with threading locks and atomic writes (os.replace) 
    to ensure data integrity across multiple threads in any operating system.
    """
    def __init__(self):
        self.data_file = 'admin_database.json'
        # Lock for thread safety within a single Python process
        self._lock = threading.Lock() 
        self.data = {}
        self.init_database()

    def generate_hash_code(self):
        """Generate a unique 12-character alphanumeric hash code"""
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choices(characters, k=12))

    def init_database(self):
        """Initialize database with default demo data if file does not exist"""
        
        if not os.path.exists(self.data_file):
            admin_hash = "ADMIN9999RSX"

            default_data = {
                "users": [
                    {
                        "id": 1,
                        "name": "Admin User",
                        "hash_code": admin_hash,
                        "balance": 9999,
                        "created_at": datetime.now().isoformat()
                    },
                    {
                        "id": 2,
                        "name": "Special User",
                        "hash_code": "SPECIAL9999X",
                        "balance": 9999,
                        "created_at": datetime.now().isoformat()
                    }
                ],
                "demo_usernames": [
                    {
                        "id": 1,
                        "username": "riyakhanna1",
                        "mobile_number": "7091729147",
                        "mobile_details": {
                            "full_name": "👤 Sattar shah",
                            "father_name": "👨 Ramtula Shah",
                            "document_number": "🃏 275339966355",
                            "region": "🗺️ VODA BHR&JHR;BIHAR JIO;AIRTEL BHR&JHR;BIHAR VODAFONE",
                            "addresses": [
                                "🏘️ S/O Sattar Shah,-,CHHOTI KABRISTAN Bettiah,INDRA CHOWK,Bettiah Bettiah,West Champaran, Bihar,845438",
                                "🏘️ choti,CHHOTI KABRISTAN INDRA CHOWK,BETTIAH BETTIAH ward no 14,ward no 14,BETTIAH BETTIAH WEST CHAMPARAN,BETTIAH,WEST CHAMPARAN,BIHAR,845438"
                            ],
                            "phone_numbers": [
                                "📞 918207426355",
                                "📞 917903028438",
                                "📞 918864033507",
                                "📞 919065717472",
                                "📞 917091729147"
                            ]
                        },
                        "active": True,
                        "created_at": datetime.now().isoformat()
                    }
                ],
                "valid_utrs": [
                    {
                        "id": 1,
                        "utr": "453983442711",
                        "description": "Valid UTR for demo deposits",
                        "active": True,
                        "created_at": datetime.now().isoformat()
                    }
                ],
                "custom_message": "No details available in the database, but we are working on it. Your search has been logged." 
            }
            
            print(f"INFO: Initializing new database file: {self.data_file}")
            try:
                self.save_data(default_data)
                print(f"--- Admin Hash Code ---")
                print(f"Hash: {admin_hash} (Use this to login with ₹9999 balance)")
                print(f"-----------------------")
            except Exception as e:
                # Log the critical error during initial file creation/write access
                print(f"CRITICAL ERROR: Failed to create or write to the database file '{self.data_file}'. "
                      f"This is often a permission or file system issue in the deployment environment. Details: {e}")
                raise # Re-raise the exception to show the crash in deployment logs

        else:
            # Load existing data and ensure all required keys are present
            data = self.load_data()
            updated = False

            if 'users' not in data: 
                data['users'] = []
                updated = True
            if 'demo_usernames' not in data: 
                data['demo_usernames'] = []
                updated = True
            if 'valid_utrs' not in data: 
                data['valid_utrs'] = []
                updated = True
            if 'custom_message' not in data:
                data['custom_message'] = "No details available in the database, but we are working on it. Your search has been logged."
                updated = True
            
            if updated:
                self.save_data(data)

    def load_data(self):
        """Load data from JSON file using threading lock and retry mechanism"""
        max_retries = 5
        retry_delay = 0.1

        for attempt in range(max_retries):
            try:
                # Use threading lock to prevent read/write conflicts
                with self._lock:
                    with open(self.data_file, 'r') as f:
                        self.data = json.load(f)
                        # Ensure all required keys exist
                        if 'users' not in self.data: self.data['users'] = []
                        if 'demo_usernames' not in self.data: self.data['demo_usernames'] = []
                        if 'valid_utrs' not in self.data: self.data['valid_utrs'] = []
                        if 'custom_message' not in self.data: 
                            self.data['custom_message'] = "No details available in the database, but we are working on it. Your search has been logged."
                        return self.data
            except (FileNotFoundError, json.JSONDecodeError):
                if attempt == 0:
                    # If file is not found, attempt to initialize it once
                    print(f"INFO: Database file {self.data_file} not found. Attempting to initialize.")
                    self.init_database()
                    continue
                raise
            except (OSError, IOError) as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                print(f"ERROR: Failed to load data from {self.data_file} after retries: {e}")
                raise

        raise Exception("Failed to load data after maximum retries")

    def save_data(self, data=None):
        """Save data to JSON file with threading lock and atomic writes (using temp file)"""
        max_retries = 5
        retry_delay = 0.1
        temp_file = self.data_file + '.tmp'

        data_to_save = data if data is not None else self.data
        if data is not None:
             self.data = data 

        for attempt in range(max_retries):
            try:
                with self._lock:
                    # 1. Write to temporary file first
                    with open(temp_file, 'w') as f:
                        json.dump(data_to_save, f, indent=2)
                        f.flush()
                        os.fsync(f.fileno()) # Ensure data is written to disk

                    # 2. Atomic move to replace original file (cross-platform way to ensure integrity)
                    os.replace(temp_file, self.data_file)
                    return
            except (OSError, IOError) as e:
                # Clean up temp file if error occurred
                if os.path.exists(temp_file):
                    try: os.remove(temp_file)
                    except: pass

                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                print(f"ERROR: Failed to save data to {self.data_file} after retries: {e}")
                raise

        raise Exception("Failed to save data after maximum retries")

    # === User Management (The rest of the class remains the same) ===
    def create_user(self, name):
        """Create a new user with hash code and default balance (0)"""
        data = self.load_data()

        # Generate unique hash code
        while True:
            hash_code = self.generate_hash_code()
            if not any(user['hash_code'] == hash_code for user in data['users']):
                break

        new_id = max([user['id'] for user in data['users']], default=0) + 1
        new_user = {
            "id": new_id,
            "name": name,
            "hash_code": hash_code,
            "balance": 0,
            "created_at": datetime.now().isoformat()
        }

        data['users'].append(new_user)
        self.save_data(data)
        return new_user

    def get_users(self):
        """Get all users"""
        data = self.load_data()
        return data['users']

    def get_user_by_hash(self, hash_code):
        """Get user by hash code"""
        data = self.load_data()
        for user in data['users']:
            if user['hash_code'] == hash_code:
                return user
        return None

    def update_user_balance(self, hash_code, new_balance):
        """Update user balance"""
        data = self.load_data()
        for user in data['users']:
            if user['hash_code'] == hash_code:
                user['balance'] = new_balance
                break
        self.save_data(data)
        return True

    def delete_user(self, user_id):
        """Delete user"""
        data = self.load_data()
        data['users'] = [user for user in data['users'] if user['id'] != int(user_id)]
        self.save_data(data)

    # === Demo Usernames CRUD ===
    def get_usernames(self):
        data = self.load_data()
        return data['demo_usernames']

    def add_username(self, username, mobile_number, mobile_details):
        """Add a new searchable demo username"""
        data = self.load_data()
        new_id = max([item['id'] for item in data['demo_usernames']], default=0) + 1

        new_username = {
            "id": new_id,
            "username": username,
            "mobile_number": mobile_number,
            "mobile_details": mobile_details,
            "active": True,
            "created_at": datetime.now().isoformat()
        }
        data['demo_usernames'].append(new_username)
        self.save_data(data)
        return new_username

    def update_username(self, username_id, username, mobile_number, mobile_details):
        """Update an existing searchable demo username"""
        data = self.load_data()
        for item in data['demo_usernames']:
            if item['id'] == int(username_id):
                item['username'] = username
                item['mobile_number'] = mobile_number
                item['mobile_details'] = mobile_details
                break
        self.save_data(data)

    def delete_username(self, username_id):
        """Delete a searchable demo username"""
        data = self.load_data()
        data['demo_usernames'] = [item for item in data['demo_usernames'] if item['id'] != int(username_id)]
        self.save_data(data)

    # === UTR CRUD ===
    def get_utrs(self):
        """Get all valid UTRs"""
        data = self.load_data()
        return data['valid_utrs']

    def add_utr(self, utr, description):
        """Add a new valid UTR"""
        data = self.load_data()
        new_id = max([item['id'] for item in data['valid_utrs']], default=0) + 1
        new_utr = {
            "id": new_id,
            "utr": utr,
            "description": description,
            "active": True,
            "created_at": datetime.now().isoformat()
        }
        data['valid_utrs'].append(new_utr)
        self.save_data(data)
        return new_utr

    def delete_utr(self, utr_id):
        """Delete a valid UTR"""
        data = self.load_data()
        data['valid_utrs'] = [item for item in data['valid_utrs'] if item['id'] != int(utr_id)]
        self.save_data(data)

    # === Statistics and Messages ===
    def get_statistics(self):
        """Get database statistics"""
        self.load_data()
        return {
            'users': len(self.data.get('users', [])),
            'usernames': len(self.data.get('demo_usernames', [])),
            'utrs': len(self.data.get('valid_utrs', []))
        }

    def get_custom_message(self):
        """Get custom 'not found' message to display to users"""
        self.load_data()
        return self.data.get('custom_message', "No details available in the database, but we are working on it. Your search has been logged.")

    def update_custom_message(self, message):
        """Update custom 'not found' message"""
        self.load_data()
        self.data['custom_message'] = message.strip()
        self.save_data()
        return True

# Global instance
admin_db = AdminDataManager()