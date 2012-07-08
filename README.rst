========
Shake
========

A web framework mixed from the best ingredients (Werkzeug, Jinja and maybe SQLAlchemy, babel, etc.)

::
    from shake import Shake

    app = Shake()

    def hello(request):
        return 'Hello World!'

    app.add_url('/', hello)

    if __name__ == "__main__":
        app.run()
