""" run.py """
import os
from app import create_app
from os.path import join, dirname
from dotenv import load_dotenv

# load .env in the base root
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

config_name = "development"
app = create_app(config_name)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run('', port=port)
