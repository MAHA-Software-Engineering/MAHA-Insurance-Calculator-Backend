import unittest
from unittest.mock import patch, MagicMock
import json
from lambdas.maha_s3_to_mysql import lambda_handler


class TestLambdaHandler(unittest.TestCase):
    @patch("lambdas.maha_s3_to_mysql.pymysql.connect")
    @patch("lambdas.maha_s3_to_mysql.boto3.client")
    def test_lambda_handler(self, mock_boto3_client, mock_pymysql_connect):
        with patch.dict(
            "os.environ",
            {
                "host": "localhost",
                "user": "user",
                "password": "password",
                "db": "db",
                "AWS_ACCESS_KEY_ID": "test",
                "AWS_SECRET_ACCESS_KEY": "test",
            },
        ):
            event = {
                "Records": [
                    {
                        "s3": {
                            "bucket": {"name": "test-bucket"},
                            "object": {"key": "recall_info.json"},
                        }
                    }
                ]
            }

            s3_object = {"Body": MagicMock()}
            s3_object["Body"].read.return_value = json.dumps(
                [
                    {
                        "Manufacturer": "Test Manufacturer",
                        "NHTSACampaignNumber": 12345,
                        "Component": "Test Component",
                        "Summary": "Test Summary",
                        "Consequence": "Test Consequence",
                        "Remedy": "Test Remedy",
                        "ModelYear": 2022,
                        "Make": "Test Make",
                        "Model": "Test Model",
                    }
                ]
            ).encode("utf-8")

            mock_s3_client = mock_boto3_client.return_value
            mock_s3_client.get_object.return_value = s3_object
            mock_db_connection = mock_pymysql_connect.return_value
            mock_cursor = mock_db_connection.cursor.return_value.__enter__.return_value

            response = lambda_handler(event, None)
            self.assertEqual(
                response,
                {"statusCode": 200, "body": json.dumps("Data processed successfully")},
            )

            mock_boto3_client.assert_called_once_with("s3")
            mock_s3_client.get_object.assert_called_once_with(
                Bucket="test-bucket", Key="recall_info.json"
            )
            mock_pymysql_connect.assert_called_once_with(
                host="localhost", user="user", password="password", db="db", port=3306
            )


if __name__ == "__main__":
    unittest.main()
