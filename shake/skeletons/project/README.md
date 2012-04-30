
# Welcome to Shake

This is the initial structure of your project

    ├── main.py
    ├── manage.py
    ├── requirements.txt
    ├── urls.py

    ├── bundles
        ├── common
            ├── __init__.py
            ├── controllers.py
            └── models.py
        └── users
            ├── __init__.py
            ├── manage.py
            └── models.py

    ├── docs
        └── README.md
    ├── libs
        └── README.md

    ├── settings
        ├── __init__.py
        ├── dev.py
        └── prod.py

    ├── static
        ├── robots.txt
        ├── images
            └── favicon.ico
        ├── scripts
            ├── jquery-1.7.1.min.js
            ├── main.js
            ├── selectivizr.js
            └── underscore-1.1.6.min.js
        └── styles
            └── main.css

    ├── tests
        └── __init__.py

    └── views
        ├── users
        ├── base.html
        ├── error_notfound.html
        ├── error.html
        └── index.html


main.py
:   The file where your main application object is created.
    A few helper objects (like `render`) are created here as well.
    Your database(s) handler is created here, but do not add your models
    here, do it inside a bundle instead.

manage.py
:   A command line program for managment tasks. You can add your
    own commands to this file.

requirements.txt
:   A list of the python modules required by your aplicación. To
    install all of them, just do:

        pip install -r requierements.txt

urls.py
:   List of URL routing rules to make the application call a
    specific controller for a given URL.

bundles
:   This subdirectory will contain all your application code organized as
    `bundles`. Bundles are related models, controllers, URLs, views and others.
    Create one using the `shake add xxxx` command, inside your app root dir. Eg:

        shake add posts

bundles/common
:   This bundle contains the code for the index page and site-wide
    pages, like `Not found`.
    Instead of defining new pages and models here, you should create new 
    bundles for the rest of your code.

bundles/users
:   This bundle contain the neccesary code to authenticate your users

docs
:   This directory is where your application documentation will be stored

libs
:   Application specific libraries. Basically, any kind of custom code
    that doesn't belong in your bundles. This directory is added
    automatically in the path, so anything you put here is directly
    importable.

settings
:   This subdirectory contains the small amount of configuration
    code that your application will need, including your
    database configuration and others.
    '__init__.py` contains the general settings, while 
    `dev.py` and `prod.py` are settings specifically for the
    development and production environments.

static
:   This directory has web files that don't change, such as
    JavaScript files (`static/scripts), images 
    (`static/images`), stylesheets (`static/styles`),
    and others.

tests
:   The tests you'll write. Yes, you should write tests.

views
:   The views subdirectory holds the display templates to fill
    in with data from our application, convert to HTML (or any
    other text-based format), and return to the user's browser.
    All templates uses the Jinja2 syntax by default.

