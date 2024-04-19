import urllib.request
import json
import mysql.connector
from datetime import datetime
import os
  




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


