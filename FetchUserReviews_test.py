import unittest
from unittest.mock import patch, MagicMock
import json
import datetime
import pymysql
from lambdas.FetchUserReviews import lambda_handler

class TestLambdaHandler(unittest.TestCase):
    @patch("pymysql.connect")
    def test_lambda_handler_success(self, mock_connect):
        # Set environment variables for the test
        with patch.dict('os.environ', {'DB_HOST': 'localhost', 'DB_USER': 'user', 'DB_PASSWORD': 'password'}):
            # Mock database connection and cursor
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_connect.return_value = mock_connection
            mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
            
            # Setup the expected database return
            date_posted = datetime.date(2022, 4, 23)
            mock_cursor.fetchall.return_value = [
                {'username': 'john_doe', 'reviewContent': 'Great product!', 'datePosted': date_posted, 'stars': 5}
            ]
            
            # Prepare the expected response for the assertion
            expected_result = [
                {'username': 'john_doe', 'reviewContent': 'Great product!', 'datePosted': date_posted.isoformat(), 'stars': 5}
            ]
            
            response = lambda_handler(None, None)
            self.assertEqual(response['statusCode'], 200)
            self.assertEqual(json.loads(response['body']), expected_result)

    @patch("pymysql.connect")
    def test_lambda_handler_failure(self, mock_connect):
        with patch.dict('os.environ', {'DB_HOST': 'localhost', 'DB_USER': 'user', 'DB_PASSWORD': 'password'}):
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_connect.return_value = mock_connection
            mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
            
            # Simulate a database error
            mock_cursor.execute.side_effect = pymysql.MySQLError("Database error")
            
            response = lambda_handler(None, None)
            self.assertEqual(response['statusCode'], 500)
            self.assertEqual(json.loads(response['body']), "Failed to fetch reviews due to database error.")

if __name__ == "__main__":
    unittest.main()
