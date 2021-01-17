import mongoengine as mongo
from datetime import datetime
import json
import os

# start by defining our documents
class User(Document):
    """This schema describes the user object to be stored in the MongoDB database"""

    username = StringField(unique=True, requireed=True)
    email = EmailField(unique=True)
    password = StringField(required=True)
    credit_count = IntField(
        default=0, max_value=None
    )  # unable to set min_value due to current bug in mongoengine
    date_created = DateTimeField(default=datetime.utcnow)

    def json(self):
        """This method will return a json representation of the user it is called on. """

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
