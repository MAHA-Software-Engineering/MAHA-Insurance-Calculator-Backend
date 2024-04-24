import unittest
from unittest.mock import patch, MagicMock
import json
import pymysql
from lambdas.userReviewsPublish import lambda_handler  

class TestLambdaHandler(unittest.TestCase):
    @patch("pymysql.connect")
    def test_lambda_handler_success(self, mock_connect):
        # Set environment variables for database connection
        with patch.dict('os.environ', {
            'DB_HOST': 'localhost', 
            'DB_USER': 'user', 
            'DB_PASSWORD': 'password'
        }):
            # Prepare a mock event with JSON body
            event = {
                "body": json.dumps({
                    "username": "john_doe",
                    "reviewContent": "Great service!",
                    "stars": 5,
                    "datePosted": "2022-04-23"
                })
            }
            context = None  # Context is not used in this lambda, so it can be None

            # Setup the mock connection and cursor
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_connect.return_value = mock_connection
            mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
            
            # Mock the database insertion to simulate success
            mock_cursor.execute.return_value = None

            # Execute the lambda function
            response = lambda_handler(event, context)

            # Check that the response is as expected
            self.assertEqual(response['statusCode'], 200)
            self.assertEqual(json.loads(response['body']), "Review saved successfully")
            mock_cursor.execute.assert_called_once()  
            mock_connection.commit.assert_called_once()  

    @patch("pymysql.connect")
    def test_lambda_handler_failure(self, mock_connect):
        with patch.dict('os.environ', {
            'DB_HOST': 'localhost', 
            'DB_USER': 'user', 
            'DB_PASSWORD': 'password'
        }):
            event = {
                "body": json.dumps({
                    "username": "john_doe",
                    "reviewContent": "Great service!",
                    "stars": 5,
                    "datePosted": "2022-04-23"
                })
            }
            context = None

            # Setup the mock connection and cursor
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_connect.return_value = mock_connection
            mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

            # Simulate a database error
            mock_cursor.execute.side_effect = Exception("Database connection failed")

            # Execute the lambda function
            response = lambda_handler(event, context)

            # Check that the response is as expected for a failure
            self.assertEqual(response['statusCode'], 500)
            self.assertEqual(json.loads(response['body']), "Internal Server Error")
            mock_cursor.execute.assert_called_once()  
            mock_connection.commit.assert_not_called()  

if __name__ == "__main__":
    unittest.main()
