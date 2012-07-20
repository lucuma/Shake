================
Shake
================

A web framework mixed from the best ingredients (Werkzeug, Jinja2 and maybe SQLAlchemy, Babel, etc.)

It can be minimal like this::

    from shake import Shake

    app = Shake(__file__)

    app.route('/', hello)
    def hello(request):
        return 'Hello World!'        

    if __name__ == "__main__":
        app.run()

Or a full featured (yet configurable if needed) framework.
