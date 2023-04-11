


# BOOKSHELF
Application made as part of the udemy course.
REST API for library.
Documentation can be found in documentation.html or [here](https://documenter.getpostman.com/view/26035390/2s93Jxr1qX)

## Authors

- [@JakubPiecha](https://github.com/JakubPiecha)


## Running Tests

To run tests, run the following command

```bash
  python -m pytest
```


## Technologies Used

- python 3.10
- Flask 2.2.3
- Flask-Migrate 4.0.4
- Flask-SQLAlchemy 3.0.3
- MySql
- AWS
- Postman

## Installation

 Clone the repository

```bash
git clone git@github.com:JakubPiecha/bookshelf.git
```
or if you don't have ssh 

```bash
git clone https://github.com/JakubPiecha/bookshelf.git
```

- Create virtual environment to install dependencies and activate it:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables

- To run this project, you will need to add the following environment variables to your .env file
- Rename .env.example to .env
- Create database and user
- migrate database

```bash
flask db upgrade
```

You can load sample data into the database

```bash
flask db-manage add-data
```
Start app

```bash
flask run
```

