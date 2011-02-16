En el universo de frameworks web d epython, estas tienden hacia los extremos. Un enfoque es tratar de englobar cualquier código bajo una superficie uniforme. El otro es dar la mayor cantidad de opciomnes de configuración y librerías diferentes y disímiles para cada una de sus funciones.

El primer enfoque

Best of the breed. El problema es que no se toma esa decisión
El segundo enfoque defeats el proósito de tener un frmework en primer lugar. Elegir entre uns sistema de plantillas u otro, por ejemplo, requiere conocerlas y probarlas. Demasiadas opciones paralizan.

Con Shake intentamos alcanzar el equilibrio entre estos dos extremos. Queremos que pueda compartirse conocimiento entre otra scomunidades por lo que aprovechamos librerías como Jinja2 para el sistema de plamntillas y SQLAlchemy pero solo una por sistema. Se integran pero con una ligera capa que no oculta su verdadero origen.


Además queremos que el código sea visible lo más posible al programador final. 
Y lo más estable
Por eso (inspirados en la filosofia de Jquery) shake s emantendrá lo más compacto al mínimo. Cualquier funcionalidad extra vendra a través de extensiones: Algunas de ellas "oficiales" pero otras no.
Un nucleo pequeño significa menos API que aprender y conocerla por completo más rápido.