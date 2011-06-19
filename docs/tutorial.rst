.. contents:: Table of Contents

.. _Bottle: http://bottle.paws.org
.. _Python: http://www.python.org
.. _SQLite: http://www.sqlite.org
.. _Windows: http://www.sqlite.org/download.html
.. _PySQLite: http://pypi.python.org/pypi/pysqlite/
.. _`decorator statement`: http://docs.python.org/glossary.html#term-decorator
.. _`Python DB API`: http://www.python.org/dev/peps/pep-0249/
.. _`WSGI reference Server`: http://docs.python.org/library/wsgiref.html#module-wsgiref.simple_server
.. _Cherrypy: http://www.cherrypy.org/
.. _Fapws3: http://github.com/william-os4y/fapws3
.. _Flup: http://trac.saddi.com/flup
.. _Paste: http://pythonpaste.org/
.. _Apache: http://www.apache.org
.. _`Bottle documentation`: http://github.com/defnull/bottle/blob/master/docs/docs.md
.. _`mod_wsgi`: http://code.google.com/p/modwsgi/
.. _`json`: http://www.json.org

Tutorial
=========

This tutorial should give a brief introduction into the Bottle_ WSGI Framework. The main goal is to be able, after reading through this tutorial, to create a project using Bottle. Within this document, not all abilities will be shown, but at least the main and important ones like routing, utilizing the Bottle template abilities to format output and handling GET / POST parameters.

To understand the content here, it is not necessary to have a basic knowledge of WSGI, as Bottle tries to keep WSGI away from the user anyway. You should have a fair understanding of the Python_ programming language. Furthermore, the example used in the tutorial retrieves and stores data in a SQL databse, so a basic idea about SQL helps, but is not a must to understand the concepts of Bottle. Right here, SQLite_ is used. The output of Bottle send to the browser is formated in some examples by the help of HTML. Thus, a basic idea about the common HTML tags does help as well.

For the sake of introducing Bottle, the Python code "in between" is kept short, in order to keep the focus. Also all code within the tutorial is working fine, but you may not necessarily use it "in the wild", e.g. on a public web server. In order to do so, you may add e.g. more error handling, protect the database with a password, test and escape the input etc.

Goals
------

At the end of this tutorial, we will have a simple, web-based ToDo list. The list contains a text (with max 100 characters) and a status (0 for closed, 1 for open) for each item. Through the web-based user interface, open items can be view and edited and new items can be added.

During development, all pages will be available on "localhost" only, but later on it will be show how to adapt the application for a "real" server, including how to use with Apache's mod_wsgi.

Bottle will do the routing and format the output, by the help of templates. The items of the list will be stored inside a SQLite database. Reading and  writing from / the database will be done by Python code.

We will end up with an application with the following pages and functionality:

 * start page ``http://localhost:8080/todo``
 * adding new items to the list: ``http://localhost:8080/new``
 * page for editing items: ``http://localhost:8080/edit/:no`` 
 * catching errors
 * sending static files
 * sending JSON data

Before We Start...
--------------------

Install Bottle
~~~~~~~~~~~~~~~

Assuming that you have a fairly new installation of Python (version 2.5 or higher), you only need to install Bottle in addition to that. Bottle has no other dependencies than Python itself.

You can either manually install Bottle or use Python's easy_install: ``easy_install bottle``

Further Software Necessities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As we use SQLite3 as a database, make sure it is installed. Python versions >= 2.5 usually come with SQlite included, so there is no more work to do. To see if this is really the case, open a Python interpreter and type ``import sqlite3``. In case you do not get an error message, everything is fine and you can jump to the next chapter.

If this is not the case: on Linux systems, most distributions have SQLite3 installed by default. SQLite is available for Windows_ and MacOS X as well. Furthermore, you need Pysqlite_, the Python modules to access SQLite databases. Again, many Linux distributions have the module (often called "python-sqlite3") pre-installed, otherwise just install manually or via ``easy_install pysqlite``.

*Note*: Many older systems may have SQLite2 pre-installed. All examples will work fine with this version, too. You just need to import the corresponding Python module named "sqlite" instead of "sqlite3", as used in the examples below.

Create An SQL Database
~~~~~~~~~~~~~~~~~~~~~~~~

First, we need to create the database we use later on. This can be easily done with the help of Python by running the following script:

