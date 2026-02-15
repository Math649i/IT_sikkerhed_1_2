import json
import os
import hashlib
from cryptography.fernet import Fernet

class FlatFileDB:
    def __init__(self, filename):
        self.filename = filename
        self.key_file = 'secret.key'
        self._load_key()
        self._load()

    def _load_key(self):
        if not os.path.exists(self.key_file):
            self.key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(self.key)
        else:
            with open(self.key_file, 'rb') as f:
                self.key = f.read()
        self.cipher = Fernet(self.key)

    def _encrypt(self, data):
        if not isinstance(data, str):
            data = str(data)
        return self.cipher.encrypt(data.encode()).decode()

    def _decrypt(self, token):
        return self.cipher.decrypt(token.encode()).decode()

    def _hash_password(self, password):
        # Use a simple salt (in production, use random salt per user)
        salt = b'static_salt' 
        return hashlib.sha256(salt + password.encode()).hexdigest()

    def _load(self):
        if not os.path.exists(self.filename):
            self.users = []
            self._save()
        else:
            try:
                with open(self.filename, 'r') as f:
                    self.users = json.load(f)
            except json.JSONDecodeError:
                self.users = []

    def _save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.users, f, indent=4)

    def add_user(self, user_data):
        required_fields = ['person_id', 'first_name', 'last_name', 'address', 'street_number', 'password', 'enabled']
        for field in required_fields:
            if field not in user_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Check if user already exists
        # We can look up by ID directly in self.users as IDs are not encrypted
        for user in self.users:
            if user['person_id'] == user_data['person_id']:
                 raise ValueError(f"User with person_id {user_data['person_id']} already exists")

        # Create a copy to encrypt
        encrypted_user = user_data.copy()
        
        # Hash password
        encrypted_user['password'] = self._hash_password(user_data['password'])
        
        # Encrypt PII
        pii_fields = ['first_name', 'last_name', 'address', 'street_number', 'email', 'phone']
        for field in pii_fields:
            if field in encrypted_user:
                encrypted_user[field] = self._encrypt(encrypted_user[field])

        self.users.append(encrypted_user)
        self._save()

    def get_user(self, person_id):
        target_user = None
        for user in self.users:
            if user['person_id'] == person_id:
                target_user = user
                break
        
        if not target_user:
            return None
        
        # Decrypt fields for the return value
        decrypted_user = target_user.copy()
        pii_fields = ['first_name', 'last_name', 'address', 'street_number', 'email', 'phone']
        
        try:
            for field in pii_fields:
                if field in decrypted_user:
                    decrypted_user[field] = self._decrypt(decrypted_user[field])
        except Exception:
            # Fallback if decryption fails (e.g. bad data)
            pass
            
        return decrypted_user

    def update_user(self, person_id, updates):
        # Find the actual mutable user dict in the list
        target_user = None
        for user in self.users:
            if user['person_id'] == person_id:
                target_user = user
                break
        
        if not target_user:
             raise ValueError(f"User with person_id {person_id} not found")
        
        # Update fields
        pii_fields = ['first_name', 'last_name', 'address', 'street_number', 'email', 'phone']
        
        for key, value in updates.items():
            if key == 'password':
                target_user[key] = self._hash_password(value)
            elif key in pii_fields:
                target_user[key] = self._encrypt(value)
            else:
                target_user[key] = value
        
        self._save()
        # Return the decrypted view
        return self.get_user(person_id)

    def delete_user(self, person_id):
        target_user = None
        for user in self.users:
            if user['person_id'] == person_id:
                target_user = user
                break
                
        if not target_user:
            raise ValueError(f"User with person_id {person_id} not found")
        
        self.users.remove(target_user)
        self._save()
