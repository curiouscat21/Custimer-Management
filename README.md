# Project Title
Customer Management API
## Description
A Customer Management Database System (CMDS) is a software solution designed to store, organize, and manage customer information efficiently. 

## Installation
```cmd
pip install -r requirements.txt

## Configuration
Environment variables needed:
blinker==1.9.0
click==8.1.7
colorama==0.4.6
coverage==7.6.9
Faker==33.1.0
Flask==3.1.0
Flask-JWT-Extended==4.7.1
Flask-MySQLdb==2.0.0
Flask-Testing==0.8.1
iniconfig==2.0.0
itsdangerous==2.2.0
Jinja2==3.1.4
MarkupSafe==3.0.2
marshmallow==3.23.1
mysql-connector-python==9.1.0
mysqlclient==2.2.6
packaging==24.2
pluggy==1.5.0
PyJWT==2.10.1
pytest==8.3.4
pytest-cov==6.0.0
pytest-mock==3.14.0
python-dateutil==2.9.0.post0
six==1.17.0
typing_extensions==4.12.2
Werkzeug==3.1.3

DATABASE_URL
Drew's_secret_key123

## API Endpoints (markdown table)
Endpoint	Method		Description
=====================================
/api/users	GET		List all users
/api/users	POST		Create user
..

## Testing
 Instructions for running tests
…

## Git Commit Guidelines

Use conventional commits:
```bash
feat: add user authentication
fix: resolve database connection issue
docs: update API documentation
test: add user registration tests
