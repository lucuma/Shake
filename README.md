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

Coded by Juan-Pablo Scaletti <juanpablo@lucumalabs.com>.<br />
Copyright © 2011 by [Lúcuma labs] (http://lucumalabs.com).<br />
License: [MIT License] (http://www.opensource.org/licenses/mit-license.php).
