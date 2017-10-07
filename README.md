[![Build Status](https://travis-ci.org/Chris-Maina/Shoppinglist-api.svg?branch=develop)](https://travis-ci.org/Chris-Maina/Shoppinglist-api) [![Coverage Status](https://coveralls.io/repos/github/Chris-Maina/Shoppinglist-api/badge.svg?branch=develop)](https://coveralls.io/github/Chris-Maina/Shoppinglist-api?branch=develop) [![Code Health](https://landscape.io/github/Chris-Maina/Shoppinglist-api/develop/landscape.svg?style=flat)](https://landscape.io/github/Chris-Maina/Shoppinglist-api/develop)


# Shoppinglist api
Flask API for shopping list application

## Installation and setup
Clone this repo
  * https://github.com/Chris-Maina/Shoppinglist-api.git

Navigate to the shoppinglist-api directory:
  * cd shoppinglist-api

Create a virtual environment and activate it.
  * mkvirtualenv shoppinglist-api 
  * workon shoppinglist-api

Install dependencies:
  * pip install -r requirements.txt

Initialize, migrate and update the database:
  * python manage.py db init 
  * python manage.py db migrate 
  * python manage.py db upgrade

Create a .env file. Add the following lines of code: PS if you're on windows use set instead of export
  * export SECRET="random_key"
  * export APP_SETTINGS="development"
  * export DATABASE_URL=postgresql://postgres-user:password@localhost/db-name

Run source .env if you are on unix or find the equivalent on windows.

## Running application
To start application:
  * python run.py
  
Test the application by running:
  * nosetests --with-coverage --cover-package=app && coverage report
  
Access the endpoints using your preferred client e.g. Postman

#### Endpoints

| Resource URL                                | Methods | Description              | Requires Token |
|---------------------------------------------|---------|--------------------------|----------------|  
| /auth/register/                             | POST    | User registers           | FALSE          |
| /auth/login/                                | POST    | User login               | FALSE          |
| /shoppinglists/                             | POST    | Creates shopping list    | TRUE           |
| /shoppinglists/                             | GET     | Get shopping list        | TRUE           |
| /shoppinglists/<int:slid>                   | PUT     | Edit a shopping list     | TRUE           |
| /shoppinglists/<int:slid>                   | DELETE  | Delete a shopping list   | TRUE           |
| /shoppinglists/<int:slid>                   | GET     | Get a shopping list      | TRUE           |
| /shoppinglists/<int:slid>/items             | POST    | Create a shopping item   | TRUE           |
| /shoppinglists/<int:slid>/items             | GET     | Get shopping items       | TRUE           |
| /shoppinglists/<int:slid>/items/<int:tid>   | PUT     | Edit a shopping item     | TRUE           |
| /shoppinglists/<int:slid>/items/<int:tid>   | DELETE  | Delete a shopping item   | TRUE           |
| /shoppinglists/<int:slid>/items/<int:tid>   | GET     | Get a shopping item      | TRUE           |

#### Options

| Method | Description                 |
|--------|-----------------------------|
| GET    | Retrieves a resource(s)     |
| POST   | Creates a new resource      |
| PUT    | Edits an existing resource  |
| DELETE | Deletes an existing resource|