# transfers

## Buiding and running for the first time
You need to have Python 3 (tested with Python 3.7.1) and you should have virtualenv configured

Install django and DRF
- `pip install django`
- `pip install djangorestframework`

You could also install coverage 
- `pip install coverage`

To run the project you need to:
- set up your database
`python manage.py makemigrations sharing`
`python manage.py migrate`

- run the server
`python manage.py runserver`

## Testing

To run unit tests:
`python manage.py test`

To run coverage:
`coverage run --source='.' manage.py test sharing`
`coverage report`
