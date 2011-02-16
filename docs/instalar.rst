Instala Shake en un instante
======================================

Shake tiene muy pocas dependencias y viene listo para que tengas una aplicación
web corriendo en minutos.
Para empezar, solo instala Python, el lenguaje, y pip, el administrador de paquetes.


Python

Recomendamos Python 2.7 o Python 2.6 para usar Shake. 
Python 2.5 y las versiones anteriores no están soportadas, tampoco la versión 3.x.

Windows: http://python.org/download/
OS X y la mayoría de distribuciones de Linux viene con una versión actualizada de Python. Pero siempre puedes descargar otra versión o compilarla tu mismo, descargándola desde aquí: http://python.org/download/


pip

Pip es el administrador estándar de paquetes de Python. Similar a apt-get, rpm o a otros administradores de paquetes.


Descárgalo [de http://pypi.python.org/pypi/pip#downloads]
(extráelo y luego ejecuta ``python setup.py install``).


Shake

Con pip instalado, puedes instalar Shake y todas sus dependencias a través de la terminal:

    pip install shake

Puedes bajar otros paquetes o nuevas versiones de Shake de la misma manera.
Si no quieres usar pip, Shake también puede descargarse como una carpeta independiente.  


Crea tu aplicación

Crea tu aplicación y corre el servidor de prueba:

    shake new ruta/hacia/tu/nueva/aplicación
    
    cd ruta/hacia/tu/nueva/aplicación
    
    python manage.py run

¡Ya estás corriendo Shake! Sigue las instrucciones en http://localhost:8000.