::

    #!python
    import sqlite3
    conn = sqlite3.connect("todo.db")
    c = conn.cursor()
    c.execute("CREATE TABLE todo (id INTEGER PRIMARY KEY, task char(100) NOT NULL, status bool NOT NULL)")
    c.execute("INSERT INTO todo (task,status) VALUES ('Read A-byte-of-python to get a good introduction into Python',0)")
    c.execute("INSERT INTO todo (task,status) VALUES ('Visit the Python website',1)")
    c.execute("INSERT INTO todo (task,status) VALUES ('Test various editors for and check the syntax highlighting',1)")
    c.execute("INSERT INTO todo (task,status) VALUES ('Choose your favorite WSGI-Framework',0)")
    conn.commit()
    conn.close()

First, a table called "todo" with the three columns "id", "task", and "status" is generated. "id" is a unique id for each row, which is used later on to reference the rows. The column "task" holds the text which describes the task, it can be max 100 characters long. Finally, the column "status" is used to mark a task as open (value 1) or closed (value 0).

Using Bottle For A Web-Based ToDo List
-----------------------------------------

Now it is time to introduce Bottle in order to create a web-based application. But first, we need to look into a basic concept of Bottle: routes.

Understanding routes
~~~~~~~~~~~~~~~~~~~~~

Basically, each page visible in the browser is dynamically generate when the page address is called. Thus, there is no static content. That is exactly what is called a "route" within Bottle: a certain address on the server. So, for example, when the page ``http://localhost:8080/todo`` is called from the browser, Bottle "grabs" the call and checks if there is any (Python) function defined for the route "todo". If so, Bottle will execute the corresponding Python code and return its result.

First Step - Showing All Open Items
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

So, after understanding the concept of routes, let's create the first one. The goal is to see all open items from the ToDo list:

::

    #!Python
    import sqlite3
    from bottle import route, run
    
    @route('/todo')
    def todo_list():
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("SELECT id, task FROM todo WHERE status LIKE '1'")
        result = c.fetchall()
        return str(result)
        
    run()
    
Save the code a "todo.py", preferable in the same directory as the file "todo.db". Otherwise, you need to add the path to "todo.db" in the ``sqlite3.connect()`` statement.

Let's have a look what we just did: We imported the necessary module "sqlite3" to access to SQLite database and from Bottle we imported "route" and "run". The ``run()`` statement simply starts the web server included in Bottle. By default, the web server serves the pages on localhost and port 8080. Furthermore, we imported "route", which is the function responsible for Bottle's routing. As you can see, we defined one function, "todo_list()", with a few lines of code reading from the database. The important point is the `decorator statement`_ ``@route('/todo')`` right before the ``def todo_list()`` statement. By doing this, we bind this function to the route "/todo", so every time the browsers calls ``http://localhost:8080/todo``, Bottle returns the result of the function "todo_list()". That is how routing within bottle works.

Actually you can bind more than one route to a function. So the following code

::

    #!Python
    ...
    @route('/todo')
    @route('/my_todo_list')
    def todo_list():
        ...
        
will work fine, too. What will not work is to bind one route to more than one function.

What you will see in the browser is what is returned, thus the value given by the ``return`` statement. In this example, we need to convert "result" in to a string by ``str()``, as Bottle expects a string or a list of strings from the return statement. But here, the result of the database query is a list of tuples, which is the standard defined by the `Python DB API`_.

Now, after understanding the little script above, it is time to execute it and watch the result yourself. Remember that on Linux- / Unix-based systems the file "todo.py" needs to be made executable first. Then, just run ``python todo.py`` and call the page ``http://localhost:8080/todo`` in your browser. In case you made no mistake writing the script, the output should look like this:

::

    #!Python
    [(2, u'Visit the Python website'), (3, u'Test various editors for and check the syntax highlighting')]
    
If so - congratulations! You are now a successful user of Bottle. In case it did not work and you need to make some changes to the script, remember to stop Bottle serving the page, otherwise the revised version will not be loaded.

Actually, the output is not really exciting nor nice to read. It is the raw result returned from the SQL-Query.

So, in the next step we format the output in a nicer way. But before we do that, we make our life easier.

Debugging and Auto-Reload
~~~~~~~~~~~~~~~~~~~~~~~~~~

Maybe you already experienced the Bottle sends a short error message to the browser in case something within the script is wrong, e.g. the connection to the database is not working. For debugging purposes it is quiet helpful to get more details. This can be easily achieved by adding the following statement to the script:

::

    #!Python
    from bottle import run, route, debug
    ...
    #add this at the very end:
    debug(True)
    run()

