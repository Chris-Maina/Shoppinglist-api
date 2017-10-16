""" run.py """
import os
from app import create_app
from os.path import join, dirname
from dotenv import load_dotenv
from flask_cors import CORS

# load .env in the base root
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

config_name = os.getenv('APP_SETTINGS')
app = create_app(config_name)
CORS(app)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run('', port=port)
