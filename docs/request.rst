

Los datos enviados a la vista en la URL (ej. 'example.org/?foo=bar') se guardan en request.args. Los datos enviados por POST, en request.form. En request.values se tiene una combinación de ambos.

Es común que se envien en formularios webs, varias valores bajo el mismo nombre. En esos casos, apareceran en form, args y values como una lista.

<input type="checkbox" name="id" value="4">
<input type="checkbox" name="id" value="5">
<input type="checkbox" name="id" value="6">

luego

>>> request.form['id']
['4', '5', '6']

Aunque tengamos un campo en un formulario, no hay garantía que este se envíe con un valor (es incluso posible para un usuario manipular localmente el código del formulario antes de enviarlo). Por eso, para evitar que salten errores, es muy recomendable usar la función ´get´ para obtener los valores de los campos, en vez de la notación de corchetes.

>>> request.form.get('id')
['4', '5', '6']

Como su equivalente en un diccionario regular, puede especificarse un valor por defecto en caso no se encuentre dicho campo

>>> request.form.get('zzz', 'valor_por_defecto')
'valor_por_defecto'

La función `get` de estos diccionarios especiales, acepta un tercer parámetro `type` que indica el tipo de dato al que debe convertirse el valor. Si el valor no puede convertirse a ese tipo, se devuelve el valor por defecto.

<input type="checkbox" name="foo" value="4">

>>> request.form.get('foo', type=int)
4

Nota que `type` es realmente una función, por lo que puedes pasarle tus propias funciones de conversión para casos especiales.
Si hay más de un valor para el mismo nombre, se intentará convertir cada uno de ellos. Si la conversión falla, ese valor no será agregado a la lista final. Si ningún valor puede convertirse al tipo deseado, se devolverá el valor por defecto.

<input type="checkbox" name="id" value="4">
<input type="checkbox" name="id" value="bar">
<input type="checkbox" name="id" value="6">

>>> request.form.get('id')
['4', 'bar', '6']
>>> request.form.get('id', type=int)
[4, 6]
>>> request.form.get('id', 'narf', type=dict)
'narf'