By enabling "debug", you will get a full stacktrace of the Python interpreter, which usually contains useful information for finding bugs. Furthermore, templates (see below) are not cached, thus changes to template will take effect without stopping the server.

**Note** that ``debug(True)`` is supposed to be used for development only, it should *not* be used in productive environments.

A further quiet nice feature is auto-reloading, which is enabled by modifying the ``run()`` statement to

::

    #!Python
    run(reloader=True)
    
This will automatically detect changes to the script and reload the new version once it is called again, without the need to stop and start the server.

Again, the feature is mainly supposed to be used while development, not on productive systems.

Bottle Template To Format The Output
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now let's have a look to cast the output of the script into a proper format.

Actually Bottle expects to receive a string or a list of strings from a function and returns them by the help of the build-in server to the browser. Bottle does not bother about the content of the string itself, so it can be text formated with HTML markup, too.

Bottle brings its own easy-to-use template engine with it. Templates are stored as separate files having a ".tpl" extension. The template can be called then from within a function. Templates can contain any type of text (which will be most likely HTML-markup mixed with Python statements). Furthermore, templates can take arguments, e.g. the result set of a database query, which will be then formated nicely within the template.

Right here, we are going to cast the result of our query showing the open ToDo items into a simple table with two columns: the first column will contain the ID of the item, the second column the text. The result set is, as seen above, a list of tuples, each tuple contains one set of results.

To include the template into our example, just add the following lines:

::

    #!Python
    from bottle import from bottle import route, run, debug, template
    ...
    result = c.fetchall()
    conn.close()
    output = template('make_table', rows=result)
    return output
    ...
    
So we do here two things: First, we import "template" from Bottle in order to be able to use templates. Second, we assign the output of the template "make_table" to the variable "output", which is then returned. In addition to calling the template, we assign "result", which we received from the database query, to the variable "rows", which is later on used within the template. If necessary, you can assign more than one variable / value to a template.

Templates always return a list of strings, thus there is no need to convert anything. Of course, we can save one line of code by writing ``return template('make_table', rows=result)``, which gives exactly the same result as above.

Now it is time to write the corresponding template, which looks like this:

::

    #!html
    %#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
    <p>The open items are as follows:</p>
    <table border="1">
    %for row in rows:
      <tr>
      %for r in row:
        <td>{{r}}</td>
      %end
      </tr>
    %end
    </table>

Save the code as "make_table.tpl" in the same directory where "todo.py" is stored.

Let's have a look at the code: Every line starting with % is interpreted as Python code. Please note that, of course, only valid Python statements are allowed, otherwise the template will raise an exception, just as any other Python code. The other lines are plain HTML-markup.

As you can see, we use Python's "for"-statement two times, in order to go through "rows". As seen above, "rows" is a variable which holds the result of the database query, so it is a list of tuples. The first "for"-statement accesses the tuples within the list, the second one the items within the tuple, which are put each into a cell of the table. Important is the fact that you need additionally close all "for", "if", "while" etc. statements with ``%end``, otherwise the output may not be what you expect.

If you need to access a variable within a non-Python code line inside the template, you need to put it into double curly braces. This tells the template to insert the actual value of the variable right in place.

Run the script again and look at the output. Still not really nice, but at least better readable than the list of tuples. Of course, you can spice-up the very simple HTML-markup above, e.g. by using in-line styles to get a better looking output.

Using GET And POST Values
~~~~~~~~~~~~~~~~~~~~~~~~~~~

As we can review all open items properly, we move to the next step, which is adding new items to the ToDo list. The new item should be received from a regular HTML-based form, which sends its data by the GET-method.

To do so, we first add a new route to our script and tell the route that it should get GET-data:

::

    #!Python
    from bottle import route, run, debug, template, request
    ...
    return template('make_table', rows=result)
    ...
    
    @route('/new', method='GET')
    def new_item():
    
        new = request.GET.get('task', '').strip()
        
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        
        c.execute("INSERT INTO todo (task,status) VALUES (?,?)", (new,1))
        c.execute("SELECT last_insert_rowid()")
        new_id = c.fetchone()[0]
        conn.commit()
        conn.close
        
        return '<p>The new task was inserted into the database, the ID is %s</p>
       
