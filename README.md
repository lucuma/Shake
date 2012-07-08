
# Shake

A web framework mixed from the best ingredients (Werkzeug, Jinja and maybe SQLAlchemy, babel, etc.)

```python
from shake import Shake

app = Shake()

def hello(request):
    return 'Hello World!'

app.add_url('/', hello)

if __name__ == "__main__":
    app.run()
```


---------------------------------------
© 2010 by [Lúcuma labs] (http://lucumalabs.com).  
See `AUTHORS.md` for more details.
License: [MIT License] (http://www.opensource.org/licenses/mit-license.php).
