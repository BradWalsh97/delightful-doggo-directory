from mongoengine import *
from datetime import datetime
import json
import os

# start by defining our documents
class User(Document):
    username = StringField(unique=True, requireed=True)
    email = EmailField(unique=True)
    password = StringField(required=True)
    credit_count = IntField(default=0, min_value=0, max_value=None)
    date_created = DateTimeField(default=datetime.utcnow)

    def json(self):
        user_dict = {
            "username": self.username,
            "email": self.email,
            "credit_count": self.credit_count,
        }

        return json.dumps(user_dict)

    meta = {
        "indexes": ["username"],  # index based on username
        "ordering": ["-date_created"],  # order in decending order
    }


# users get a credit for uploading a dog, and lose credits for getting a dog