To access GET (or POST) data, we need to import "request" from Bottle. To assign the actual data to a variable, we use the statement ``request.GET.get('task','').strip()`` statement, where "task" is the name of the GET-data we want to access. That's all. If your GET-data has more than one variable, multiple ``request.GET.get()`` statements can be used and assigned to other variables. By the way: This works exactly the same way with POST data. Just replace "GET" with "POST" in the above (and the following) examples.

The rest of this piece of code is just processing of the gained data: writing to the database, retrieve the corresponding id from the database and generate the output.

But where do we get the GET-data from? Well, we can use a static HTML page holding the form. Or, what we do right now, is to use a template which is output when the route "/new" is called without GET-data.

The code need to be extended to:

::

    #!Python 
    ...
    @route('/new', method='GET')
    def new_item():

    if request.GET.get('save','').strip():

        new = request.GET.get('task', '').strip()
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()

        c.execute("INSERT INTO todo (task,status) VALUES (?,?)", (new,1))
        conn.commit()

        c.execute("SELECT last_insert_rowid()")
        new_id = c.fetchone()[0]
        conn.close()
          
        return '<p>The new task was inserted into the database, the ID is %s</p>' %new_id
    
    else:
        return template('new_task.tpl')
    ...

"new_task.tpl" looks like this:

::

    #!html
    <p>Add a new task to the ToDo list:</p>
    <form action="/new" method="GET">
    <input type="text" size="100" maxlength="100" name="task">
    <input type="submit" name="save" value="save">
    </form>
    
That's all. As you can see, the template is plain HTML this time.

Now we are able to extend our to do list.

Editing Existing Items - Dynamic Routes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The last point to do is to enable editing of existing items.

By using the routes we know so far only it is possible, but may be quiet tricky. But Bottle knows something called "dynamic routes", which makes this task quiet easy.

The basic statement for a dynamic route looks like this:

::

    #!Python
    @route('/myroute/:something')
    
The key point here is the colon. This tells Bottle to accept for ":something" any string up to the next slash. Furthermore, the value of "something" will be passed to the function assigned to that route, so the data can be processed within the function.

