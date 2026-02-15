import json
import os

class FlatFileDB:
    def __init__(self, filename):
        self.filename = filename
        self._load()

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
        if self.get_user(user_data['person_id']):
             raise ValueError(f"User with person_id {user_data['person_id']} already exists")

        self.users.append(user_data)
        self._save()

    def get_user(self, person_id):
        for user in self.users:
            if user['person_id'] == person_id:
                return user
        return None

    def update_user(self, person_id, updates):
        user = self.get_user(person_id)
        if not user:
             raise ValueError(f"User with person_id {person_id} not found")
        
        # Update fields
        for key, value in updates.items():
            user[key] = value
        
        self._save()
        return user

    def delete_user(self, person_id):
        user = self.get_user(person_id)
        if not user:
            raise ValueError(f"User with person_id {person_id} not found")
        
        self.users.remove(user)
        self._save()
