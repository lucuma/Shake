
# Awesome web application

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

    ├── settings
        ├── __init__.py
        ├── common.py
        ├── development.py
        ├── production.py
        ├── testing.py
	    ├── req.txt
		  ├── req-dev.txt
			└── req-prod.txt

    ├── static
        ├── images
            └── favicon.ico
        ├── scripts
            ├── jquery-1.7.1.min.js
            ├── main.js
            ├── selectivizr.js
            └── underscore-1.1.6.min.js
        └── styles
            └── main.css
        └── robots.txt

    ├── tests
        └── __init__.py

    └── templates
        ├── common
            ├── base.html
            ├── base_error.html
            ├── error.html
            ├── error_notallowed.html
            └── error_notfound.html
        ├── users
        └── index.html


main.py
:   The file where your main application object is created. A few helper objects (like `db`) are created here as well.

manage.py
:   A command line program for managment tasks. You can add your own commands to this file.

urls.py
:   List of URL routing rules to make the application call a specific view for a given URL.

bundles
:   This subdirectory will contain all your application code organized as `bundles`. Bundles are related models, views, URLs and others.
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

settings
:   This subdirectory contains the configuration code that your application will need, including your database configuration, required modules and others.

:   `base.py` contains the general settings, while `development.py`, `testing.py` and `production.py` are settings specifically for those environments.

:   `req.txt` contains list of the python modules required by your aplicación. To install all of them, just do:

        pip install -r req.txt

:   `req-dev.txt` and `req-prod.txt` are also lists of required python modules `req.txt` but only those used specifically only in development or production environments.

static
:   This directory has web files that don't change, such as JavaScript files (`static/scripts`), images  (`static/images`), stylesheets (`static/styles`), and others.

tests
:   The tests you'll write. Yes, you should write tests.

templates
:   This subdirectory holds the display templates to fill in with data from our application, convert to HTML (or any other text-based format), and return to the user's browser. All templates uses the Jinja2 syntax by default.


-----
Powered by Shake