For our ToDo list, we will create a route ``@route('/edit/:no)``, where "no" is the id of the item to edit.

The code looks like this:

::

    #!Python
    @route('/edit/:no', method='GET')
    def edit_item(no):

        if request.GET.get('save','').strip():
            edit = request.GET.get('task','').strip()
            status = request.GET.get('status','').strip()
    
            if status == 'open':
                status = 1
            else:
                status = 0
        
            conn = sqlite3.connect('todo.db')
            c = conn.cursor()
            c.execute("UPDATE todo SET task = ?, status = ? WHERE id LIKE ?", (edit,status,no))
            conn.commit()
            conn.close()
        
            return '<p>The item number %s was successfully updated</p>' %no

        else:
            conn = sqlite3.connect('todo.db')
            c = conn.cursor()
            c.execute("SELECT task FROM todo WHERE id LIKE ?", str(no))
            cur_data = c.fetchone()
            conn.close()
        
            return template('edit_task', old = cur_data, no = no)

It is basically pretty much the same what we already did above when adding new items, like using "GET"-data etc. The main addition here is using the dynamic route ":no", which here passes the number to the corresponding function. As you can see, "no" is used within the function to access the right row of data within the database.

The template "edit_task.tpl" called within the function looks like this:

::

    #!html
    %#template for editing a task
    %#the template expects to receive a value for "no" as well a "old", the text of the selected ToDo item
    <p>Edit the task with ID = {{no}}</p>
    <form action="/edit/{{no}}" method="get">
    <input type="text" name="task" value="{{old[0]}}" size="100" maxlength="100">
    <select name="status">
    <option>open</option>
    <option>closed</option>
    </select>
    <br/>
    <input type="submit" name="save" value="save">
    </form>

Again, this template is a mix of Python statements and HTML, as already explained above.

A last word on dynamic routes: you can even use a regular expression for a dynamic route. This is shown a bit later in this tutorial.

Validating Dynamic Routes
~~~~~~~~~~~~~~~~~~~~~~~~~~

In documentations on previous versions of Bottle, you may find sections describing the ``@valdiate`` decorator. Since version 0.7, this feature is marked at "deprecated". This reason for this is, in very short words, that it is in most cases more useful to take care of validation yourself, if needed. Thus, validating routes by ``@validate`` is not explained any further here.


Dynamic Routes Using Regular Expressions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bottle can also handle dynamic routes, where the "dynamic part" of the route can be a regular expression.

So, just to demonstrate that, let's assume that all single items in our ToDo list should be accessible by their plain number, by a term like e.g. "item1". For obvious reasons, you do not want to create a route for every item. Furthermore, the simple dynamic routes do not work either, as part of the route, the term "item" is static.

As said above, the solution is a regular expression:

::

    #!Python
    ...

    @route('/item:item#[1-9]+#')
    def show_item(item):
    
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("SELECT task FROM todo WHERE id LIKE ?", item)
        result = c.fetchall()
        conn.close()
            
        if not result:
            return 'This item number does not exist!'
        else:
            return 'Task: %s' %result[0]


    ...
        
Of course, this example is somehow artificially constructed - it would be easier to use a plain dynamic route only combined with a validation. Nevertheless, we want to see how regular expression routes work: The line ``@route(/item:item_#[1-9]+#)`` starts like a normal route, but the part surrounded by # is interpreted as a regular expression, which is the dynamic part of the route. So in this case, we want to match any digit between 0 and 9. The following function "show_item" just checks whether the given item is present in the database or not. In case it is present, the corresponding text of the task is returned. As you can see, only the regular expression part of the route is passed forward. Furthermore, it is always forwarded as a string, even if it is a plain integer number, like in this case.

Returning Static Files
~~~~~~~~~~~~~~~~~~~~~~~

Sometimes it may become necessary to associate a route not to a Python function, but just return a static file. So if you have for example a help page for your application, you may want to return this page as plain HTML. This works as follows:

::

    #!Python
    from bottle import route, run, debug, template, request, send_file

    ...
        
    @route('/help')
    def help():

        send_file('help.html', root='/path/to/file')
       
    ...
        
At first, we need to import ``send_file`` from Bottle. As you can see, the ``send_file`` statement replace the ``return`` statement. It takes at least two arguments: The name of the file to be returned and the path to the file. Even if the file is in the same directory as your application, the path needs to be stated. But in this case, you can use ``'.'`` as a path, too. Bottle guesses the MIME-type of the file automatically, but in case you like to state it explicitly, add a third argument to ``send_file``, which would be here ``mimetype='text/html'``. ``send_file`` works with any type of route, including the dynamic ones.

Returning JSON Data
~~~~~~~~~~~~~~~~~~~~

There may be cases where you do not want your application to generate the output directly, but return data to be processed further on, e.g. by JavaScript. For those cases, Bottle offers to possibility to return JSON objects, which is sort of standard for exchanging data between web applications. Furthermore, JSON can be processed by many programming languages, including Python

So, let's assume we want to return the data generated in the regular expression route example as a JSON object. The code looks like this:

::

    #!Python
    ...

    @route('/json:json#[1-9]+#')
    def show_json(json):
    
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("SELECT task FROM todo WHERE id LIKE ?", item)
        result = c.fetchall()
        conn.close()
            
        if not result:
            return {'task':'This item number does not exist!'}
        else:
            return {'Task': result[0]}

    ...

As you can, that is fairly simple: Just return a regular Python dictionary and Bottle will convert it automatically into a JSON object prior to sending. So if you e.g. call "http://localhost/json1" Bottle should in this case return the JSON object ``{"Task": ["Read A-byte-of-python to get a good introduction into Python"]}``.


Catching Errors
~~~~~~~~~~~~~~~~

The next step may is to catch the error with Bottle itself, to keep away any type of error message from the user of your application. To do that, Bottle has an "error-route", which can be a assigned to a HTML-error.

In our case, we want to catch a 403 error. The code is as follows:

::

    #!Python
    from bottle import route, run, debug, template, request, send_file, error
    
    ...
    
    @error(403)
    def mistake(code):
        return 'The parameter you passed has the wrong format!'
        
So, at first we need to import "error" from Bottle and define a route by ``error(403)``, which catches all "403 forbidden" errors. The function "mistake" is assigned to that. Please note that ``error()`` always passed the error-code to the function - even if you do not need it. Thus, the function always needs to accept one argument, otherwise it will not work.

Again, you can assign more than one error-route to a function, or catch various errors with one function each. So this code:

::

    #!Python
    @error(404)
    @error(403)
    def mistake(code):
        return 'There is something wrong!'
        
works fine, the following one as well:

::

    #!Python
    @error(403)
    def mistake403(code):
        return 'The parameter you passed has the wrong format!'
        
    @error(404)
    def mistake404(code):
        return 'Sorry, this page does not exist!'

Summary
~~~~~~~~
After going through all the sections above, you should have a brief understanding how the Bottle WSGI framework works. Furthermore you have all the knowledge necessary to use Bottle for you applications.

The following chapter give a short introduction how to adapt Bottle for larger projects. Furthermore, we will show how to operate Bottle with web servers which performs better on a higher load / more web traffic than the one we used so far.

Server Setup
-------------

So far, we used the standard server used by Bottle, which is the `WSGI reference Server`_ shipped along with Python. Although this server is perfectly suitable for development purposes, it is not really suitable for larger applications. But before we have a look at the alternatives, let's have a look how to tweak the setting of the standard server first

Running Bottle on a different port and IP
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As a standard, Bottle does serve the pages on the IP-adress 127.0.0.1, also known as "localhost", and on port "8080". To modify there setting is pretty simple, as additional parameters can be passed to Bottle's ``run()`` function to change the port and the address.

To change the port, just add ``port=portnumber`` to the run command. So, for example

::

    #!Python
    run(port=80)
    
would make Bottle listen to port 80.

To change the IP-address where Bottle is listing / serving can be change by

::

    #!Python
    run(host='123.45.67.89')
    
Of course, both parameters can be combined, like:

::

    #!Python
    run(port=80, host='123.45.67.89')
    
The ``port`` and ``host`` parameter can also be applied when Bottle is running with a different server, as shown in the following section

Running Bottle with a different server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As said above, the standard server is perfectly suitable for development, personal use or a small group of people only using your application based on Bottle. For larger task, the standard server may become a Bottle neck, as it is single-threaded, thus it can only serve on request at a time.

But Bottle has already various adapters to multi-threaded server on board, which perform better on higher load. Bottle supports Cherrypy_, Fapws3_, Flup_ and Paste_.

If you want to run for example Bottle with the past server, use the following code:

::

    #!Python
    from bottle import PasteServer
    ...
    run(server=PasterServer)
    
This works exactly the same way with ``FlupServer``, ``CherryPyServer`` and ``FapwsServer``.

Running Bottle on Apache with mod_wsgi
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Maybe you already have an Apache_ or you want to run a Bottle-based application large scale - than it is time to think about Apache with mod_wsgi_.

We assume that your Apache server is up and running and mod_wsgi is working fine as well. On a lot of Linux distributions, mod_wsgi can be installed via the package management easily.

Bottle brings a adapter for mod_wsgi with it, so serving your application is an easy task.

In the following example, we assume that you want to make your application "ToDO list" accessible through "http://www.mypage.com/todo" and your code, templates and SQLite database is stored in the path "var/www/todo".

At first, we need to import "defautl_app" from Bottle in our little script:

::

    #!Python
    from bottle import route, run, debug, template, request, send_file, error, default_app
    
When you run your application via mod_wsgi, it is imperative to remove the ``run()`` statement from you code, otherwise it won't work here.

After that, create a file called "adapter.wsgi" with the following content:

::

    #!Python
    import sys
    sys.path = ['/var/www/todo/'] + sys.path

    import todo
    import os

    os.chdir(os.path.dirname(__file__))

    application = default_app()

and save it in the same path, "/var/www/todo". Actually the name of the file can be anything, as long as the extensions is ".wsgi". The name is only used to reference the file from your virtual host.

Finally, we need to add a virtual host to the Apache configuration, which looks like this:

::

    #!ApacheConf
        <VirtualHost *>
            ServerName mypage.com
            
            WSGIDaemonProcess todo user=www-data group=www-data processes=1 threads=5
            WSGIScriptAlias / /var/www/todo/adapter.wsgi
            
            <Directory /var/www/todo>
                WSGIProcessGroup todo
                WSGIApplicationGroup %{GLOBAL}
                Order deny,allow
                Allow from all
            </Directory>
        </VirtualHost>
        
After restarting the server, your the ToDo list should be accessible at "http://www.mypage.com/todo"

Final Words
-------------

Now we are at the end of this introduction and tutorial to Bottle. We learned about the basic concepts of Bottle and wrote a first application using the Bottle framework. In addition to that, we saw how to adapt Bottle for large task and server Bottle through a Apache web server with mod_wsgi.

As said in the introduction, this tutorial is not showing all shades and possibilities of Bottle. What we skipped here is e.g. receiving File Objects and Streams and how to handle authentication data. Furthermore, we did not show how templates can be called from within another template. For an introduction into those points, please refer to the full `Bottle documentation`_ .
