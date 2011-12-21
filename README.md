
# Shake

A web framework mixed from the best ingredients:

    from shake import Shake, Rule

    def hello(request):
        return 'Hello World!'

    urls = [Rule('/', hello),]

    app = Shake(urls)

    if __name__ == "__main__":
        app.run()


---------------------------------------
Copyright © 2011 by [Lúcuma labs] (http://lucumalabs.com).  
See `AUTHORS.md` for more details.  
License: [MIT License] (http://www.opensource.org/licenses/mit-license.php).
