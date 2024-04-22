import json
import pymysql
import os
import datetime


def lambda_handler(event, context):
    # Connect to MySQL RDS instance using PyMySQL
    connection = pymysql.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database="NHTSA_Data",
        cursorclass=pymysql.cursors.DictCursor,
    )

    try:
        with connection.cursor() as cursor:
            sql = "SELECT `username`, `reviewContent`, `datePosted`, `stars` FROM `userReviews`"
            cursor.execute(sql)
            result = cursor.fetchall()

            for review in result:
                if isinstance(review["datePosted"], datetime.date):
                    review["datePosted"] = review["datePosted"].isoformat()

        return {
            "statusCode": 200,
            "body": json.dumps(result),  # Removed cls=CustomJSONEncoder
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",  # Ensure CORS compatibility
            },
        }

    except pymysql.MySQLError as e:
        print("Got error {!r}, errno is {}".format(e, e.args[0]))
        result = "Failed to fetch reviews due to database error."
        status_code = 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        result = "An unexpected error occurred."
        status_code = 500
    finally:
        if connection:
            connection.close()

    # In case of exception, return the error response
    return {
        "statusCode": status_code,
        "body": json.dumps(result),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
    }
