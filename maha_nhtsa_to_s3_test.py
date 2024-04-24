import unittest
from unittest.mock import patch, MagicMock
import json
import os

class TestLambdaHandler(unittest.TestCase):
    @patch('boto3.client')  
    @patch('requests.get')
    def test_lambda_handler(self, mock_requests_get, mock_boto3_client):
        os.environ['s3_bucket'] = 'test-bucket'

        from lambdas.maha_nhtsa_to_s3 import lambda_handler

        mock_s3_client = mock_boto3_client.return_value
        mock_s3_client.put_object = MagicMock()

        default_mock_response = MagicMock(status_code=200, json=lambda: {"Results": [{'VehicleId': 12345, 'OverallRating': '5'}]})
        mock_requests_get.return_value = default_mock_response

        response = lambda_handler(None, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), 'Data successfully uploaded to S3')

        mock_s3_client.put_object.assert_called()

if __name__ == '__main__':
    unittest.main()
