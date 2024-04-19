import unittest
from unittest.mock import patch, MagicMock
from get_coins import get_coin_price, insert_db
import json

class TestLambdaHandler(unittest.TestCase):

    @patch('get_coins.urllib.request.urlopen')
    def test_get_coin_price(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            'data': {
                'bitcoin': {'name': 'Bitcoin', 'quote': {'USD': {'price': 50000}}}
            }
        }).encode('utf-8')
        mock_urlopen.return_value = mock_response

        data = get_coin_price('fake_api_key')
        self.assertIsNotNone(data)
        self.assertIn('bitcoin', data)

    @patch('get_coins.mysql.connector.connect')
    def test_insert_db(self, mock_connect):
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_db.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_db

        data = {
            'bitcoin': {'name': 'Bitcoin', 'quote': {'USD': {'price': 50000}}, 'last_updated': '2022-01-01T00:00:00.000Z'}
        }
        insert_db(mock_cursor, mock_db, data)

        mock_cursor.execute.assert_called_once()
        mock_db.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()
