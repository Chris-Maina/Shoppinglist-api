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
  * python run.py db init 
  * python run.py db migrate 
  * python run.py db upgrade

Test the application by running:
  * nosetests test_file_name

## Running application
To start application:
  * python run.py
  
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