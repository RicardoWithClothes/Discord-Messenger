import json
import os
from Task import SavedContact

FILE_NAME = "contacts.json"

class Storage:
    @staticmethod
    def load_contacts():
        if not os.path.exists(FILE_NAME):
            return []
        
        try:
            with open(FILE_NAME, 'r') as f:
                data = json.load(f)
                # Convert raw JSON back into Resipient objects
                return [SavedContact(**item) for item in data]
        except:
            return []

    @staticmethod
    def save_contacts(contacts_list):
        data = [vars(u) for u in contacts_list]
        with open(FILE_NAME, 'w') as f:
            json.dump(data, f, indent=4)