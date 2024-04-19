# Lambda-Coinmarket
Una funcion que extrae informacion del precio de bitcoin y ethereum para insertarlo en una base de datos. Esta funcion tiene la intencion de ser una funcion lambda de AWS
## Dependencies

- urllib3
- mysqlconnector

La funcion necesita de estas librerias para funcionar correctamente

## Installation

```sh
pip install urllib3==1.26.6
```
Fue necesarion instalar esta version de urllib para evitar conflictos con AWS: 
ImportError: urllib3 v2.0 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with LibreSSL 2.8.3
This text you see here is *actually- written in Markdown! To get a feel
for Markdown's syntax, type some text into the left window and
watch the results in the right.

```sh
pip mysql-connector-python
```


## Lambda

Lambda tiene un limite de 10MB por carga de .zip, en caso de sobrepasar el limite no se podra editar desde la consola de lambda. Para ello usamos 
las capas de AWS para cargar las dependencias por separado:

<img title="a title" alt="Alt text" src="/lambda_function.png">

Capa para dependencias:
<img title="a title" alt="Alt text" src="/layer-dep.png">

Estructura de cargas para dependencias:
<img title="a title" alt="Alt text" src="/dep-structure.png">

##Conexion RDS y Lambda

Para la conexion de la RDS y Lambda he creado una VPC con subredes publicas y privadas
y he colocado la funcion lambda y la RDS en la misma VPC para que puedan conectarse sin problemas.
He creado un Security Group individual para cada uno.

- Para la RDS he creado una regla de entrada para mi IP y el security group de lambda
- Para Lambda he creado una regla de salida que permita todo el trafico pues necesita conexion a internet
para consumir la api de Coinmarketcap

Finalmente para que lambda tenga una conexion a internet configure un NAT gateway para que tenga el acceso a internet.

##Creacion Base de datos
Para la creacion de la base de datos se uso la capa gratuita de aws con mysql se dejo casi toda la configuracion
por defecto, solo cambiando la VPC y el grupo de seguridad.

Se creo una tabla sencilla para almacenar el id de la moneda, nombre, precio y la fecha de carga.

```
CREATE TABLE coin_prices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    id_coin int NOT NULL,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    date_price TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

##Funcion Lambda

Inicialmente se importan las librerias anteriormente mencionadas y adicionalmente json, datetime y OS con el 
objetivo de manejar la respuesta json de la peticion a la api, el formato de la fecha y las variables de entorno respectivamente
```
import urllib.request
import json
import mysql.connector
from datetime import datetime
import os
```

lambda_handler es la funcion que ejecuta lambda,
al principio se define la conexion a la base de datos y la url para hacer la peticion. 
El endpoint a utilizar de la api  es 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
que nos devuelve la informacion mas actualizada de las monedas que filtremos segun los parametro.
En los headers tenemos la api_key de coinmakertcap y en los parametros las monedas de las cuales 
necesitamos la informacion. El parametro slug filtra por nombre las monedas, de igual forma es posible filtrar por el parametro id o symbol.

```
def lambda_handler(event, execution):
    mydb = mysql.connector.connect(
    host=str(os.environ['endpoint_db']),
    user=str(os.environ['user_db']),
    password=str(os.environ['pass_db']),
    database=str(os.environ['db_name'])
    )

    mycursor = mydb.cursor()
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    api_key = os.environ['api_key']
    parameters = {
        'slug':'bitcoin,ethereum'
    }

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key
    }
    url += '?' + urllib.parse.urlencode(parameters)
    req = urllib.request.Request(url, headers=headers)

```
Por ultimo tenemos el bloque try catch que intenta hacer la peticion y posteriormente insertar los 
resultados en la tabla coin_prices. Es posible ver que se tiene un print para ver la data que recibe de la api.
En el ciclo for se obtiene las variables a insertar en la base de datos y se obtienen desglosando el json que retorna la API.
Cabe mencionar que la fecha de coinmarketcap viene en formato iso 8061 y en el codigo se modifica para que sea compatible con el tipo datetime 
de sql.

```
try:
        response = urllib.request.urlopen(req)
        data = json.loads(response.read().decode('utf-8'))
        print(json.dumps(data, indent=4))
        for attr, value in  data['data'].items():     
            id_name = str(attr)
            name = value['name']
            coin_price = value['quote']['USD']['price'] 
            date_iso = value['last_updated'] 
            date_iso = date_iso.replace('T', ' ').replace('Z', '')[:-4]
            iso_datetime = datetime.fromisoformat(date_iso)
            date_price = iso_datetime.strftime('%Y-%m-%d %H:%M:%S')
            sql = f"INSERT INTO coin_prices (id_coin, name, price, date_price) VALUES (%s, %s, %s, %s)"
            val = (id_name, name, coin_price, date_price)
            mycursor.execute(sql, val)
            mydb.commit()
            print(mycursor.rowcount, "record inserted.")
        mycursor.close()
        mydb.close()

    except Exception as e:
        print('Error al hacer la solicitud:', e)

```



