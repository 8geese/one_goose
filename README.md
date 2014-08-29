# one_goose

http://onegoose.herokuapp.com/api/v1/

## notes

### running on heroku

1. Create a heroku app
2. attach postgres
3. push repo to heroku
4. `heroku config:set env=heroku`
5. `heroku run python manage.py syncdb`
6.  `heroku run python manage.py migrate`
7. `heroku restart`


### running locally

Create a `local_settings.py` inside the `one_goose` directory, and override the DATABASES to your database of choice.


#### Example `local_settings.py` ####
~~~
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'database.sql',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': ''
    }
}
~~~


### running unit tests

Just use the django test runner:

`python manage.py tests`
