
# [Awesome Web Application]


This is the initial structure of the project

    ├── main.py
    ├── manage.py
    ├── urls.py

    ├── bundles
        ├── common
            ├── __init__.py
            ├── models.py
            └── views.py
        └── users
            ├── __init__.py
            ├── manage.py
            └── models.py

    ├── docs
        └── README.md
    ├── libs
        └── README.md
 
    ├── locales
        └── en.yml

    ├── requirements
        ├── common.txt
        ├── dev.txt
        ├── prod.txt
        └── test.txt
    ├── requirements.txt

    ├── settings
        ├── __init__.py
        ├── common.py
        ├── dev.py
        ├── prod.py
        └── test.py

    ├── static
        ├── images
            └── favicon.ico
        ├── robots.txt
        ├── scripts
            ├── jquery-1.7.2.min.js
            ├── underscore-1.3.3.min.js
            └── main.js
        └── styles
            └── main.css

    ├── templates
        ├── common
            ├── base.html
            ├── base_error.html
            ├── error.html
            ├── error_notallowed.html
            └── error_notfound.html
        ├── users
        └── index.html

    ├── tests
        └── __init__.py


main.py
:   The file where your main application object is created. A few helper objects (like `db`) are created here as well.

manage.py
:   A command line program for managment tasks. You can add your own commands to this file.

urls.py
:   List of URL routing rules to make the application call a specific view for a given URL.

bundles
:   This subdirectory will contain all your application code organized as `bundles`. Bundles are related models, views, URLs and others (a 'resource' more than a Django app).
    Create one using the `shake add xxxx` command, inside your app root dir.
    Example:

        shake add posts

bundles/common
:   This bundle contains the code for the index page and site-wide pages, like `Not found`.
    Instead of defining new pages and models here, you should create new bundles for the rest of your code.

bundles/users
:   This bundle contain the neccesary code to authenticate your users.

docs
:   This directory is where your application documentation will be stored.

libs
:   Application specific libraries. Basically, any kind of custom code that doesn't belong in a bundle. This directory is added automatically in the path, so anything you put here is directly importable.

locales
:   Strings for internationalization.

requirements
:   Lists of all required third-party applications that are needed to run this project. `common.txt` contains the list of common requirements, while `dev.txt`, `test.txt` and `prod.txt` those specifically for development, testing and production environments.  To install any of them, just do:

    pip install -r requirements/dev.txt

requirements.txt
:   A shortcut to `requirements/prod.txt`. It's customary to have this file. Also, systems like Heroku expect it.

settings
:   This subdirectory contains the configuration code that your application will need, including your database configuration, and others.

static
:   This directory has files that don't change with every request, such as JavaScript files (`static/scripts`), images  (`static/images`), stylesheets (`static/styles`), and others.

templates
:   This subdirectory holds the display templates to fill in with data from our application, convert to HTML (or any other text-based format), and return to the user's browser. The templates uses the Jinja2 syntax by default.

tests
:   The tests you'll write. Yes, you should write tests.


-----
Powered by Shake.
