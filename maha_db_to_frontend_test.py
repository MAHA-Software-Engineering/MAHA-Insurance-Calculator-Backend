import unittest
from unittest.mock import patch, MagicMock
import json

from lambdas.maha_db_to_frontend import lambda_handler


class TestLambdaHandler(unittest.TestCase):
    @patch("pymysql.connect")
    @patch.dict(
        "os.environ",
        {
            "host": "test_host",
            "user": "test_user",
            "password": "test_password",
            "db": "test_db",
        },
    )
    def test_lambda_handler_successful(self, mock_connect):
        # Set up mock connection and cursor
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        # Mocking the fetchall to return sample data
        mock_cursor.fetchall.side_effect = [
            [("Vehicle1", 5, 4, 4, 3, "Yes", "Yes", "No", 10, 2, 1)],  # Ratings data
            [("Brakes", "Brake failure", "Accidents", "Repair brakes")],  # Recalls data
        ]

        # Define a sample event and context
        event = {
            "queryStringParameters": {"year": "2020", "make": "Honda", "model": "Civic"}
        }
        context = {}

        # Call the lambda handler
        response = lambda_handler(event, context)

        # Check that the status code is 200
        self.assertEqual(
            response["statusCode"],
            200,
            f"Expected status code 200, but got {response['statusCode']}",
        )

        # Load the body to check the response content
        body = json.loads(response["body"])
        self.assertTrue(
            "ratings" in body, f"Expected 'ratings' in response body, but got {body}"
        )
        self.assertTrue(
            "recalls" in body, f"Expected 'recalls' in response body, but got {body}"
        )
        self.assertEqual(
            len(body["ratings"]),
            1,
            f"Expected 1 rating, but got {len(body['ratings'])}",
        )
        self.assertEqual(
            len(body["recalls"]),
            1,
            f"Expected 1 recall, but got {len(body['recalls'])}",
        )

    @patch("pymysql.connect")
    @patch.dict(
        "os.environ",
        {
            "host": "test_host",
            "user": "test_user",
            "password": "test_password",
            "db": "test_db",
        },
    )
    def test_lambda_handler_no_data_found(self, mock_connect):
        # Set up mock connection and cursor
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        # Mocking the fetchall to return empty data
        mock_cursor.fetchall.return_value = []

        # Define a sample event and context
        event = {
            "queryStringParameters": {
                "year": "2025",
                "make": "Tesla",
                "model": "Model X",
            }
        }
        context = {}

        # Call the lambda handler
        response = lambda_handler(event, context)

        # Check that the status code is 404
        self.assertEqual(
            response["statusCode"],
            404,
            f"Expected status code 404, but got {response['statusCode']}",
        )

        # Load the body to check the response content
        body = json.loads(response["body"])
        self.assertEqual(
            body,
            {"message": "No information on this vehicle"},
            f"Expected message 'No information on this vehicle', but got {body}",
        )


if __name__ == "__main__":
    unittest.main()
