===========
Plantillas
===========

Aunque puedes armar una página web concatenado manualmente trozos de código, esto es poco práctico y rápidamente se hace difícil de mantener y propenso a errores. En vez de eso, lo más práctico es usar un sistema de plantillas.

Una plantilla es simplemente un archivo de texto con variables, que son reemplazadas por valores cuando la plantilla se evalúa; y etiquetas, que controlan la lógica de la plantilla, por ejemplo repitiendo ciertas líneas o mostrando una sección solo en ciertos casos.

Puede generar cualquier formato basado en texto, como HTML, XML o CSV, y no necesita tener una extensión particular, así que usar algo como .html o .xml, está bien.

Para sus plantillas, Shake usa la biblioteca Jinja2. Si tienes experiencia con otros sistemas de plantillas como el de Django o Smarty, deberías sentirte como en casa.

..Nota:
    Jinja2 tiene una documentación oficial –en ingles– detallada. Para detalles más avanzados no dejes de consultarla.

Sintaxis
========

Lo de abajo es un ejemplo de plantilla ilustrando algunos conceptos comunes. Cubriremos los detalles más adelante en este documento


    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <title>Mi página</title>
    </head>
    <body>
        <ul id="menu">
        {% for item in menu %}
				<li><a href="{{ item.url }}">{{ item.nombre }}</a></li>
        {% endif %}
        </ul>
        
        <h1>Mi página>
        {{ una_variable }}
    </body>
    </html>

Hay dos tipos de delimitadores aquí: {% … %} y {{ … }}. El primero lo usas para controlar la lógica de la plantilla y el segundo para imprimir un valor o el resultado de una expresión.

Para llamar a las plantillas desde Shake usas la clase `Render`.

>>> from shake import Render
>>> render = Render('carpeta_de_plantillas')
>>> render('miplantilla.html')

Solo es necesario instanciar `Render` una vez, y puedes reusar el objeto `render’ en todas tus vistas.
Por defecto el navegador interpretará el resultado como HTML, pero si no lo fuera, tenemos que especificarlo usando `mimetype`:

>>> render('miplantilla.txt', mimetype='text/plain')


Estructuras de control
-----------------------

Las estructuras de control son instrucciones que cambian lógica de la plantilla, como condicionales (e.g. if/elif/else), bucles (e.g. for/while) y macros.

En Jinja2 estas aparecen dentro de {% … %} con una sintáxis muy similar a la del mismo python. *No* encontrarás cosas como un {% ifequal foo bar %}, si no, más bien {% if foo ==  bar %}.

Mira la [lista de estructuras de control], para una descripción detallada de cada una.


Variables
---------

as variableTu aplicación le pasa variables a una plantilla usando un diccionario, de esta forma:

>>> render('miplantilla.html', {‘nombre’: valor, … })

Como la plantilla use esa variable depende de su valor (¿es una lista, un diccionario, un número entero?), pero la sintaxis para hacerlo es muy similar a código en Python. Las siguientes dos líneas hacen lo mismo.

{{ foo.bar }}
{{ foo[‘bar’] }}

Nota que las llaves aquí son la orden imprimir y no parte del valor. No van a salir en el resultado final y si usas una variable dentro de otra expresión, no es necesario repetirlas.

{{ variable1 * variable2 + ‘ días’ }}

Si intentas usar una variable o un atributo que no existe, obtendrás como resultado un valor ‘indefinido’ que, por defecto, se imprimirá como un texto vacío (aunque puede cambiarse este comportamiento).

..Nota:
	En Jinja2, las constantes especiales True, False, y None, tambien pueden escribirse en minúsculas (true, false y none). La idea es mantener la consistencia en el lenguaje de la plantilla (los demás identificadores en Jinja2 están en minúsculas). Personalmente, prefiero las originales (consistentes con el *código* de la aplicación), para evitar tener que pensar cual versión usar.


Filtros
--------

Las variables pueden modificarse con *filtros*. Los filtros se separan de las variables por una línea vertical (|) y pueden tener argumentos opcionales en parèntesis. Además, los  filtros pueden encadenarse: El resultado de uno es usado como valor de entrada del siguiente.

{{ nombre|striptags|title }} por ejemplo, quitara todas las etiquetas HTML de `nombre` y pondrá en mayúsculas su primera letra. Los filtros que aceptan argumentos tienen paréntesis alrededor de ellos, como llamando a una función. Este ejemplo juntará una lista con comas: {{ lista|join(‘, ‘) }}.

La [lista de filtros incluidos], más abajo, describe todos los filtros que un plantilla incluye por defecto.

Agregar tus propios filtros es muy fácil. Basta hacer una función que tome como primer argumento el valor original.

>>> def entre_tres(valor)
>>>     return valor / 3

>>> render.set_filter(‘entre_tres’, entre_tres)


Tests
------


...

[Custom tests]


Herencia
---------

...

Escapado de HTML
----------------

...

Lista de estructuras de control
-----------------

...

Lista de filtros
-----------------

...

Lista de tests
-----------------

...

Lista de funciones globales
----------------------------

...


Trucos
-------

[funciones de loop, resaltar sección activa, null-master fallback, whitespace control]


Temas avanzados
---------------

[Loaders, cache]


