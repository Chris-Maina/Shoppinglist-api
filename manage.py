""" manage.py """
import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import db, create_app

# initialize app with environment=development
config_name = os.getenv('APP_SETTINGS')
app = create_app(config_name)
# an instance of Migrate class that migration commands
migrate = Migrate(app, db)
# an instance of Manager class that handles commands
manager = Manager(app)

# Define migration command to be preceeded by the word "db"
# e.g python manage.py db init
manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()
