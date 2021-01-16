import os
from delightful_doggo_directory.main import doggo
from flask import Flask
from dotenv import load_dotenv, find_dotenv
app = Flask(__name__)
app.register_blueprint(doggo)
load_dotenv(find_dotenv())

@app.route('/')
def index():
    return 'Hello world!'

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')