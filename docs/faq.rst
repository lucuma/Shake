
¿Shake escala?

Shake es un framework nuevo, y no ha sido usado en ningún proyecto de gran escala.
Las bibliotecas en las que se apoya (Werkzeug, Jinja y SQLAlchemy) son rápidas y estables y no hay ninguna razón para creer que Shake será el cuello de botella en tu aplicación. Los problemas de escalabilidad están relacionados a menudo con la entrada/salida de datos – como tu base de datos – y Shake no previene que te dispares en el pie.